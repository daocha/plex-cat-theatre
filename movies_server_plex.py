#!/usr/bin/env python3
"""Plex integration adapter for movies server.

This module overlays Plex metadata/streaming on top of local catalog entries.
When disabled or unavailable, caller should fall back to local behavior.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional
import struct


class PlexAdapter:
    def __init__(self, enabled: bool, plex_cfg: dict | None = None):
        self.enabled = bool(enabled)
        cfg = plex_cfg or {}
        self.base_url = str(cfg.get("base_url", "http://127.0.0.1:32400")).rstrip("/")
        self.token = str(cfg.get("token", "")).strip()
        self.timeout = int(cfg.get("timeout_seconds", 8) or 8)
        self.prefer_transcode = bool(cfg.get("prefer_transcode", False))

        self._last_refresh = 0.0
        self._refresh_interval = int(cfg.get("refresh_interval_seconds", 120) or 120)
        self._items_by_file: Dict[str, dict] = {}
        self._items_by_name_size: Dict[tuple[str, int], dict] = {}
        self._by_video_id: Dict[str, dict] = {}
        self._catalog_video_map: Dict[str, Path] = {}
        self._poster_ar_by_thumb: Dict[str, float] = {}
        self._last_error: Optional[str] = None
        self._refreshing = False
        self._lock = threading.Lock()

    def _normalize_match_text(self, value: str) -> str:
        return unicodedata.normalize("NFC", str(value or "")).casefold()

    def _normalize_match_path(self, value: str) -> str:
        return self._normalize_match_text(str(Path(value).expanduser()))

    def status(self) -> dict:
        return {
            "enabled": self.enabled,
            "base_url": self.base_url,
            "has_token": bool(self.token),
            "last_refresh": self._last_refresh,
            "last_error": self._last_error,
            "item_count": len(self._items_by_file),
            "refreshing": self._refreshing,
        }

    def maybe_refresh(self):
        if not self.enabled:
            return
        now = time.time()
        if self._items_by_file and (now - self._last_refresh) < self._refresh_interval:
            return

        with self._lock:
            if self._refreshing:
                return
            self._refreshing = True

        def _run_refresh():
            try:
                self.refresh()
            finally:
                with self._lock:
                    self._refreshing = False

        threading.Thread(target=_run_refresh, daemon=True).start()

    def refresh(self):
        if not self.enabled:
            return
        try:
            sections_xml = self._get_xml("/library/sections")
            section_keys = [d.attrib.get("key") for d in sections_xml.findall(".//Directory") if d.attrib.get("key")]

            items: Dict[str, dict] = {}
            items_by_name_size: Dict[tuple[str, int], dict] = {}

            def collect_videos(sec_xml: ET.Element):
                for video in sec_xml.findall(".//Video"):
                    title = video.attrib.get("title", "")
                    rating_key = video.attrib.get("ratingKey", "")
                    thumb = video.attrib.get("thumb", "")

                    media = video.find("Media")
                    if media is None:
                        continue
                    part = media.find("Part")
                    if part is None:
                        continue

                    file_path = part.attrib.get("file", "")
                    part_key = part.attrib.get("key", "")
                    if not file_path:
                        continue

                    subtitle_key = self._pick_subtitle_key(part)
                    norm_file = self._normalize_match_path(file_path)
                    file_name = self._normalize_match_text(Path(file_path).name)
                    try:
                        part_size = int(part.attrib.get("size", "0") or 0)
                    except Exception:
                        part_size = 0
                    item = {
                        "title": title,
                        "rating_key": rating_key,
                        "thumb": thumb,
                        "part_key": part_key,
                        "subtitle_key": subtitle_key,
                        "size": part_size,
                        "file_name": file_name,
                        "poster_ar": 0.0,
                    }
                    items[norm_file] = item
                    if part_size > 0:
                        items_by_name_size[(file_name, part_size)] = item

            for skey in section_keys:
                sec_xml = self._get_xml(f"/library/sections/{skey}/all")
                collect_videos(sec_xml)

            self._items_by_file = items
            self._items_by_name_size = items_by_name_size
            self._last_refresh = time.time()
            self._last_error = None
        except Exception as e:
            self._last_error = str(e)
            logging.warning("Plex refresh failed: %s", e)

    def _pick_subtitle_key(self, part) -> str:
        text_codecs = {"srt", "vtt", "webvtt", "ass", "ssa", "subrip"}
        chinese_codes = {"zh", "zho", "chi", "cmn", "zh-cn", "zh-tw", "chs", "cht"}
        chinese_hints = {
            "chinese", "mandarin", "traditional chinese", "simplified chinese",
            "中文", "國語", "国语", "漢語", "汉语", "繁中", "简中", "簡中",
        }
        best_text = ""
        best_any = ""
        for st in part.findall("Stream"):
            if st.attrib.get("streamType") != "3":
                continue
            s_key = str(st.attrib.get("key", "") or "").strip()
            if not s_key:
                continue
            codec = str(st.attrib.get("codec", "") or "").lower()
            lang = str(st.attrib.get("languageCode", "") or st.attrib.get("language", "") or "").lower()
            title = " ".join(
                str(st.attrib.get(k, "") or "") for k in ("title", "displayTitle", "extendedDisplayTitle")
            ).lower()
            is_text = codec in text_codecs
            is_chinese = any(code and code in lang for code in chinese_codes) or any(h in title for h in chinese_hints)
            if is_text and is_chinese:
                return s_key
            if is_text and not best_text:
                best_text = s_key
            if not best_any:
                best_any = s_key
        return best_text or best_any

    def bind_catalog(self, video_map: Dict[str, Path]):
        """Map catalog video_id -> Plex item (if any)."""
        self._catalog_video_map = dict(video_map)
        self.maybe_refresh()
        mapping: Dict[str, dict] = {}
        for vid, p in video_map.items():
            key = self._normalize_match_path(str(p))
            item = self._items_by_file.get(key)
            if not item:
                try:
                    sz = int(p.stat().st_size)
                except Exception:
                    sz = 0
                if sz > 0:
                    item = self._items_by_name_size.get((self._normalize_match_text(p.name), sz))
            if item:
                if item.get("thumb") and not float(item.get("poster_ar") or 0.0):
                    item["poster_ar"] = self._resolve_poster_ar(item)
                mapping[vid] = item
        self._by_video_id = mapping

    def overlay_item(self, video_id: str, local_item: dict) -> dict:
        """Return merged item, keeping local playback as primary.

        Playback order is handled by frontend:
        1) direct local playback
        2) plex playback (if matched)
        3) local soft-decode fallback (if provided)
        """
        item = dict(local_item)
        p = self._by_video_id.get(video_id)
        if not p:
            return item

        if p.get("title"):
            item["name"] = p["title"]

        item["plex_stream_url"] = f"/plex/video/{video_id}.m3u8"

        if p.get("thumb"):
            item["thumb_url"] = f"/plex/poster/{video_id}.jpg?w=360&h=540"
            poster_ar = float(p.get("poster_ar") or 0.0)
            if poster_ar > 0:
                item["ar"] = poster_ar

        if p.get("subtitle_key"):
            item["subtitle_url"] = f"/plex/subtitle/{video_id}.vtt"

        return item

    def _build_url(self, path: str, query: dict | None = None) -> str:
        q = dict(query or {})
        if self.token:
            q["X-Plex-Token"] = self.token
        return f"{self.base_url}{path}" + ("?" + urllib.parse.urlencode(q) if q else "")

    def _open(self, path: str, query: dict | None = None, headers: dict | None = None):
        req = urllib.request.Request(self._build_url(path, query), headers=headers or {})
        return urllib.request.urlopen(req, timeout=self.timeout)

    def _get_xml(self, path: str, query: dict | None = None) -> ET.Element:
        with self._open(path, query, headers={"Accept": "application/xml"}) as resp:
            body = resp.read()
        return ET.fromstring(body)

    def _resolve_item(self, video_id: str):
        p = self._by_video_id.get(video_id)
        if p:
            return p
        vp = self._catalog_video_map.get(video_id)
        if not vp:
            return None
        key = self._normalize_match_path(str(vp))
        p = self._items_by_file.get(key)
        if p:
            self._by_video_id[video_id] = p
            return p
        try:
            sz = int(vp.stat().st_size)
        except Exception:
            sz = 0
        if sz > 0:
            p = self._items_by_name_size.get((self._normalize_match_text(vp.name), sz))
            if p:
                self._by_video_id[video_id] = p
                return p
        return None

    def resolve_part_url(self, video_id: str) -> str | None:
        p = self._resolve_item(video_id)
        if not p or not p.get("part_key"):
            return None
        return self._build_url(p["part_key"])

    def build_transcode_playlist_url(self, video_id: str, session_id: str | None = None) -> str | None:
        p = self._resolve_item(video_id)
        rating_key = str((p or {}).get("rating_key", "")).strip()
        if not rating_key:
            return None

        session = session_id or f"miranda-{uuid.uuid4().hex[:12]}"
        params = {
            "path": self._build_url(f"/library/metadata/{rating_key}"),
            "mediaIndex": "0",
            "partIndex": "0",
            "protocol": "hls",
            "directPlay": "0",
            "directStream": "1",
            "fastSeek": "1",
            "audioCodec": "aac",
            "maxAudioChannels": "2",
            "session": session,
            "X-Plex-Product": "MirandaMovies",
            "X-Plex-Client-Identifier": "miranda-movies-web",
            "X-Plex-Platform": "Chrome",
            "X-Plex-Platform-Version": "1.0",
            "X-Plex-Device": "Web",
            "X-Plex-Device-Name": "Miranda Browser",
        }
        return self._build_url("/video/:/transcode/universal/start.m3u8", params)

    def open_absolute(self, absolute_url: str, headers: dict | None = None):
        req = urllib.request.Request(absolute_url, headers=headers or {})
        return urllib.request.urlopen(req, timeout=self.timeout)

    def proxy_video(self, video_id: str, range_header: str | None = None):
        p = self._resolve_item(video_id)
        if not p or not p.get("part_key"):
            return None, "not_found"

        path = p["part_key"]
        headers = {}
        if range_header:
            headers["Range"] = range_header
        try:
            resp = self._open(path, headers=headers)
            return resp, None
        except Exception as e:
            return None, str(e)

    def _sniff_image_size(self, head: bytes) -> tuple[int, int] | None:
        try:
            if head.startswith(b"\x89PNG\r\n\x1a\n") and len(head) >= 24:
                w, h = struct.unpack(">II", head[16:24])
                if w > 0 and h > 0:
                    return w, h
            if head.startswith(b"\xff\xd8"):
                i = 2
                n = len(head)
                while i + 9 < n:
                    if head[i] != 0xFF:
                        i += 1
                        continue
                    marker = head[i + 1]
                    if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                        block_len = struct.unpack(">H", head[i + 2:i + 4])[0]
                        if i + 2 + block_len <= n and i + 9 <= n:
                            h = struct.unpack(">H", head[i + 5:i + 7])[0]
                            w = struct.unpack(">H", head[i + 7:i + 9])[0]
                            if w > 0 and h > 0:
                                return w, h
                        break
                    if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
                        i += 2
                        continue
                    if i + 4 > n:
                        break
                    block_len = struct.unpack(">H", head[i + 2:i + 4])[0]
                    if block_len < 2:
                        break
                    i += 2 + block_len
        except Exception:
            return None
        return None

    def _resolve_poster_ar(self, item: dict) -> float:
        thumb = str((item or {}).get("thumb", "") or "").strip()
        if not thumb:
            return 0.0
        cached = float(self._poster_ar_by_thumb.get(thumb, 0.0) or 0.0)
        if cached > 0:
            return cached
        try:
            with self._open(thumb, headers={"Accept": "image/*"}) as resp:
                head = resp.read(65536)
            size = self._sniff_image_size(head)
            if not size:
                return 0.0
            w, h = size
            if w > 0 and h > 0:
                ar = float(w) / float(h)
                self._poster_ar_by_thumb[thumb] = ar
                return ar
        except Exception:
            return 0.0
        return 0.0

    def proxy_binary_by_kind(self, video_id: str, kind: str):
        p = self._resolve_item(video_id)
        if not p:
            return None, "not_found"

        if kind == "poster":
            k = p.get("thumb")
        elif kind == "subtitle":
            k = p.get("subtitle_key")
        else:
            return None, "invalid_kind"

        if not k:
            return None, "not_found"

        try:
            resp = self._open(k)
            return resp, None
        except Exception as e:
            return None, str(e)

    def proxy_resized_poster(self, video_id: str, width: int, height: int):
        p = self._resolve_item(video_id)
        if not p:
            return None, "not_found"
        thumb = str(p.get("thumb", "") or "").strip()
        if not thumb:
            return None, "not_found"
        width = max(80, min(int(width or 0), 640))
        height = max(120, min(int(height or 0), 960))
        inner_thumb = thumb
        if self.token:
            sep = "&" if "?" in inner_thumb else "?"
            inner_thumb = f"{inner_thumb}{sep}{urllib.parse.urlencode({'X-Plex-Token': self.token})}"
        query = {
            "width": str(width),
            "height": str(height),
            "minSize": "0",
            "upscale": "0",
            "url": inner_thumb,
        }
        try:
            resp = self._open("/photo/:/transcode", query=query, headers={"Accept": "image/*"})
            return resp, None
        except Exception as e:
            logging.debug("Plex resized poster request failed for %s: %s", video_id, e)
            return self.proxy_binary_by_kind(video_id, "poster")
