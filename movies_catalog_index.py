#!/usr/bin/env python3
"""Index load/save helpers for the catalog."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, List


def load_catalog_index(path: Path, is_private_video_fn):
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("videos", [])
    if not isinstance(rows, list) or not rows:
        return None

    videos: List[dict] = []
    vmap: Dict[str, Path] = {}
    tmap: Dict[str, Path] = {}
    pdir_map: Dict[str, Path] = {}
    smap: Dict[str, Path] = {}
    sig_cache: Dict[str, tuple[float, int]] = {}
    meta_cache: Dict[str, dict] = {}
    audio_codec_cache: Dict[str, List[str]] = {}

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
            audio_codec_cache[str(resolved_path)] = audio_codes

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
                "audio_codecs": list(audio_codes),
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
        return None

    private_ids = {video["id"] for video in videos if is_private_video_fn(video)}
    return {
        "videos": videos,
        "video_map": vmap,
        "thumb_map": tmap,
        "preview_dir_map": pdir_map,
        "subtitle_map": smap,
        "file_sig_cache": sig_cache,
        "file_meta_cache": meta_cache,
        "audio_codec_cache": audio_codec_cache,
        "private_ids": private_ids,
        "last_scan_at": float(data.get("last_scan_at", time.time())),
    }


def save_catalog_index(
    path: Path,
    *,
    videos_snapshot,
    video_map_snapshot,
    thumb_map_snapshot,
    preview_dir_snapshot,
    subtitle_map_snapshot,
    file_sig_snapshot,
    file_meta_snapshot,
    last_scan_at,
):
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
                "audio_codecs": list(video.get("audio_codecs", [])),
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
    logging.debug("Saved catalog index: %s (%d videos)", path, len(rows))
