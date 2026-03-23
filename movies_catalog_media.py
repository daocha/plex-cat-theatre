#!/usr/bin/env python3
"""Media probing and subtitle helper functions for the catalog."""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Optional

from movies_resources import load_asset_text


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


def probe_aspect(
    video_path: Path,
    ffprobe_bin: Optional[str],
    aspect_cache: dict[str, float],
    timeout: int,
):
    if not ffprobe_bin:
        return None
    key = str(video_path)
    if key in aspect_cache:
        return aspect_cache[key]
    try:
        out = (
            subprocess.check_output(
                [
                    ffprobe_bin,
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
                timeout=timeout,
            )
            .decode("utf-8", "ignore")
            .strip()
        )
        if "x" in out:
            width, height = out.split("x", 1)
            aspect_width, aspect_height = float(width), float(height)
            if aspect_width > 0 and aspect_height > 0:
                aspect_ratio = aspect_width / aspect_height
                aspect_cache[key] = aspect_ratio
                return aspect_ratio
    except Exception:
        pass
    return None


def probe_audio_codecs(
    video_path: Path,
    ffprobe_bin: Optional[str],
    audio_codec_cache: dict[str, List[str]],
    timeout: int,
) -> List[str]:
    if not ffprobe_bin or not video_path.exists():
        return []
    key = str(video_path)
    cached = audio_codec_cache.get(key)
    if cached is not None:
        return list(cached)
    try:
        out = (
            subprocess.check_output(
                [
                    ffprobe_bin,
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
                timeout=timeout,
            )
            .decode("utf-8", "ignore")
            .strip()
        )
        codecs = [line.strip().lower() for line in out.splitlines() if line.strip()]
        audio_codec_cache[key] = codecs
        return codecs
    except Exception:
        return []


def probe_duration(video_path: Path, ffprobe_bin: Optional[str], timeout: int):
    if not ffprobe_bin:
        return None
    try:
        out = (
            subprocess.check_output(
                [
                    ffprobe_bin,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=nw=1:nk=1",
                    str(video_path),
                ],
                stderr=subprocess.DEVNULL,
                timeout=timeout,
            )
            .decode("utf-8", "ignore")
            .strip()
        )
        return float(out) if out else None
    except Exception:
        return None


def pick_best_subtitle_file(files: List[Path]) -> Optional[Path]:
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


def srt_to_vtt(srt_path: Path, vtt_path: Path):
    import re

    text = srt_path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", text)
    vtt_path.write_text("WEBVTT\n\n" + text, encoding="utf-8")


def extract_chi_from_mkv_to_vtt(
    mkv_path: Path,
    target_vtt: Path,
    ffprobe_bin: Optional[str],
    ffmpeg_bin: Optional[str],
    ffprobe_timeout: int,
    ffmpeg_timeout: int,
) -> Optional[Path]:
    if not ffprobe_bin or not ffmpeg_bin or not mkv_path.exists():
        return None
    try:
        probe = subprocess.run(
            [ffprobe_bin, "-v", "quiet", "-print_format", "json", "-show_streams", str(mkv_path)],
            capture_output=True,
            text=True,
            timeout=ffprobe_timeout,
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
            [ffmpeg_bin, "-y", "-i", str(mkv_path), "-map", f"0:{chosen_idx}", str(tmp_srt)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=ffmpeg_timeout,
        )
        srt_to_vtt(tmp_srt, target_vtt)
        try:
            tmp_srt.unlink()
        except Exception:
            pass
        return target_vtt if target_vtt.exists() else None
    except Exception as exc:
        logging.debug("MKV subtitle extract failed for %s: %s", mkv_path.name, exc)
        return None


def resolve_sidecar_subtitle(
    video_path: Path,
    ffprobe_bin: Optional[str],
    ffmpeg_bin: Optional[str],
    ffprobe_timeout: int,
    ffmpeg_timeout: int,
):
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
    extracted = extract_chi_from_mkv_to_vtt(
        sibling_mkv,
        target_vtt,
        ffprobe_bin,
        ffmpeg_bin,
        ffprobe_timeout,
        ffmpeg_timeout,
    )
    if extracted and extracted.exists():
        return extracted

    vtt_files = glob_many([".vtt"])
    vtt = pick_best_subtitle_file(vtt_files)
    if vtt and vtt.stat().st_mtime >= video_path.stat().st_mtime:
        return vtt

    srt = pick_best_subtitle_file(glob_many([".srt"]))
    ass = pick_best_subtitle_file(glob_many([".ass", ".ssa"]))

    if srt:
        try:
            if (not target_vtt.exists()) or target_vtt.stat().st_mtime < max(
                video_path.stat().st_mtime,
                srt.stat().st_mtime,
            ):
                srt_to_vtt(srt, target_vtt)
            return target_vtt if target_vtt.exists() else None
        except Exception as exc:
            logging.debug("SRT->VTT failed for %s: %s", video_path.name, exc)

    if ass and ffmpeg_bin:
        try:
            if (not target_vtt.exists()) or target_vtt.stat().st_mtime < max(
                video_path.stat().st_mtime,
                ass.stat().st_mtime,
            ):
                cmd = [ffmpeg_bin, "-y", "-i", str(ass), str(target_vtt)]
                subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=ffmpeg_timeout,
                )
            return target_vtt if target_vtt.exists() else None
        except Exception as exc:
            logging.debug("ASS/SSA->VTT failed for %s: %s", video_path.name, exc)

    return None


def extract_subtitle(
    src_path: Path,
    out_mp4: Path,
    ffprobe_bin: Optional[str],
    ffmpeg_bin: Optional[str],
    target_lang: str = "chi",
    target_title: str = "Traditional",
):
    if not ffprobe_bin or not ffmpeg_bin:
        return
    try:
        probe_cmd = [
            ffprobe_bin,
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
            ffmpeg_bin,
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
        srt_to_vtt(srt_path, vtt_path)
        srt_path.unlink()
        logging.info("Extracted subtitle: %s", vtt_path.name)
    except Exception as exc:
        logging.debug("Subtitle extraction failed: %s", exc)


def load_html_template() -> str:
    try:
        return load_asset_text("index.html")
    except Exception as exc:
        logging.error("Failed to load template index.html: %s", exc)
        return (
            "<!doctype html><html><body><h1>Cat Theatre</h1>"
            "<p>Template load failed.</p></body></html>"
        )
