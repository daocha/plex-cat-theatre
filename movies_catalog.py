#!/usr/bin/env python3
"""Catalog and media processing utilities for the movies server."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List

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


def vid_id(path: Path) -> str:
    return hashlib.sha1(str(path.resolve()).encode("utf-8")).hexdigest()[:16]


def fmt_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    scaled = float(size)
    for unit in units:
        if scaled < 1024 or unit == units[-1]:
            return f"{scaled:.1f}{unit}".rstrip("0").rstrip(".")
        scaled /= 1024
    return f"{size}B"


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

    def scan(self):
        with self._lock:
            self.is_scanning = True
            self.scan_progress = {
                "phase": "initializing",
                "started_at": time.time(),
                "updated_at": time.time(),
                "roots_total": len(self.roots),
                "root_index": 0,
                "root_name": "",
                "root_path": "",
                "processed_entries": 0,
                "videos_found": 0,
                "new_count": 0,
                "changed_count": 0,
                "unchanged_count": 0,
                "removed_count": 0,
                "thumbs_pending": 0,
                "previews_pending": 0,
                "current_path": "",
                "current_stage": "",
                "metadata_pending": 0,
            }
            videos = [dict(v, mtime=0) for v in self._videos]
            vmap: Dict[str, Path] = dict(self.video_map)
            tmap: Dict[str, Path] = dict(self.thumb_map)
            pdir_map: Dict[str, Path] = dict(self.preview_dir_map)
            smap: Dict[str, Path] = dict(self.subtitle_map)
            thumb_queue: List[str] = list(self._thumb_queue)
            preview_queue: List[str] = list(self._preview_queue)
            old_items_by_id: Dict[str, dict] = {
                str(video.get("id", "")): dict(video) for video in self._videos
            }
            old_items_by_path: Dict[str, dict] = {
                str(path): old_items_by_id.get(str(video_id), {})
                for video_id, path in self.video_map.items()
                if str(video_id) in old_items_by_id
            }

        existing_roots = [root for root in self.roots if root.exists()]
        if not existing_roots:
            with self._lock:
                self.available = True
                self.last_error = f"No roots found: {', '.join(str(root) for root in self.roots)}"
                self.last_scan_at = time.time()
                self.is_scanning = False
                self.scan_progress = {}
            logging.warning(self.last_error)
            return False

        transcode_jobs: List[Path] = []
        scan_started_at = time.time()
        logging.info(
            "Full scan start: roots=%d thumbs=%s previews=%s transcode=%s",
            len(existing_roots),
            "enabled" if self.generate_thumbs else "disabled",
            "enabled",
            "enabled" if self.transcode_enabled else "disabled",
        )

        def commit_snapshot(scanning: bool, persist_progress: bool = False):
            videos_sorted = sorted(videos, key=lambda item: item.get("mtime", 0), reverse=True)
            private_ids_local = {
                item["id"] for item in videos_sorted if self._is_private_video(item)
            }
            payload = []
            for video in videos_sorted:
                item = dict(video)
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

        def remove_root_from_accumulator(root_label: str):
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

        def cleanup_removed_ids(removed_ids: set[str], old_tmap: Dict[str, Path], old_pdir_map: Dict[str, Path], old_vmap: Dict[str, Path]):
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

        def queue_missing_job(queue: List[str], video_id: str):
            if video_id not in queue:
                queue.append(video_id)

        def preview_frames_ready_fast(preview_dir: Path) -> bool:
            return (
                preview_dir.exists()
                and (preview_dir / "01.jpg").exists()
                and (preview_dir / f"{PREVIEW_FRAME_COUNT:02d}.jpg").exists()
            )

        def preview_frames_ready_full(preview_dir: Path, media_mtime: float) -> bool:
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

        for root_index, root in enumerate(existing_roots, start=1):
            root_label = root.name
            processed_entries = 0
            root_video_count = 0
            unchanged_count = 0
            changed_count = 0
            new_count = 0
            missing_thumb_count = 0
            missing_preview_count = 0
            root_started_at = time.time()
            logging.info("Scan start [%s]: root=%s", root_label, root)
            with self._lock:
                self.scan_progress.update(
                    {
                        "phase": "scanning",
                        "updated_at": time.time(),
                        "root_index": root_index,
                        "root_name": root_label,
                        "root_path": str(root),
                        "processed_entries": 0,
                        "videos_found": 0,
                        "new_count": 0,
                        "changed_count": 0,
                        "unchanged_count": 0,
                        "removed_count": 0,
                        "thumbs_pending": 0,
                        "previews_pending": 0,
                        "current_path": "",
                        "current_stage": "",
                        "metadata_pending": len(self._metadata_queue),
                    }
                )

            old_root_ids = {
                video.get("id")
                for video in videos
                if str(video.get("relative_path", "")).startswith(f"{root_label}/")
            }
            old_root_tmap = {video_id: tmap.get(video_id) for video_id in old_root_ids if video_id}
            old_root_pdir_map = {video_id: pdir_map.get(video_id) for video_id in old_root_ids if video_id}
            old_root_vmap = {video_id: vmap.get(video_id) for video_id in old_root_ids if video_id}
            remove_root_from_accumulator(root_label)
            seen_ids: set[str] = set()
            last_progress_log_at = 0.0

            for dirpath, _, filenames in os.walk(root):
                for filename in filenames:
                    processed_entries += 1
                    path = Path(dirpath) / filename
                    suffix = path.suffix.lower()
                    self._update_scan_progress(
                        phase="scanning",
                        root_index=root_index,
                        root_name=root_label,
                        root_path=str(root),
                        processed_entries=processed_entries,
                        videos_found=root_video_count,
                        new_count=new_count,
                        changed_count=changed_count,
                        unchanged_count=unchanged_count,
                        thumbs_pending=missing_thumb_count,
                        previews_pending=missing_preview_count,
                        metadata_pending=len(self._metadata_queue),
                        current_path=str(path),
                        current_stage="discovering",
                    )
                    if suffix in SOURCE_EXTENSIONS:
                        if self.transcode_enabled:
                            transcode_jobs.append(path)
                            if len(transcode_jobs) <= 5 or len(transcode_jobs) % 50 == 0:
                                logging.info(
                                    "Scan transcode candidate [%s]: queued=%d file=%s",
                                    root_label,
                                    len(transcode_jobs),
                                    path,
                                )
                            continue
                    if suffix not in VIDEO_EXTENSIONS and not (
                        suffix in SOURCE_EXTENSIONS and not self.transcode_enabled
                    ):
                        continue

                    stat = path.stat()
                    video_id = vid_id(path)
                    seen_ids.add(video_id)
                    rel_under_root = os.path.relpath(path, root)
                    rel = f"{root_label}/{rel_under_root}"
                    parent = Path(rel_under_root).parent
                    folder = f"{root_label}/" + (
                        str(parent) if parent != Path(".") else "(root)"
                    )
                    thumb = self.thumbs_dir / f"{video_id}.jpg"
                    preview_dir = self.thumbs_dir / "previews" / video_id

                    file_key = str(path)
                    file_sig = (float(stat.st_mtime), int(stat.st_size))
                    cached_sig = self._file_sig_cache.get(file_key)
                    cached_meta = self._file_meta_cache.get(file_key, {}) if cached_sig == file_sig else {}
                    if cached_sig is None:
                        new_count += 1
                    elif cached_sig == file_sig:
                        unchanged_count += 1
                    else:
                        changed_count += 1

                    thumb_ready_cached = bool(cached_meta.get("thumb_ready", False))
                    preview_ready_cached = bool(cached_meta.get("preview_ready", False))
                    subtitle_ready_cached = bool(cached_meta.get("subtitle_ready", False))

                    has_thumb = False
                    try:
                        if thumb_ready_cached:
                            has_thumb = thumb.exists()
                        elif thumb.exists():
                            has_thumb = thumb.stat().st_mtime >= stat.st_mtime
                    except OSError:
                        has_thumb = False

                    if preview_ready_cached:
                        previews_ready = preview_frames_ready_fast(preview_dir)
                    else:
                        previews_ready = preview_frames_ready_full(preview_dir, stat.st_mtime)

                    old_item = old_items_by_path.get(file_key)
                    needs_metadata_refresh = cached_sig != file_sig
                    subtitle_path = None
                    cached_subtitle = str(cached_meta.get("subtitle_path", "") or "")
                    if subtitle_ready_cached and cached_subtitle:
                        subtitle_candidate = Path(cached_subtitle)
                        if subtitle_candidate.exists():
                            subtitle_path = subtitle_candidate
                    has_subtitle = bool(subtitle_path and subtitle_path.exists())

                    if cached_sig == file_sig:
                        aspect = float(cached_meta.get("ar", 0) or 0) or 1.6
                        audio_codecs = list(cached_meta.get("audio_codecs", []))
                    else:
                        aspect = float((old_item or {}).get("ar", 0) or 0) or 1.6
                        audio_codecs = list((old_item or {}).get("audio_codecs", []) or [])
                    self._file_sig_cache[file_key] = file_sig
                    self._file_meta_cache[file_key] = {
                        "ar": aspect,
                        "subtitle_path": str(subtitle_path) if subtitle_path else "",
                        "thumb_ready": bool(has_thumb),
                        "preview_ready": bool(previews_ready),
                        "subtitle_ready": bool(has_subtitle),
                        "audio_codecs": list(audio_codecs),
                    }

                    if cached_sig == file_sig and old_item:
                        item = dict(old_item)
                        item["mtime"] = stat.st_mtime
                        item["ar"] = aspect
                        item["size"] = fmt_size(stat.st_size)
                        item["thumb_url"] = (
                            f"/thumbs/{video_id}.jpg" if has_thumb else "/thumbs/placeholder.jpg"
                        )
                        item["subtitle_url"] = f"/subtitle/{video_id}.vtt" if has_subtitle else ""
                        item["preview_urls"] = (
                            [
                                f"/thumbs/prev/{video_id}/{index:02d}.jpg"
                                for index in range(1, PREVIEW_FRAME_COUNT + 1)
                            ]
                            if previews_ready
                            else []
                        )
                        item["audio_codecs"] = list(audio_codecs)
                    else:
                        item = {
                            "id": video_id,
                            "name": path.name,
                            "relative_path": rel,
                            "folder": folder,
                            "size": fmt_size(stat.st_size),
                            "mtime": stat.st_mtime,
                            "ar": aspect,
                            "video_url": f"/video/{video_id}",
                            "thumb_url": (
                                f"/thumbs/{video_id}.jpg"
                                if has_thumb
                                else "/thumbs/placeholder.jpg"
                            ),
                            "subtitle_url": (
                                f"/subtitle/{video_id}.vtt" if has_subtitle else ""
                            ),
                            "preview_urls": (
                                [
                                    f"/thumbs/prev/{video_id}/{index:02d}.jpg"
                                    for index in range(1, PREVIEW_FRAME_COUNT + 1)
                                ]
                                if previews_ready
                                else []
                            ),
                            "audio_codecs": list(audio_codecs),
                        }
                    videos.append(item)
                    root_video_count += 1
                    if root_video_count % 100 == 0:
                        commit_snapshot(scanning=True, persist_progress=True)
                    vmap[video_id] = path
                    tmap[video_id] = thumb
                    pdir_map[video_id] = preview_dir
                    if has_subtitle and subtitle_path:
                        smap[video_id] = subtitle_path
                    else:
                        smap.pop(video_id, None)
                    if self.generate_thumbs and not has_thumb:
                        queue_missing_job(thumb_queue, video_id)
                        missing_thumb_count += 1
                    if not previews_ready:
                        queue_missing_job(preview_queue, video_id)
                        missing_preview_count += 1
                    if needs_metadata_refresh:
                        self._queue_metadata_refresh(video_id)
                        self._update_scan_progress(
                            metadata_pending=len(self._metadata_queue),
                        )

                    now_ts = time.time()
                    if now_ts - last_progress_log_at >= 2.0:
                        elapsed = max(0.001, now_ts - root_started_at)
                        logging.info(
                            "Scan progress [%s]: processed=%d videos=%d new=%d changed=%d unchanged=%d thumbs_pending=%d previews_pending=%d metadata_pending=%d rate=%.1f entries/s current=%s",
                            root_label,
                            processed_entries,
                            root_video_count,
                            new_count,
                            changed_count,
                            unchanged_count,
                            missing_thumb_count,
                            missing_preview_count,
                            len(self._metadata_queue),
                            processed_entries / elapsed,
                            path,
                        )
                        last_progress_log_at = now_ts

            removed_ids = {video_id for video_id in old_root_ids if video_id not in seen_ids}
            logging.info(
                "Scan done [%s]: videos=%d new=%d changed=%d unchanged=%d removed=%d thumbs_pending=%d previews_pending=%d elapsed=%.1fs",
                root_label,
                root_video_count,
                new_count,
                changed_count,
                unchanged_count,
                len(removed_ids),
                missing_thumb_count,
                missing_preview_count,
                time.time() - root_started_at,
            )
            with self._lock:
                self.scan_progress.update(
                    {
                        "updated_at": time.time(),
                        "processed_entries": processed_entries,
                        "videos_found": root_video_count,
                        "new_count": new_count,
                        "changed_count": changed_count,
                        "unchanged_count": unchanged_count,
                        "removed_count": len(removed_ids),
                        "thumbs_pending": missing_thumb_count,
                        "previews_pending": missing_preview_count,
                        "metadata_pending": len(self._metadata_queue),
                        "current_path": "",
                        "current_stage": "",
                    }
                )
            cleanup_removed_ids(
                removed_ids,
                old_root_tmap,
                old_root_pdir_map,
                old_root_vmap,
            )
            commit_snapshot(scanning=True, persist_progress=True)

        commit_snapshot(scanning=False)
        logging.info(
            "Full scan complete: roots=%d total_videos=%d elapsed=%.1fs",
            len(existing_roots),
            len(videos),
            time.time() - scan_started_at,
        )
        with self._lock:
            self.scan_progress = {}
        return True

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
            if not path.exists():
                return
            data = json.loads(path.read_text(encoding="utf-8"))
            rows = data.get("videos", [])
            if not isinstance(rows, list) or not rows:
                return

            videos: List[dict] = []
            vmap: Dict[str, Path] = {}
            tmap: Dict[str, Path] = {}
            pdir_map: Dict[str, Path] = {}
            smap: Dict[str, Path] = {}
            sig_cache: Dict[str, tuple[float, int]] = {}
            meta_cache: Dict[str, dict] = {}

            for row in rows:
                video_id = str(row.get("id", "")).strip()
                video_path = str(row.get("vpath", "")).strip()
                if not video_id or not video_path:
                    continue
                resolved_path = Path(video_path)
                vmap[video_id] = resolved_path
                mtime_epoch = float(row.get("mtime_epoch", 0) or 0)
                size_bytes = int(row.get("size_bytes", 0) or 0)
                if mtime_epoch > 0 and size_bytes >= 0:
                    sig_cache[str(resolved_path)] = (mtime_epoch, size_bytes)
                audio_codes = [
                    str(codec).strip().lower()
                    for codec in (row.get("audio_codecs") or [])
                    if str(codec or "").strip()
                ]
                meta_cache[str(resolved_path)] = {
                    "ar": float(row.get("ar", 1.6) or 1.6),
                    "subtitle_path": str(row.get("subtitle_path", "") or ""),
                    "thumb_ready": bool(row.get("thumb_ready", False)),
                    "preview_ready": bool(row.get("preview_ready", False)),
                    "subtitle_ready": bool(row.get("subtitle_ready", False)),
                    "audio_codecs": audio_codes,
                }
                if audio_codes:
                    self._audio_codec_cache[str(resolved_path)] = audio_codes

                thumb_path = str(row.get("thumb_path", "")).strip()
                if thumb_path:
                    tmap[video_id] = Path(thumb_path)
                preview_path = str(row.get("preview_dir", "")).strip()
                if preview_path:
                    pdir_map[video_id] = Path(preview_path)
                subtitle_path = str(row.get("subtitle_path", "")).strip()
                if subtitle_path:
                    smap[video_id] = Path(subtitle_path)

                videos.append(
                    {
                        "id": video_id,
                        "name": str(row.get("name", "")),
                        "relative_path": str(row.get("relative_path", "")),
                        "folder": str(row.get("folder", "")),
                        "size": str(row.get("size", "")),
                        "ar": float(row.get("ar", 1.6) or 1.6),
                        "video_url": f"/video/{video_id}",
                        "thumb_url": str(row.get("thumb_url", "/thumbs/placeholder.jpg"))
                        or "/thumbs/placeholder.jpg",
                        "subtitle_url": str(row.get("subtitle_url", "")),
                        "plex_stream_url": str(row.get("plex_stream_url", "")),
                        "preview_urls": (
                            list(row.get("preview_urls", []))
                            if isinstance(row.get("preview_urls", []), list)
                            else []
                        ),
                    }
                )

            if not videos:
                return

            private_ids = {video["id"] for video in videos if self._is_private_video(video)}
            with self._lock:
                self._videos = videos
                self._public_videos = list(videos)
                self.video_map = vmap
                self.thumb_map = tmap
                self.preview_dir_map = pdir_map
                self.subtitle_map = smap
                self.private_video_ids = private_ids
                self._public_private_video_ids = set(private_ids)
                self._file_sig_cache = sig_cache
                self._file_meta_cache = meta_cache
                self.available = True
                self.last_error = None
                self.last_scan_at = float(data.get("last_scan_at", time.time()))
            logging.info("Loaded catalog index: %d videos", len(videos))
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

            rows = []
            for video in videos_snapshot:
                video_id = video.get("id", "")
                video_path = video_map_snapshot.get(video_id)
                if not video_path:
                    continue
                cached_sig = file_sig_snapshot.get(str(video_path))
                if cached_sig:
                    mtime_epoch = float(cached_sig[0])
                    size_bytes = int(cached_sig[1])
                else:
                    try:
                        video_stat = video_path.stat()
                        mtime_epoch = float(video_stat.st_mtime)
                        size_bytes = int(video_stat.st_size)
                    except Exception:
                        mtime_epoch = 0.0
                        size_bytes = 0
                file_meta = file_meta_snapshot.get(str(video_path), {})
                rows.append(
                    {
                        "id": video_id,
                        "name": video.get("name", ""),
                        "relative_path": video.get("relative_path", ""),
                        "folder": video.get("folder", ""),
                        "size": video.get("size", ""),
                        "size_bytes": size_bytes,
                        "mtime_epoch": mtime_epoch,
                        "ar": video.get("ar", 1.6),
                        "thumb_url": video.get("thumb_url", ""),
                        "subtitle_url": video.get("subtitle_url", ""),
                        "plex_stream_url": video.get("plex_stream_url", ""),
                        "preview_urls": video.get("preview_urls", []),
                        "thumb_ready": bool(file_meta.get("thumb_ready", False)),
                        "preview_ready": bool(file_meta.get("preview_ready", False)),
                        "subtitle_ready": bool(file_meta.get("subtitle_ready", False)),
                        "vpath": str(video_path),
                        "thumb_path": str(thumb_map_snapshot.get(video_id, "")),
                        "preview_dir": str(preview_dir_snapshot.get(video_id, "")),
                        "subtitle_path": str(subtitle_map_snapshot.get(video_id, "")),
                    }
                )
            payload = {"version": 1, "last_scan_at": last_scan_at, "videos": rows}
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
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
            if aspect and aspect > 0:
                meta["ar"] = float(aspect)
            if subtitle_path and subtitle_path.exists():
                meta["subtitle_path"] = str(subtitle_path)
                meta["subtitle_ready"] = True
                self.subtitle_map[video_id] = subtitle_path
            else:
                meta["subtitle_path"] = ""
                meta["subtitle_ready"] = False
                self.subtitle_map.pop(video_id, None)
            if audio_codecs is not None:
                meta["audio_codecs"] = list(audio_codecs)
                self._audio_codec_cache[file_key] = list(audio_codecs)
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
        now_ts = time.time()
        if (not scanning) and (now_ts - self._last_index_persist_at >= 15):
            self._save_index(INDEX_STATE_PATH)
            self._last_index_persist_at = now_ts

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
        if video_path.suffix.lower() in DIRECT_AUDIO_EXTENSIONS:
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
        while not self._stop.is_set():
            video_id = self.pop_metadata_job()
            if not video_id:
                time.sleep(0.25)
                continue
            try:
                self._probe_video_metadata(video_id)
            except Exception as exc:
                logging.debug("Metadata refresh failed for %s: %s", video_id, exc)
            finally:
                with self._lock:
                    self._metadata_inflight.discard(video_id)
                    pending = len(self._metadata_queue) + len(self._metadata_inflight)
                self._update_scan_progress(metadata_pending=pending)

    def _thumb_worker(self):
        while not self._stop.is_set():
            job = self.pop_thumb_job()
            if not job:
                time.sleep(0.5)
                continue
            if not FFMPEG:
                continue
            video_path = self.video_map.get(job)
            thumb_path = self.thumb_map.get(job)
            if not video_path or not thumb_path:
                continue
            thumb_path.parent.mkdir(parents=True, exist_ok=True)
            ok = False
            for point in ("00:00:05", "00:00:02", "00:00:01"):
                cmd = [
                    FFMPEG,
                    "-y",
                    "-ss",
                    point,
                    "-i",
                    str(video_path),
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale=512:-1:flags=lanczos",
                    str(thumb_path),
                ]
                try:
                    subprocess.run(
                        cmd,
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    ok = True
                    break
                except subprocess.CalledProcessError:
                    continue
            if ok:
                self.update_thumb_url(job)

            with self._lock:
                self._thumb_done += 1
                done = self._thumb_done
                total = self._thumb_total
            if total and (done % 20 == 0 or done == total):
                pct = min(100.0, (done / total) * 100.0)
                logging.info("Thumbnail progress: %.1f%% (%d/%d)", pct, done, total)

    def _probe_aspect(self, video_path: Path):
        if not FFPROBE:
            return None
        key = str(video_path)
        if key in self._aspect_cache:
            return self._aspect_cache[key]
        try:
            out = (
                subprocess.check_output(
                    [
                        FFPROBE,
                        "-v",
                        "error",
                        "-select_streams",
                        "v:0",
                        "-show_entries",
                        "stream=width,height",
                        "-of",
                        "csv=p=0:s=x",
                        str(video_path),
                    ],
                    stderr=subprocess.DEVNULL,
                    timeout=FFPROBE_TIMEOUT,
                )
                .decode("utf-8", "ignore")
                .strip()
            )
            if "x" in out:
                width, height = out.split("x", 1)
                aspect_width, aspect_height = float(width), float(height)
                if aspect_width > 0 and aspect_height > 0:
                    aspect_ratio = aspect_width / aspect_height
                    self._aspect_cache[key] = aspect_ratio
                    return aspect_ratio
        except Exception:
            pass
        return None

    def _probe_audio_codecs(self, video_path: Path) -> List[str]:
        if not FFPROBE or not video_path.exists():
            return []
        key = str(video_path)
        cached = self._audio_codec_cache.get(key)
        if cached is not None:
            return list(cached)
        try:
            out = (
                subprocess.check_output(
                    [
                        FFPROBE,
                        "-v",
                        "error",
                        "-select_streams",
                        "a",
                        "-show_entries",
                        "stream=codec_name",
                        "-of",
                        "csv=p=0",
                        str(video_path),
                    ],
                    stderr=subprocess.DEVNULL,
                    timeout=FFPROBE_TIMEOUT,
                )
                .decode("utf-8", "ignore")
                .strip()
            )
            codecs = [
                line.strip().lower()
                for line in out.splitlines()
                if line.strip()
            ]
            self._audio_codec_cache[key] = codecs
            return codecs
        except Exception:
            return []

    def _probe_duration(self, video_path: Path):
        if not FFPROBE:
            return None
        try:
            out = (
                subprocess.check_output(
                    [
                        FFPROBE,
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=nw=1:nk=1",
                        str(video_path),
                    ],
                    stderr=subprocess.DEVNULL,
                    timeout=FFPROBE_TIMEOUT,
                )
                .decode("utf-8", "ignore")
                .strip()
            )
            return float(out) if out else None
        except Exception:
            return None

    def _pick_best_subtitle_file(self, files: List[Path]) -> Path | None:
        if not files:
            return None

        def score(path: Path):
            name = path.name.lower()
            value = 0
            if any(
                key in name
                for key in [
                    "traditional",
                    "trad",
                    "繁",
                    "cht",
                    "zh-tw",
                    "zht",
                    "tc",
                    "chi",
                ]
            ):
                value += 30
            if any(key in name for key in ["eng", "english"]):
                value += 5
            return (value, path.stat().st_mtime)

        return sorted(files, key=score, reverse=True)[0]

    def _srt_to_vtt(self, srt_path: Path, vtt_path: Path):
        import re

        text = srt_path.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", text)
        vtt_path.write_text("WEBVTT\n\n" + text, encoding="utf-8")

    def _extract_chi_from_mkv_to_vtt(self, mkv_path: Path, target_vtt: Path) -> Path | None:
        if not FFPROBE or not FFMPEG or not mkv_path.exists():
            return None
        try:
            probe = subprocess.run(
                [FFPROBE, "-v", "quiet", "-print_format", "json", "-show_streams", str(mkv_path)],
                capture_output=True,
                text=True,
                timeout=FFPROBE_TIMEOUT,
            )
            if probe.returncode != 0:
                return None
            streams = json.loads(probe.stdout).get("streams", [])
            chosen_idx = None
            for stream in streams:
                if stream.get("codec_type") != "subtitle":
                    continue
                tags = stream.get("tags", {}) or {}
                language = str(tags.get("language", "")).lower()
                title = str(tags.get("title", "")).lower()
                if language in {"chi", "zho", "zh"} and any(
                    key in title for key in ["traditional", "trad", "繁", "cht", "zh-tw"]
                ):
                    chosen_idx = stream.get("index")
                    break
            if chosen_idx is None:
                for stream in streams:
                    if stream.get("codec_type") == "subtitle":
                        tags = stream.get("tags", {}) or {}
                        language = str(tags.get("language", "")).lower()
                        if language in {"chi", "zho", "zh"}:
                            chosen_idx = stream.get("index")
                            break
            if chosen_idx is None:
                return None

            if target_vtt.exists() and target_vtt.stat().st_mtime >= mkv_path.stat().st_mtime:
                return target_vtt

            tmp_srt = target_vtt.with_suffix(".srt.tmp")
            subprocess.run(
                [FFMPEG, "-y", "-i", str(mkv_path), "-map", f"0:{chosen_idx}", str(tmp_srt)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=FFMPEG_TIMEOUT,
            )
            self._srt_to_vtt(tmp_srt, target_vtt)
            try:
                tmp_srt.unlink()
            except Exception:
                pass
            return target_vtt if target_vtt.exists() else None
        except Exception as exc:
            logging.debug("MKV subtitle extract failed for %s: %s", mkv_path.name, exc)
            return None

    def _resolve_sidecar_subtitle(self, video_path: Path):
        base = video_path.with_suffix("")
        parent = video_path.parent
        stem = base.name

        def glob_many(exts: List[str]):
            items: List[Path] = []
            for ext in exts:
                items.extend(sorted(parent.glob(f"{stem}*{ext}")))
            return [item for item in items if item.is_file()]

        target_vtt = video_path.with_suffix(".vtt")
        sibling_mkv = video_path.with_suffix(".mkv")
        extracted = self._extract_chi_from_mkv_to_vtt(sibling_mkv, target_vtt)
        if extracted and extracted.exists():
            return extracted

        vtt_files = glob_many([".vtt"])
        vtt = self._pick_best_subtitle_file(vtt_files)
        if vtt and vtt.stat().st_mtime >= video_path.stat().st_mtime:
            return vtt

        srt = self._pick_best_subtitle_file(glob_many([".srt"]))
        ass = self._pick_best_subtitle_file(glob_many([".ass", ".ssa"]))

        if srt:
            try:
                if (not target_vtt.exists()) or target_vtt.stat().st_mtime < max(
                    video_path.stat().st_mtime,
                    srt.stat().st_mtime,
                ):
                    self._srt_to_vtt(srt, target_vtt)
                return target_vtt if target_vtt.exists() else None
            except Exception as exc:
                logging.debug("SRT->VTT failed for %s: %s", video_path.name, exc)

        if ass and FFMPEG:
            try:
                if (not target_vtt.exists()) or target_vtt.stat().st_mtime < max(
                    video_path.stat().st_mtime,
                    ass.stat().st_mtime,
                ):
                    cmd = [FFMPEG, "-y", "-i", str(ass), str(target_vtt)]
                    subprocess.run(
                        cmd,
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=FFMPEG_TIMEOUT,
                    )
                return target_vtt if target_vtt.exists() else None
            except Exception as exc:
                logging.debug("ASS/SSA->VTT failed for %s: %s", video_path.name, exc)

        return None

    def _extract_subtitle(
        self,
        src_path: Path,
        out_mp4: Path,
        target_lang: str = "chi",
        target_title: str = "Traditional",
    ):
        if not FFPROBE or not FFMPEG:
            return
        try:
            probe_cmd = [
                FFPROBE,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                str(src_path),
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return
            streams = json.loads(result.stdout).get("streams", [])
            subtitle_idx = None
            for index, stream in enumerate(streams):
                if stream.get("codec_type") == "subtitle":
                    tags = stream.get("tags", {})
                    if tags.get("language") == target_lang and tags.get("title") == target_title:
                        subtitle_idx = index
                        break

            if subtitle_idx is None:
                logging.debug("Subtitle stream not found: %s", src_path.name)
                return

            vtt_path = out_mp4.with_suffix(".vtt")
            if vtt_path.exists() and vtt_path.stat().st_mtime >= src_path.stat().st_mtime:
                return

            srt_path = out_mp4.with_suffix(".srt.tmp")
            extract_cmd = [
                FFMPEG,
                "-y",
                "-i",
                str(src_path),
                "-map",
                f"0:s:{subtitle_idx}",
                str(srt_path),
            ]
            subprocess.run(
                extract_cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._srt_to_vtt(srt_path, vtt_path)
            srt_path.unlink()
            logging.info("Extracted subtitle: %s", vtt_path.name)
        except Exception as exc:
            logging.debug("Subtitle extraction failed: %s", exc)

    def _preview_worker(self):
        while not self._stop.is_set():
            video_id = self.pop_preview_job()
            if not video_id:
                time.sleep(0.7)
                continue
            if not FFMPEG:
                continue
            video_path = self.video_map.get(video_id)
            preview_dir = self.preview_dir_map.get(video_id)
            if not video_path or not preview_dir:
                continue
            try:
                preview_dir.mkdir(parents=True, exist_ok=True)
                duration = self._probe_duration(video_path) or 0.0
                if duration > 5:
                    fractions = [
                        (index + 1) / (PREVIEW_FRAME_COUNT + 1)
                        for index in range(PREVIEW_FRAME_COUNT)
                    ]
                    times = [
                        max(0.5, min(duration - 0.5, duration * fraction))
                        for fraction in fractions
                    ]
                else:
                    times = [0.5 + index * 0.5 for index in range(PREVIEW_FRAME_COUNT)]
                ok_count = 0
                for index, preview_time in enumerate(times, 1):
                    out = preview_dir / f"{index:02d}.jpg"
                    try:
                        if out.exists() and out.stat().st_mtime >= video_path.stat().st_mtime:
                            ok_count += 1
                            continue
                    except OSError:
                        pass
                    cmd = [
                        FFMPEG,
                        "-y",
                        "-ss",
                        f"{preview_time:.3f}",
                        "-i",
                        str(video_path),
                        "-frames:v",
                        "1",
                        "-vf",
                        f"scale={PREVIEW_WIDTH}:-1:flags=lanczos",
                        str(out),
                    ]
                    try:
                        subprocess.run(
                            cmd,
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        ok_count += 1
                    except subprocess.CalledProcessError:
                        continue
                if ok_count == PREVIEW_FRAME_COUNT:
                    self.update_preview_urls(video_id)
            except Exception as exc:
                logging.debug("Preview gen failed for %s: %s", video_id, exc)

    def pop_transcode_job(self):
        with self._lock:
            return self._transcode_queue.pop(0) if self._transcode_queue else None

    def _transcode_worker(self):
        while not self._stop.is_set():
            job = self.pop_transcode_job()
            if not job:
                time.sleep(0.8)
                continue
            key = str(job.resolve())
            try:
                if not FFMPEG or not job.exists():
                    continue
                out_mp4 = job.with_suffix(".mp4")
                try:
                    if out_mp4.exists() and out_mp4.stat().st_mtime >= job.stat().st_mtime:
                        continue
                except OSError:
                    pass
                out_tmp = out_mp4.with_name(out_mp4.name + ".tmp.mp4")
                is_mkv = job.suffix.lower() == ".mkv"
                ok = False
                if not is_mkv:
                    remux_cmd = [
                        FFMPEG,
                        "-y",
                        "-i",
                        str(job),
                        "-map",
                        "0",
                        "-c",
                        "copy",
                        "-movflags",
                        "+faststart",
                        str(out_tmp),
                    ]
                    try:
                        subprocess.run(
                            remux_cmd,
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        ok = True
                    except subprocess.CalledProcessError:
                        ok = False
                if not ok:
                    transcode_cmd = [
                        FFMPEG,
                        "-y",
                        "-i",
                        str(job),
                        "-map",
                        "0:v:0",
                        "-map",
                        "0:a:0?",
                        "-c:v",
                        "libx264",
                        "-preset",
                        "veryfast",
                        "-crf",
                        "23",
                        "-c:a",
                        "aac",
                        "-b:a",
                        "160k",
                        "-movflags",
                        "+faststart",
                        str(out_tmp),
                    ]
                    subprocess.run(
                        transcode_cmd,
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    ok = True
                if ok:
                    out_tmp.replace(out_mp4)
                    logging.info("Converted %s -> %s", job.name, out_mp4.name)
                    if is_mkv:
                        self._extract_subtitle(job, out_mp4, "chi", "Traditional")
                    threading.Thread(target=self.scan, daemon=True).start()
            except Exception as exc:
                logging.warning("Transcode failed for %s: %s", job, exc)
                try:
                    out_mp4 = job.with_suffix(".mp4")
                    out_tmp = out_mp4.with_name(out_mp4.name + ".tmp.mp4")
                    if out_tmp.exists():
                        out_tmp.unlink()
                except Exception:
                    pass
            finally:
                with self._lock:
                    self._transcode_inflight.discard(key)


def load_html_template() -> str:
    html_path = Path(__file__).with_name("index.html")
    try:
        return html_path.read_text(encoding="utf-8")
    except Exception as exc:
        logging.error("Failed to load template %s: %s", html_path, exc)
        return (
            "<!doctype html><html><body><h1>Cat Theatre</h1>"
            "<p>Template load failed.</p></body></html>"
        )
