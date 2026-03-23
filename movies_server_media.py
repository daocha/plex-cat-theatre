#!/usr/bin/env python3
"""Media-path, Plex-HLS, and subtitle normalization helpers."""

from __future__ import annotations

import logging
import re
import shlex
import subprocess
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple


def build_plex_hls_proxy_url(
    target_url: str,
    mount_root: str = "",
    relative_mode: str = "absolute",
) -> str:
    clean_target = str(target_url or "").strip()
    if relative_mode == "from_video":
        proxy_path = "../hls/proxy?"
    elif relative_mode == "from_proxy":
        proxy_path = "?"
    else:
        proxy_path = (
            (mount_root.rstrip("/") + "/plex/hls/proxy")
            if mount_root
            else "/plex/hls/proxy"
        ) + "?"
    query = urllib.parse.urlencode({"u": clean_target, "root": mount_root or ""})
    return proxy_path + query


def extract_video_id_from_referer(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        path = urllib.parse.urlparse(raw).path
    except Exception:
        path = raw
    match = re.search(r"/plex/video/([^/?#]+?)(?:\.m3u8)?$", path)
    if match:
        return urllib.parse.unquote(match.group(1))
    match = re.search(r"/video/([^/?#]+)$", path)
    if match:
        return urllib.parse.unquote(match.group(1))
    return ""


def run_mount_script(command_text: str) -> bool:
    clean_command = str(command_text or "").strip()
    if not clean_command:
        return False
    try:
        command = shlex.split(clean_command)
        if not command:
            return False
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=45,
        )
        if completed.returncode == 0:
            logging.info("Mount script succeeded: %s", clean_command)
            return True
        logging.warning(
            "Mount script failed: rc=%d stdout=%r stderr=%r",
            completed.returncode,
            completed.stdout.strip(),
            completed.stderr.strip(),
        )
    except Exception as exc:
        logging.warning("Mount script execution failed: %s", exc)
    return False


def ensure_media_path_ready(
    media_path: Optional[Path],
    mount_script: str,
    localized_message_fn,
) -> Tuple[Optional[Path], Optional[Tuple[str, int]]]:
    if media_path and media_path.exists():
        return media_path, None
    folder = media_path.parent if media_path else None
    folder_missing = bool(folder and not folder.exists())
    if folder_missing and str(mount_script or "").strip():
        logging.info("Media folder missing, attempting mount recovery: %s", folder)
        run_mount_script(mount_script)
        if media_path and media_path.exists():
            return media_path, None
        folder_missing = bool(folder and not folder.exists())
    if folder_missing:
        return None, (localized_message_fn("media_folder_not_mounted"), 404)
    return None, (localized_message_fn("file_not_found"), 404)


def ensure_media_id_ready(
    video_map,
    video_id: str,
    mount_script: str,
    localized_message_fn,
) -> Tuple[Optional[Path], Optional[Tuple[str, int]]]:
    return ensure_media_path_ready(
        video_map.get(urllib.parse.unquote(video_id)),
        mount_script,
        localized_message_fn,
    )


def _ass_time_to_vtt(value: str) -> str:
    raw = str(value or "").strip()
    match = re.match(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.](\d{1,2})", raw)
    if not match:
        return "00:00:00.000"
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    centis = int(match.group(4) or 0)
    millis = centis * 10
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def _strip_ass_text_markup(text: str) -> str:
    out = str(text or "")
    out = out.replace("\\N", "\n").replace("\\n", "\n").replace("\\h", " ")
    out = re.sub(r"\{[^}]*\}", "", out)
    return out.strip()


def normalize_subtitle_to_vtt(body: bytes, content_type: str = "") -> bytes:
    raw = body or b""
    text = raw.decode("utf-8", errors="ignore").lstrip("\ufeff")
    if not text.strip():
        return b"WEBVTT\n\n"

    if text.lstrip().startswith("WEBVTT"):
        return text.encode("utf-8")

    lowered_ctype = str(content_type or "").lower()
    lowered_text = text.lower()

    if "[script info]" in lowered_text or "\ndialogue:" in lowered_text or lowered_ctype.endswith("/x-ass"):
        cues = ["WEBVTT", ""]
        for line in text.splitlines():
            if not line.startswith("Dialogue:"):
                continue
            payload = line.split(":", 1)[1].lstrip()
            parts = payload.split(",", 9)
            if len(parts) < 10:
                continue
            start = _ass_time_to_vtt(parts[1])
            end = _ass_time_to_vtt(parts[2])
            cue_text = _strip_ass_text_markup(parts[9])
            if not cue_text:
                continue
            cues.extend([f"{start} --> {end}", cue_text, ""])
        return ("\n".join(cues).strip() + "\n").encode("utf-8")

    text = re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", text)
    if not text.lstrip().startswith("WEBVTT"):
        text = "WEBVTT\n\n" + text
    return text.encode("utf-8")
