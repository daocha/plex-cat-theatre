#!/usr/bin/env python3
"""Scan orchestration helpers for the catalog."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

from movies_catalog_media import fmt_size, vid_id


def run_catalog_scan(catalog, *, video_extensions, source_extensions, preview_frame_count):
    with catalog._lock:
        catalog.is_scanning = True
        catalog.scan_progress = {
            "phase": "initializing",
            "started_at": time.time(),
            "updated_at": time.time(),
            "roots_total": len(catalog.roots),
            "root_index": 0,
            "root_name": "",
            "root_path": "",
            "traversed_entries": 0,
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
        videos = [dict(v, mtime=0) for v in catalog._videos]
        vmap = dict(catalog.video_map)
        tmap = dict(catalog.thumb_map)
        pdir_map = dict(catalog.preview_dir_map)
        smap = dict(catalog.subtitle_map)
        thumb_queue = list(catalog._thumb_queue)
        preview_queue = list(catalog._preview_queue)
        old_items_by_id = {
            str(video.get("id", "")): dict(video) for video in catalog._videos
        }
        old_items_by_path = {
            str(path): old_items_by_id.get(str(video_id), {})
            for video_id, path in catalog.video_map.items()
            if str(video_id) in old_items_by_id
        }

    existing_roots = [root for root in catalog.roots if root.exists()]
    if not existing_roots:
        with catalog._lock:
            catalog.available = True
            catalog.last_error = f"No roots found: {', '.join(str(root) for root in catalog.roots)}"
            catalog.last_scan_at = time.time()
            catalog.is_scanning = False
            catalog.scan_progress = {}
        logging.warning(catalog.last_error)
        return False

    transcode_jobs = []
    scan_started_at = time.time()
    logging.info(
        "Full scan start: roots=%d thumbs=%s previews=%s transcode=%s",
        len(existing_roots),
        "enabled" if catalog.generate_thumbs else "disabled",
        "enabled",
        "enabled" if catalog.transcode_enabled else "disabled",
    )

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
        with catalog._lock:
            catalog.scan_progress.update(
                {
                    "phase": "scanning",
                    "updated_at": time.time(),
                    "root_index": root_index,
                    "root_name": root_label,
                    "root_path": str(root),
                    "traversed_entries": 0,
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
                    "metadata_pending": len(catalog._metadata_queue),
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
        catalog._remove_root_from_accumulator(
            root_label=root_label,
            videos=videos,
            vmap=vmap,
            tmap=tmap,
            pdir_map=pdir_map,
            smap=smap,
            thumb_queue=thumb_queue,
            preview_queue=preview_queue,
        )
        seen_ids = set()
        last_progress_log_at = 0.0
        traversed_entries = 0

        candidate_suffixes = set(video_extensions) | set(source_extensions)
        for dirpath, _, filenames in os.walk(root):
            catalog._update_scan_progress(
                phase="scanning",
                root_index=root_index,
                root_name=root_label,
                root_path=str(root),
                traversed_entries=traversed_entries,
                processed_entries=processed_entries,
                videos_found=root_video_count,
                new_count=new_count,
                changed_count=changed_count,
                unchanged_count=unchanged_count,
                thumbs_pending=missing_thumb_count,
                previews_pending=missing_preview_count,
                metadata_pending=len(catalog._metadata_queue),
                current_path=str(dirpath),
                current_stage="walking",
            )
            for filename in filenames:
                traversed_entries += 1
                path = Path(dirpath) / filename
                suffix = path.suffix.lower()
                if suffix not in candidate_suffixes:
                    if traversed_entries % 500 == 0:
                        catalog._update_scan_progress(
                            phase="scanning",
                            root_index=root_index,
                            root_name=root_label,
                            root_path=str(root),
                            traversed_entries=traversed_entries,
                            processed_entries=processed_entries,
                            videos_found=root_video_count,
                            new_count=new_count,
                            changed_count=changed_count,
                            unchanged_count=unchanged_count,
                            thumbs_pending=missing_thumb_count,
                            previews_pending=missing_preview_count,
                            metadata_pending=len(catalog._metadata_queue),
                            current_path=str(path),
                            current_stage="walking",
                        )
                    continue
                processed_entries += 1
                catalog._update_scan_progress(
                    phase="scanning",
                    root_index=root_index,
                    root_name=root_label,
                    root_path=str(root),
                    traversed_entries=traversed_entries,
                    processed_entries=processed_entries,
                    videos_found=root_video_count,
                    new_count=new_count,
                    changed_count=changed_count,
                    unchanged_count=unchanged_count,
                    thumbs_pending=missing_thumb_count,
                    previews_pending=missing_preview_count,
                    metadata_pending=len(catalog._metadata_queue),
                    current_path=str(path),
                    current_stage="discovering",
                )
                if suffix in source_extensions:
                    if catalog.transcode_enabled:
                        transcode_jobs.append(path)
                        if len(transcode_jobs) <= 5 or len(transcode_jobs) % 50 == 0:
                            logging.info(
                                "Scan transcode candidate [%s]: queued=%d file=%s",
                                root_label,
                                len(transcode_jobs),
                                path,
                            )
                        continue
                stat = path.stat()
                video_id = vid_id(path)
                seen_ids.add(video_id)
                rel_under_root = os.path.relpath(path, root)
                rel = f"{root_label}/{rel_under_root}"
                parent = Path(rel_under_root).parent
                folder = f"{root_label}/" + (str(parent) if parent != Path(".") else "(root)")
                thumb = catalog.thumbs_dir / f"{video_id}.jpg"
                preview_dir = catalog.thumbs_dir / "previews" / video_id

                file_key = str(path)
                file_sig = (float(stat.st_mtime), int(stat.st_size))
                cached_sig = catalog._file_sig_cache.get(file_key)
                cached_meta = catalog._file_meta_cache.get(file_key, {}) if cached_sig == file_sig else {}
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
                    previews_ready = catalog._preview_frames_ready_fast(preview_dir)
                else:
                    previews_ready = catalog._preview_frames_ready_full(preview_dir, stat.st_mtime)

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
                catalog._file_sig_cache[file_key] = file_sig
                catalog._file_meta_cache[file_key] = {
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
                    item["thumb_url"] = f"/thumbs/{video_id}.jpg" if has_thumb else "/thumbs/placeholder.jpg"
                    item["subtitle_url"] = f"/subtitle/{video_id}.vtt" if has_subtitle else ""
                    item["preview_urls"] = (
                        [f"/thumbs/prev/{video_id}/{index:02d}.jpg" for index in range(1, preview_frame_count + 1)]
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
                        "thumb_url": f"/thumbs/{video_id}.jpg" if has_thumb else "/thumbs/placeholder.jpg",
                        "subtitle_url": f"/subtitle/{video_id}.vtt" if has_subtitle else "",
                        "preview_urls": (
                            [f"/thumbs/prev/{video_id}/{index:02d}.jpg" for index in range(1, preview_frame_count + 1)]
                            if previews_ready
                            else []
                        ),
                        "audio_codecs": list(audio_codecs),
                    }
                videos.append(item)
                root_video_count += 1
                if root_video_count % 100 == 0:
                    catalog._commit_scan_snapshot(
                        videos=videos,
                        vmap=vmap,
                        tmap=tmap,
                        pdir_map=pdir_map,
                        smap=smap,
                        thumb_queue=thumb_queue,
                        preview_queue=preview_queue,
                        transcode_jobs=transcode_jobs,
                        scanning=True,
                        persist_progress=True,
                    )
                vmap[video_id] = path
                tmap[video_id] = thumb
                pdir_map[video_id] = preview_dir
                if has_subtitle and subtitle_path:
                    smap[video_id] = subtitle_path
                else:
                    smap.pop(video_id, None)
                if catalog.generate_thumbs and not has_thumb:
                    catalog._queue_missing_job(thumb_queue, video_id)
                    missing_thumb_count += 1
                if not previews_ready:
                    catalog._queue_missing_job(preview_queue, video_id)
                    missing_preview_count += 1
                if needs_metadata_refresh:
                    catalog._queue_metadata_refresh(video_id)
                    catalog._update_scan_progress(metadata_pending=len(catalog._metadata_queue))

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
                        len(catalog._metadata_queue),
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
        with catalog._lock:
            catalog.scan_progress.update(
                {
                    "updated_at": time.time(),
                    "traversed_entries": traversed_entries,
                    "processed_entries": processed_entries,
                    "videos_found": root_video_count,
                    "new_count": new_count,
                    "changed_count": changed_count,
                    "unchanged_count": unchanged_count,
                    "removed_count": len(removed_ids),
                    "thumbs_pending": missing_thumb_count,
                    "previews_pending": missing_preview_count,
                    "metadata_pending": len(catalog._metadata_queue),
                    "current_path": "",
                    "current_stage": "",
                }
            )
        catalog._cleanup_removed_ids(
            removed_ids,
            old_root_tmap,
            old_root_pdir_map,
            old_root_vmap,
        )
        catalog._commit_scan_snapshot(
            videos=videos,
            vmap=vmap,
            tmap=tmap,
            pdir_map=pdir_map,
            smap=smap,
            thumb_queue=thumb_queue,
            preview_queue=preview_queue,
            transcode_jobs=transcode_jobs,
            scanning=True,
            persist_progress=True,
        )

    catalog._wait_for_metadata_idle()
    catalog._commit_scan_snapshot(
        videos=videos,
        vmap=vmap,
        tmap=tmap,
        pdir_map=pdir_map,
        smap=smap,
        thumb_queue=thumb_queue,
        preview_queue=preview_queue,
        transcode_jobs=transcode_jobs,
        scanning=False,
    )
    logging.info(
        "Full scan complete: roots=%d total_videos=%d elapsed=%.1fs",
        len(existing_roots),
        len(videos),
        time.time() - scan_started_at,
    )
    with catalog._lock:
        catalog.scan_progress = {}
    return True
