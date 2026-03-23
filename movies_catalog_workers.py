#!/usr/bin/env python3
"""Background worker helpers for the catalog."""

from __future__ import annotations

import logging
import subprocess
import threading
import time


def run_metadata_worker(catalog):
    while not catalog._stop.is_set():
        video_id = catalog.pop_metadata_job()
        if not video_id:
            time.sleep(0.25)
            continue
        try:
            catalog._probe_video_metadata(video_id)
        except Exception as exc:
            logging.debug("Metadata refresh failed for %s: %s", video_id, exc)
        finally:
            with catalog._lock:
                catalog._metadata_inflight.discard(video_id)
                pending = len(catalog._metadata_queue) + len(catalog._metadata_inflight)
            catalog._update_scan_progress(metadata_pending=pending)


def run_thumb_worker(catalog, *, ffmpeg_bin):
    while not catalog._stop.is_set():
        job = catalog.pop_thumb_job()
        if not job:
            time.sleep(0.5)
            continue
        if not ffmpeg_bin:
            continue
        video_path = catalog.video_map.get(job)
        thumb_path = catalog.thumb_map.get(job)
        if not video_path or not thumb_path:
            continue
        thumb_path.parent.mkdir(parents=True, exist_ok=True)
        ok = False
        for point in ("00:00:05", "00:00:02", "00:00:01"):
            cmd = [
                ffmpeg_bin,
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
            catalog.update_thumb_url(job)

        with catalog._lock:
            catalog._thumb_done += 1
            done = catalog._thumb_done
            total = catalog._thumb_total
        if total and (done % 20 == 0 or done == total):
            pct = min(100.0, (done / total) * 100.0)
            logging.info("Thumbnail progress: %.1f%% (%d/%d)", pct, done, total)


def run_preview_worker(catalog, *, ffmpeg_bin, preview_frame_count, preview_width):
    while not catalog._stop.is_set():
        video_id = catalog.pop_preview_job()
        if not video_id:
            time.sleep(0.7)
            continue
        if not ffmpeg_bin:
            continue
        video_path = catalog.video_map.get(video_id)
        preview_dir = catalog.preview_dir_map.get(video_id)
        if not video_path or not preview_dir:
            continue
        try:
            preview_dir.mkdir(parents=True, exist_ok=True)
            duration = catalog._probe_duration(video_path) or 0.0
            if duration > 5:
                fractions = [
                    (index + 1) / (preview_frame_count + 1)
                    for index in range(preview_frame_count)
                ]
                times = [
                    max(0.5, min(duration - 0.5, duration * fraction))
                    for fraction in fractions
                ]
            else:
                times = [0.5 + index * 0.5 for index in range(preview_frame_count)]
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
                    ffmpeg_bin,
                    "-y",
                    "-ss",
                    f"{preview_time:.3f}",
                    "-i",
                    str(video_path),
                    "-frames:v",
                    "1",
                    "-vf",
                    f"scale={preview_width}:-1:flags=lanczos",
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
            if ok_count == preview_frame_count:
                catalog.update_preview_urls(video_id)
        except Exception as exc:
            logging.debug("Preview gen failed for %s: %s", video_id, exc)


def run_transcode_worker(catalog, *, ffmpeg_bin):
    while not catalog._stop.is_set():
        job = catalog.pop_transcode_job()
        if not job:
            time.sleep(0.8)
            continue
        key = str(job.resolve())
        try:
            if not ffmpeg_bin or not job.exists():
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
                    ffmpeg_bin,
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
                    ffmpeg_bin,
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
                    catalog._extract_subtitle(job, out_mp4, "chi", "Traditional")
                threading.Thread(target=catalog.scan, daemon=True).start()
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
            with catalog._lock:
                catalog._transcode_inflight.discard(key)
