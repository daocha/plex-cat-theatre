#!/usr/bin/env python3
"""Server-side locale normalization and message loading."""

from __future__ import annotations

import json
from pathlib import Path

from flask import jsonify, request

from movies_resources import load_asset_text

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = {
    "en",
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "fr",
    "ko",
    "ja",
    "de",
    "th",
    "vi",
    "nl",
}


class ServerLocalizer:
    def __init__(self, locale_dir: Path | None = None):
        self.locale_dir = locale_dir
        self._cache: dict[str, dict[str, str]] = {}

    def normalize_locale_code(self, value: str) -> str:
        raw = str(value or "").strip().replace("_", "-")
        if not raw:
            return ""
        if raw in SUPPORTED_LOCALES:
            return raw
        lowered = raw.lower()
        if lowered in {"zh", "zh-hans", "zh-sg", "zh-my"}:
            return "zh-CN"
        if lowered in {"zh-hant"}:
            return "zh-TW"
        parts = raw.split("-")
        base = parts[0].lower()
        if base == "zh":
            region = (parts[1] if len(parts) > 1 else "").lower()
            if region in {"hk", "mo"}:
                return "zh-HK"
            if region in {"tw", "hant"}:
                return "zh-TW"
            return "zh-CN"
        for supported in SUPPORTED_LOCALES:
            if supported.lower() == base:
                return supported
        return ""

    def request_locale(self, configured_locale: str = "auto") -> str:
        requested = self.normalize_locale_code(
            str(request.headers.get("X-UI-Locale", "") or "")
        )
        if requested:
            return requested
        cookie_locale = self.normalize_locale_code(
            str(request.cookies.get("movies_ui_locale", "") or "")
        )
        if cookie_locale:
            return cookie_locale
        configured = self.normalize_locale_code(str(configured_locale or ""))
        if configured and configured != "auto":
            return configured
        accept = str(request.headers.get("Accept-Language", "") or "")
        for chunk in accept.split(","):
            code = self.normalize_locale_code(chunk.split(";", 1)[0])
            if code:
                return code
        return DEFAULT_LOCALE

    def load_bundle(self, locale: str) -> dict[str, str]:
        normalized = self.normalize_locale_code(locale) or DEFAULT_LOCALE
        cached = self._cache.get(normalized)
        if cached is not None:
            return cached
        try:
            if self.locale_dir is not None:
                bundle = json.loads((self.locale_dir / f"{normalized}.json").read_text(encoding="utf-8"))
            else:
                bundle = json.loads(load_asset_text(f"{normalized}.json", subdir="server_locales"))
        except Exception:
            if normalized != DEFAULT_LOCALE:
                bundle = self.load_bundle(DEFAULT_LOCALE)
            else:
                bundle = {}
        self._cache[normalized] = bundle
        return bundle

    def localized_message(self, configured_locale: str, message_key: str) -> str:
        locale = self.request_locale(configured_locale)
        table = self.load_bundle(locale)
        fallback = self.load_bundle(DEFAULT_LOCALE)
        return table.get(message_key, fallback.get(message_key, message_key))

    def localized_json_error(
        self,
        configured_locale: str,
        error_key: str,
        status: int,
        **extra,
    ):
        payload = {
            "error": error_key,
            "message": self.localized_message(configured_locale, error_key),
        }
        payload.update(extra)
        return jsonify(payload), status
