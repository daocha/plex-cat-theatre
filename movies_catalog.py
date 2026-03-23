#!/usr/bin/env python3
"""Catalog and media processing utilities for the movies server."""

from __future__ import annotations

import logging
import shutil
import threading
import time
from pathlib import Path
from typing import Dict, List

from movies_catalog_index import load_catalog_index, save_catalog_index
from movies_catalog_scan import run_catalog_scan
from movies_catalog_workers import (
    run_metadata_worker,
    run_preview_worker,
    run_thumb_worker,
    run_transcode_worker,
)
from movies_catalog_media import (
    extract_chi_from_mkv_to_vtt,
    extract_subtitle,
    fmt_size,
    load_html_template,
    pick_best_subtitle_file,
    probe_aspect,
    probe_audio_codecs,
    probe_duration,
    resolve_sidecar_subtitle,
    srt_to_vtt,
    vid_id,
)

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".webm",
    ".mpg",
    ".mpeg",
    ".flv",
    ".ogg",
    ".wmv",
    ".m4v",
}
SOURCE_EXTENSIONS = {".ts", ".mkv"}
DIRECT_AUDIO_EXTENSIONS = {".mp4", ".m4v", ".mov", ".webm"}
FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")
INDEX_STATE_PATH = Path(__file__).with_name("movies_catalog_index.json")
INDEX_PROGRESS_PATH = Path(__file__).with_name("movies_catalog_tmp.json")
PREVIEW_FRAME_COUNT = 12
PREVIEW_WIDTH = 320
FFPROBE_TIMEOUT = 12
FFMPEG_TIMEOUT = 45
class Catalog:
    def __init__(
        self,
        roots: List[Path],
        thumbs_dir: Path,
        private_folders: List[str] | None = None,
        private_passcode: str = "",
        transcode_enabled: bool = True,
        verify_passcode_fn=None,
        generate_thumbs: bool = True,
        scan_checkpoint_cb=None,
    ):
        self.roots = roots
        self.thumbs_dir = thumbs_dir
        self.transcode_enabled = bool(transcode_enabled)
        self.generate_thumbs = bool(generate_thumbs)
        self.private_folders = [
            str(x).strip().strip("/") for x in (private_folders or []) if str(x).strip()
        ]
        self.private_passcode = str(private_passcode or "")
        self.verify_passcode = verify_passcode_fn or (lambda input_passcode, stored: False)
        self.scan_checkpoint_cb = scan_checkpoint_cb
        self.thumbs_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._videos: List[dict] = []
        self._public_videos: List[dict] = []
        self.video_map: Dict[str, Path] = {}
        self.thumb_map: Dict[str, Path] = {}
        self.preview_dir_map: Dict[str, Path] = {}
        self.subtitle_map: Dict[str, Path] = {}
        self.private_video_ids: set[str] = set()
        self._public_private_video_ids: set[str] = set()
        self._aspect_cache: Dict[str, float] = {}
        self._audio_codec_cache: Dict[str, List[str]] = {}
        self._file_sig_cache: Dict[str, tuple[float, int]] = {}
        self._file_meta_cache: Dict[str, dict] = {}
        self._thumb_queue: List[str] = []
        self._thumb_total = 0
        self._thumb_done = 0
        self._preview_queue: List[str] = []
        self._metadata_queue: List[str] = []
        self._metadata_inflight: set[str] = set()
        self._transcode_queue: List[Path] = []
        self._transcode_inflight: set[str] = set()
        self._stop = threading.Event()
        self.available = True
        self.is_scanning = False
        self.scan_progress: dict = {}
        self.last_error = None
        self.last_scan_at = None
        self._last_index_persist_at = 0.0

        if self.generate_thumbs:
            threading.Thread(target=self._thumb_worker, daemon=True).start()
        threading.Thread(target=self._preview_worker, daemon=True).start()
        threading.Thread(target=self._metadata_worker, daemon=True).start()
        if self.transcode_enabled:
            threading.Thread(target=self._transcode_worker, daemon=True).start()

        self._load_index(INDEX_STATE_PATH)

    def _update_scan_progress(self, **fields):
        with self._lock:
            if not self.is_scanning:
                return
            self.scan_progress.update(fields)
            self.scan_progress["updated_at"] = time.time()

    def _queue_metadata_refresh(self, video_id: str):
        if not video_id:
            return
        with self._lock:
            if video_id in self._metadata_inflight or video_id in self._metadata_queue:
                return
            self._metadata_queue.append(video_id)

    def pop_metadata_job(self):
        with self._lock:
            if not self._metadata_queue:
                return None
            video_id = self._metadata_queue.pop(0)
            self._metadata_inflight.add(video_id)
            return video_id

    def _commit_scan_snapshot(
        self,
        *,
        videos: List[dict],
        vmap: Dict[str, Path],
        tmap: Dict[str, Path],
        pdir_map: Dict[str, Path],
        smap: Dict[str, Path],
        thumb_queue: List[str],
        preview_queue: List[str],
        transcode_jobs: List[Path],
        scanning: bool,
        persist_progress: bool = False,
    ):
        videos_sorted = sorted(videos, key=lambda item: item.get("mtime", 0), reverse=True)
        private_ids_local = {
            item["id"] for item in videos_sorted if self._is_private_video(item)
        }
        with self._lock:
            latest_video_map = dict(self.video_map)
            latest_file_meta = dict(self._file_meta_cache)
            latest_subtitle_map = dict(self.subtitle_map)
        payload = []
        for video in videos_sorted:
            item = dict(video)
            video_id = str(item.get("id", "")).strip()
            video_path = latest_video_map.get(video_id) or vmap.get(video_id)
            if video_path:
                file_meta = latest_file_meta.get(str(video_path), {})
                latest_aspect = float(file_meta.get("ar", 0) or 0)
                if latest_aspect > 0:
                    item["ar"] = latest_aspect
                item["audio_codecs"] = list(file_meta.get("audio_codecs", []))
            subtitle_path = latest_subtitle_map.get(video_id) or smap.get(video_id)
            item["subtitle_url"] = (
                f"/subtitle/{video_id}.vtt"
                if subtitle_path and Path(subtitle_path).exists()
                else ""
            )
            item.pop("mtime", None)
            payload.append(item)

        enqueue_jobs: list[Path] = []
        inflight_snapshot = set(self._transcode_inflight)
        for job in transcode_jobs:
            key = str(job.resolve())
            if key in inflight_snapshot:
                continue
            mp4 = job.with_suffix(".mp4")
            try:
                if mp4.exists() and mp4.stat().st_mtime >= job.stat().st_mtime:
                    continue
            except OSError:
                pass
            inflight_snapshot.add(key)
            enqueue_jobs.append(job)

        with self._lock:
            self._videos = payload
            if not scanning:
                self._public_videos = list(payload)
                self._public_private_video_ids = set(private_ids_local)
            self.video_map = dict(vmap)
            self.thumb_map = dict(tmap)
            self.preview_dir_map = dict(pdir_map)
            self.subtitle_map = dict(smap)
            self.private_video_ids = private_ids_local
            self._thumb_queue = list(thumb_queue)
            self._thumb_total = len(thumb_queue)
            self._thumb_done = 0
            self._preview_queue = list(preview_queue)
            self.available = True
            self.is_scanning = scanning
            if not scanning:
                self.scan_progress = {}
            self.last_error = None
            self.last_scan_at = time.time()
            for job in enqueue_jobs:
                self._transcode_inflight.add(str(job.resolve()))
                self._transcode_queue.append(job)

        now_ts = time.time()
        if scanning and persist_progress:
            self._save_index(INDEX_PROGRESS_PATH)

        if (not scanning) or (now_ts - self._last_index_persist_at >= 15):
            target = INDEX_STATE_PATH if not scanning else INDEX_PROGRESS_PATH
            self._save_index(target)
            self._last_index_persist_at = now_ts

        if not scanning:
            try:
                if INDEX_PROGRESS_PATH.exists():
                    INDEX_PROGRESS_PATH.unlink()
            except Exception:
                pass

        if self.scan_checkpoint_cb:
            try:
                self.scan_checkpoint_cb(scanning=scanning)
            except Exception as exc:
                logging.debug("Scan checkpoint callback failed: %s", exc)

    def _wait_for_metadata_idle(self, timeout: float = 120.0):
        deadline = time.time() + max(0.0, timeout)
        last_log_at = 0.0
        while time.time() < deadline:
            with self._lock:
                pending = len(self._metadata_queue)
                inflight = len(self._metadata_inflight)
            if pending == 0 and inflight == 0:
                return True
            now_ts = time.time()
            if now_ts - last_log_at >= 2.0:
                logging.info(
                    "Waiting for metadata worker before final snapshot: pending=%d inflight=%d",
                    pending,
                    inflight,
                )
                last_log_at = now_ts
            time.sleep(0.1)
        with self._lock:
            pending = len(self._metadata_queue)
            inflight = len(self._metadata_inflight)
        logging.warning(
            "Metadata worker did not drain before final snapshot timeout: pending=%d inflight=%d timeout=%.1fs",
            pending,
            inflight,
            timeout,
        )
        return False

    def _remove_root_from_accumulator(
        self,
        *,
        root_label: str,
        videos: List[dict],
        vmap: Dict[str, Path],
        tmap: Dict[str, Path],
        pdir_map: Dict[str, Path],
        smap: Dict[str, Path],
        thumb_queue: List[str],
        preview_queue: List[str],
    ):
        prefix = f"{root_label}/"
        removed_ids = {
            video.get("id")
            for video in videos
            if str(video.get("relative_path", "")).startswith(prefix)
        }
        videos[:] = [
            video
            for video in videos
            if not str(video.get("relative_path", "")).startswith(prefix)
        ]
        valid_ids = {video.get("id") for video in videos}
        for mapping in (vmap, tmap, pdir_map, smap):
            for key in list(mapping.keys()):
                if key not in valid_ids:
                    mapping.pop(key, None)
        thumb_queue[:] = [item for item in thumb_queue if item in valid_ids]
        preview_queue[:] = [item for item in preview_queue if item in valid_ids]
        return removed_ids

    def _cleanup_removed_ids(
        self,
        removed_ids: set[str],
        old_tmap: Dict[str, Path],
        old_pdir_map: Dict[str, Path],
        old_vmap: Dict[str, Path],
    ):
        cleaned_thumbs = 0
        cleaned_previews = 0
        for removed_id in removed_ids:
            thumb_path = old_tmap.get(removed_id)
            if thumb_path:
                try:
                    thumb_path.unlink(missing_ok=True)
                    cleaned_thumbs += 1
                except Exception:
                    pass

            preview_dir = old_pdir_map.get(removed_id)
            if preview_dir and preview_dir.exists():
                try:
                    shutil.rmtree(preview_dir, ignore_errors=True)
                    cleaned_previews += 1
                except Exception:
                    pass

            old_video_path = old_vmap.get(removed_id)
            if old_video_path:
                old_key = str(old_video_path)
                self._file_sig_cache.pop(old_key, None)
                self._file_meta_cache.pop(old_key, None)
                self._aspect_cache.pop(old_key, None)
        if removed_ids:
            logging.info(
                "Scan cleanup: removed=%d thumbnails=%d preview_dirs=%d",
                len(removed_ids),
                cleaned_thumbs,
                cleaned_previews,
            )

    @staticmethod
    def _queue_missing_job(queue: List[str], video_id: str):
        if video_id not in queue:
            queue.append(video_id)

    @staticmethod
    def _preview_frames_ready_fast(preview_dir: Path) -> bool:
        return (
            preview_dir.exists()
            and (preview_dir / "01.jpg").exists()
            and (preview_dir / f"{PREVIEW_FRAME_COUNT:02d}.jpg").exists()
        )

    @staticmethod
    def _preview_frames_ready_full(preview_dir: Path, media_mtime: float) -> bool:
        try:
            if not preview_dir.exists():
                return False
            frames = [
                preview_dir / f"{index:02d}.jpg"
                for index in range(1, PREVIEW_FRAME_COUNT + 1)
            ]
            if not all(frame.exists() for frame in frames):
                return False
            newest = max(frame.stat().st_mtime for frame in frames)
            return newest >= media_mtime
        except OSError:
            return False

    def scan(self):
        return run_catalog_scan(
            self,
            video_extensions=VIDEO_EXTENSIONS,
            source_extensions=SOURCE_EXTENSIONS,
            preview_frame_count=PREVIEW_FRAME_COUNT,
        )

    def invalidate_scan_state(self):
        with self._lock:
            self._file_sig_cache.clear()
            self._file_meta_cache.clear()
            self._aspect_cache.clear()
            self._audio_codec_cache.clear()
            self._thumb_queue = []
            self._preview_queue = []
            self._metadata_queue = []
            self._metadata_inflight.clear()
            self._thumb_total = 0
            self._thumb_done = 0
        logging.info("Catalog scan state invalidated: next scan will run in full rebuild mode")

    def _is_private_video(self, video: dict) -> bool:
        if not self.private_folders:
            return False
        rel = str(video.get("relative_path", "")).replace("\\", "/").lower()
        for private_folder in self.private_folders:
            normalized = str(private_folder).replace("\\", "/").lower().rstrip("/")
            if rel.startswith(normalized + "/") or rel == normalized:
                return True
        return False

    def list(self, include_private: bool = False, passcode: str = "", allow_approved: bool = False):
        with self._lock:
            videos_snapshot = list(self._public_videos or self._videos)
        if include_private and (
            allow_approved
            or (
                self.private_folders
                and self.verify_passcode(passcode, self.private_passcode)
            )
        ):
            return videos_snapshot
        return [video for video in videos_snapshot if not self._is_private_video(video)]

    def is_private_id(self, video_id: str) -> bool:
        with self._lock:
            ids = self._public_private_video_ids or self.private_video_ids
            return video_id in ids

    def status(self):
        with self._lock:
            thumb_pending = len(self._thumb_queue)
            preview_pending = len(self._preview_queue)
            metadata_pending = len(self._metadata_queue) + len(self._metadata_inflight)
            scan_progress = dict(self.scan_progress or {})
            background_work = {
                "thumbs_pending": thumb_pending,
                "thumbs_total": int(self._thumb_total or 0),
                "thumbs_done": int(self._thumb_done or 0),
                "previews_pending": preview_pending,
                "metadata_pending": metadata_pending,
                "metadata_inflight": len(self._metadata_inflight),
            }
            if scan_progress:
                scan_progress.setdefault("thumbs_pending", thumb_pending)
                scan_progress.setdefault("previews_pending", preview_pending)
                scan_progress.setdefault("metadata_pending", metadata_pending)
            return {
                "available": self.available,
                "is_scanning": self.is_scanning,
                "scan_progress": scan_progress,
                "background_work": background_work,
                "last_error": self.last_error,
                "last_scan_at": self.last_scan_at,
                "video_count": len(self._public_videos or self._videos),
                "private_enabled": bool(self.private_folders and self.private_passcode),
                "transcode_enabled": self.transcode_enabled,
            }

    def _load_index(self, path: Path):
        try:
            loaded = load_catalog_index(path, self._is_private_video)
            if not loaded:
                return
            with self._lock:
                self._videos = loaded["videos"]
                self._public_videos = list(loaded["videos"])
                self.video_map = loaded["video_map"]
                self.thumb_map = loaded["thumb_map"]
                self.preview_dir_map = loaded["preview_dir_map"]
                self.subtitle_map = loaded["subtitle_map"]
                self.private_video_ids = loaded["private_ids"]
                self._public_private_video_ids = set(loaded["private_ids"])
                self._file_sig_cache = loaded["file_sig_cache"]
                self._file_meta_cache = loaded["file_meta_cache"]
                self._audio_codec_cache = loaded["audio_codec_cache"]
                self.available = True
                self.last_error = None
                self.last_scan_at = loaded["last_scan_at"]
            logging.info("Loaded catalog index: %d videos", len(loaded["videos"]))
        except Exception as exc:
            logging.warning("Failed to load catalog index: %s", exc)

    def _save_index(self, path: Path):
        try:
            with self._lock:
                videos_snapshot = list(self._videos)
                video_map_snapshot = dict(self.video_map)
                thumb_map_snapshot = dict(self.thumb_map)
                preview_dir_snapshot = dict(self.preview_dir_map)
                subtitle_map_snapshot = dict(self.subtitle_map)
                file_sig_snapshot = dict(self._file_sig_cache)
                file_meta_snapshot = dict(self._file_meta_cache)
                last_scan_at = self.last_scan_at

            save_catalog_index(
                path,
                videos_snapshot=videos_snapshot,
                video_map_snapshot=video_map_snapshot,
                thumb_map_snapshot=thumb_map_snapshot,
                preview_dir_snapshot=preview_dir_snapshot,
                subtitle_map_snapshot=subtitle_map_snapshot,
                file_sig_snapshot=file_sig_snapshot,
                file_meta_snapshot=file_meta_snapshot,
                last_scan_at=last_scan_at,
            )
        except Exception as exc:
            logging.warning("Failed to save catalog index: %s", exc)

    def pop_thumb_job(self):
        with self._lock:
            return self._thumb_queue.pop(0) if self._thumb_queue else None

    def pop_preview_job(self):
        with self._lock:
            return self._preview_queue.pop(0) if self._preview_queue else None

    def update_thumb_url(self, video_id: str):
        with self._lock:
            for video in self._videos:
                if video["id"] == video_id:
                    video["thumb_url"] = f"/thumbs/{video_id}.jpg"
                    break

    def update_preview_urls(self, video_id: str):
        with self._lock:
            for video in self._videos:
                if video["id"] == video_id:
                    video["preview_urls"] = [
                        f"/thumbs/prev/{video_id}/{index:02d}.jpg"
                        for index in range(1, PREVIEW_FRAME_COUNT + 1)
                    ]
                    break

    def _update_video_metadata(
        self,
        video_id: str,
        *,
        aspect: float | None = None,
        subtitle_path: Path | None = None,
        audio_codecs: List[str] | None = None,
    ):
        with self._lock:
            video_path = self.video_map.get(video_id)
            if not video_path:
                return
            file_key = str(video_path)
            meta = dict(self._file_meta_cache.get(file_key, {}))
            changed = False
            if aspect and aspect > 0:
                normalized_aspect = float(aspect)
                if float(meta.get("ar", 0) or 0) != normalized_aspect:
                    changed = True
                meta["ar"] = normalized_aspect
            if subtitle_path and subtitle_path.exists():
                subtitle_value = str(subtitle_path)
                if meta.get("subtitle_path", "") != subtitle_value or not bool(
                    meta.get("subtitle_ready", False)
                ):
                    changed = True
                meta["subtitle_path"] = subtitle_value
                meta["subtitle_ready"] = True
                self.subtitle_map[video_id] = subtitle_path
            else:
                if meta.get("subtitle_path", "") or bool(meta.get("subtitle_ready", False)):
                    changed = True
                meta["subtitle_path"] = ""
                meta["subtitle_ready"] = False
                self.subtitle_map.pop(video_id, None)
            if audio_codecs is not None:
                normalized_audio_codecs = list(audio_codecs)
                if list(meta.get("audio_codecs", [])) != normalized_audio_codecs:
                    changed = True
                meta["audio_codecs"] = normalized_audio_codecs
                self._audio_codec_cache[file_key] = normalized_audio_codecs
            self._file_meta_cache[file_key] = meta
            subtitle_url = f"/subtitle/{video_id}.vtt" if subtitle_path and subtitle_path.exists() else ""
            for collection in (self._videos, self._public_videos):
                for video in collection:
                    if video.get("id") != video_id:
                        continue
                    if aspect and aspect > 0:
                        video["ar"] = float(aspect)
                    video["subtitle_url"] = subtitle_url
                    if audio_codecs is not None:
                        video["audio_codecs"] = list(audio_codecs)
                    break
            scanning = self.is_scanning
        if (not scanning) and changed:
            self._save_index(INDEX_STATE_PATH)
            self._last_index_persist_at = time.time()

    def _probe_video_metadata(self, video_id: str):
        with self._lock:
            video_path = self.video_map.get(video_id)
        if not video_path or not video_path.exists():
            return
        self._update_scan_progress(
            current_path=str(video_path),
            current_stage="metadata",
        )
        aspect = self._probe_aspect(video_path) or 1.6
        self._update_scan_progress(
            current_path=str(video_path),
            current_stage="subtitle",
        )
        subtitle_path = self._resolve_sidecar_subtitle(video_path)
        if video_path.suffix.lower() in VIDEO_EXTENSIONS or video_path.suffix.lower() in SOURCE_EXTENSIONS:
            self._update_scan_progress(
                current_path=str(video_path),
                current_stage="audio",
            )
            audio_codecs = self._probe_audio_codecs(video_path)
        else:
            audio_codecs = []
        self._update_video_metadata(
            video_id,
            aspect=aspect,
            subtitle_path=subtitle_path,
            audio_codecs=audio_codecs,
        )

    def _metadata_worker(self):
        run_metadata_worker(self)

    def _thumb_worker(self):
        run_thumb_worker(self, ffmpeg_bin=FFMPEG)

    def _probe_aspect(self, video_path: Path):
        return probe_aspect(video_path, FFPROBE, self._aspect_cache, FFPROBE_TIMEOUT)

    def _probe_audio_codecs(self, video_path: Path) -> List[str]:
        return probe_audio_codecs(
            video_path,
            FFPROBE,
            self._audio_codec_cache,
            FFPROBE_TIMEOUT,
        )

    def _probe_duration(self, video_path: Path):
        return probe_duration(video_path, FFPROBE, FFPROBE_TIMEOUT)

    def _pick_best_subtitle_file(self, files: List[Path]) -> Path | None:
        return pick_best_subtitle_file(files)

    def _srt_to_vtt(self, srt_path: Path, vtt_path: Path):
        srt_to_vtt(srt_path, vtt_path)

    def _extract_chi_from_mkv_to_vtt(self, mkv_path: Path, target_vtt: Path) -> Path | None:
        return extract_chi_from_mkv_to_vtt(
            mkv_path,
            target_vtt,
            FFPROBE,
            FFMPEG,
            FFPROBE_TIMEOUT,
            FFMPEG_TIMEOUT,
        )

    def _resolve_sidecar_subtitle(self, video_path: Path):
        return resolve_sidecar_subtitle(
            video_path,
            FFPROBE,
            FFMPEG,
            FFPROBE_TIMEOUT,
            FFMPEG_TIMEOUT,
        )

    def _extract_subtitle(
        self,
        src_path: Path,
        out_mp4: Path,
        target_lang: str = "chi",
        target_title: str = "Traditional",
    ):
        extract_subtitle(
            src_path,
            out_mp4,
            FFPROBE,
            FFMPEG,
            target_lang=target_lang,
            target_title=target_title,
        )

    def _preview_worker(self):
        run_preview_worker(
            self,
            ffmpeg_bin=FFMPEG,
            preview_frame_count=PREVIEW_FRAME_COUNT,
            preview_width=PREVIEW_WIDTH,
        )

    def pop_transcode_job(self):
        with self._lock:
            return self._transcode_queue.pop(0) if self._transcode_queue else None

    def _transcode_worker(self):
        run_transcode_worker(self, ffmpeg_bin=FFMPEG)
