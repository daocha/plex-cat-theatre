#!/usr/bin/env python3
"""Shared server-side helpers for auth, config, and request path handling."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Dict

from flask import request

DEFAULT_PORT = 9245
PRIVATE_STATE_PATH = Path(__file__).with_name("movies_state.json")
AUTH_STATE_PATH = Path(__file__).with_name("movies_auth_state.json")
TRUE_VALUES = {"1", "true", "yes", "on"}
UNLOCK_MAX_ATTEMPTS = 5
UNLOCK_COOLDOWN_SECONDS = 3600
SUPPORTED_LOCALES = {"auto", "en", "zh-CN", "zh-HK", "zh-TW", "fr", "ko", "ja", "de", "th", "vi", "nl"}
LOCALE_ALIASES = {
    "zh": "zh-CN",
    "zh-hans": "zh-CN",
    "zh-sg": "zh-CN",
    "zh-my": "zh-CN",
    "zh-hant": "zh-TW",
    "zh-mo": "zh-HK",
}


def hash_passcode_sha256(passcode: str) -> str:
    return "sha256:" + hashlib.sha256((passcode or "").encode("utf-8")).hexdigest()


def verify_passcode(input_passcode: str, stored_secret: str) -> bool:
    stored = str(stored_secret or "")
    if stored.startswith("sha256:"):
        calc = hash_passcode_sha256(input_passcode)
        return hmac.compare_digest(calc, stored)
    return hmac.compare_digest(str(input_passcode or ""), stored)


def load_private_state(path: Path) -> dict:
    try:
        if not path.exists():
            return {"approved_devices": []}
        data = json.loads(path.read_text(encoding="utf-8"))
        devices = data.get("approved_devices", [])
        if not isinstance(devices, list):
            devices = []
        return {"approved_devices": [str(item) for item in devices if str(item).strip()]}
    except Exception:
        return {"approved_devices": []}


def save_private_state(path: Path, devices: set[str]):
    try:
        path.write_text(
            json.dumps(
                {"approved_devices": sorted(list(devices))},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception:
        pass


def load_auth_state(path: Path) -> dict:
    try:
        if not path.exists():
            return {"unlock_failures": {}}
        data = json.loads(path.read_text(encoding="utf-8"))
        failures = data.get("unlock_failures", {})
        if not isinstance(failures, dict):
            failures = {}
        return {"unlock_failures": failures}
    except Exception:
        return {"unlock_failures": {}}


def save_auth_state(path: Path, failures: dict):
    try:
        path.write_text(
            json.dumps({"unlock_failures": failures}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def parse_bool(value, default: str = "0") -> bool:
    raw = default if value is None else value
    return str(raw).strip().lower() in TRUE_VALUES


def extract_device_id(data: dict | None = None) -> str:
    payload = data or {}
    return str(
        request.headers.get("X-Device-Id", "")
        or request.cookies.get("movies_device_id", "")
        or payload.get("device_id", "")
        or request.args.get("device_id", "")
    ).strip()


class StripPrefixMiddleware:
    """Allow serving the same app at root or under any single-segment mount prefix."""

    APP_ROOTS = {
        "api",
        "plex",
        "video",
    "hls",
    "thumbs",
        "subtitle",
        "rescan",
        "locales",
        "movies.css",
    "movies.js",
    "movies.min.js",
    "plex.svg",
    }

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = str(environ.get("PATH_INFO", "") or "")
        script_name = str(environ.get("SCRIPT_NAME", "") or "")
        parts = [part for part in path.split("/") if part]
        if not parts:
            return self.wsgi_app(environ, start_response)

        first = parts[0]
        if first in self.APP_ROOTS:
            return self.wsgi_app(environ, start_response)

        should_strip = False
        if len(parts) == 1:
            should_strip = True
        elif parts[1] in self.APP_ROOTS:
            should_strip = True

        if should_strip:
            prefix = "/" + first
            new_path = path[len(prefix) :] or "/"
            environ = dict(environ)
            environ["SCRIPT_NAME"] = script_name + prefix
            environ["PATH_INFO"] = new_path
        return self.wsgi_app(environ, start_response)


def client_identity(data: dict | None = None) -> str:
    device_id = extract_device_id(data) or "anonymous"
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
    ip_first = str(ip).split(",", 1)[0].strip()
    return f"{device_id}|{ip_first}"


def auth_failure_info(failures: dict, identity: str) -> tuple[int, float]:
    record = failures.get(identity) or {}
    return int(record.get("count", 0)), float(record.get("locked_until", 0))


def register_unlock_failure(failures: dict, identity: str):
    now = time.time()
    count, locked_until = auth_failure_info(failures, identity)
    if locked_until > now:
        failures[identity] = {"count": count, "locked_until": locked_until}
        return
    count += 1
    if count >= UNLOCK_MAX_ATTEMPTS:
        failures[identity] = {
            "count": count,
            "locked_until": now + UNLOCK_COOLDOWN_SECONDS,
        }
    else:
        failures[identity] = {"count": count, "locked_until": 0}


def clear_unlock_failures(failures: dict, identity: str):
    failures.pop(identity, None)


def is_unlock_locked(failures: dict, identity: str) -> tuple[bool, int]:
    now = time.time()
    count, locked_until = auth_failure_info(failures, identity)
    if locked_until > now:
        return True, int(locked_until - now)
    if locked_until and locked_until <= now:
        failures.pop(identity, None)
    return False, 0


def normalize_mount_prefix(raw: str) -> str:
    prefix = str(raw or "").strip()
    if not prefix:
        return ""
    if "://" in prefix:
        try:
            prefix = urllib.parse.urlparse(prefix).path or ""
        except Exception:
            prefix = ""
    prefix = "/" + prefix.strip("/")
    return "" if prefix == "/" else prefix.rstrip("/")


def infer_mount_prefix_from_path(path: str) -> str:
    parts = [part for part in str(path or "").split("/") if part]
    if not parts:
        return ""
    first = parts[0]
    if first in StripPrefixMiddleware.APP_ROOTS:
        return ""
    if len(parts) == 1 or parts[1] in StripPrefixMiddleware.APP_ROOTS:
        return "/" + first
    return ""


def resolve_app_root() -> str:
    direct = normalize_mount_prefix(request.environ.get("SCRIPT_NAME") or request.script_root or "")
    if direct:
        return direct

    forwarded_prefix = normalize_mount_prefix(
        request.headers.get("X-Forwarded-Prefix", "")
        or request.headers.get("X-Script-Name", "")
    )
    if forwarded_prefix:
        return forwarded_prefix

    original_uri = str(
        request.headers.get("X-Original-URI", "")
        or request.headers.get("X-Rewrite-URL", "")
        or request.headers.get("X-Forwarded-Uri", "")
    ).strip()
    if original_uri:
        try:
            parsed_path = urllib.parse.urlparse(original_uri).path or original_uri
        except Exception:
            parsed_path = original_uri
        inferred = infer_mount_prefix_from_path(parsed_path)
        if inferred:
            return inferred

    referer = str(request.headers.get("Referer", "") or "").strip()
    if referer:
        try:
            ref_path = urllib.parse.urlparse(referer).path or ""
        except Exception:
            ref_path = ""
        inferred = infer_mount_prefix_from_path(ref_path)
        if inferred:
            return inferred

    return ""


def app_url(path: str) -> str:
    root = resolve_app_root()
    clean = "/" + str(path or "").lstrip("/")
    return f"{root}{clean}" if root else clean


def apply_device_cookie(resp, device_id: str = "", clear: bool = False):
    cookie_path = resolve_app_root() or "/"
    is_secure = request.is_secure or str(
        request.headers.get("X-Forwarded-Proto", "")
    ).lower() == "https"
    if clear:
        resp.delete_cookie(
            "movies_device_id",
            path=cookie_path,
            samesite="Lax",
            secure=is_secure,
        )
        return resp
    if not device_id:
        return resp
    resp.set_cookie(
        "movies_device_id",
        device_id,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        samesite="Lax",
        secure=is_secure,
        path=cookie_path,
    )
    return resp


def apply_public_image_cache(resp, max_age: int = 30 * 24 * 60 * 60):
    try:
        resp.cache_control.public = True
        resp.cache_control.max_age = int(max_age)
        resp.cache_control.immutable = True
        resp.expires = int(time.time()) + int(max_age)
    except Exception:
        pass
    return resp


def _ensure_bool_field(cfg: dict, key: str):
    if not isinstance(cfg.get(key), bool):
        raise ValueError(f"Config field '{key}' must be true or false")


def _ensure_string_field(cfg: dict, key: str):
    value = cfg.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Config field '{key}' must be a string")
    cfg[key] = value.strip()


def _normalize_string_list(value, field_name: str) -> list[str]:
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        raise ValueError(f"Config field '{field_name}' must be a string or a list of strings")
    normalized: list[str] = []
    for item in items:
        if not isinstance(item, str):
            raise ValueError(f"Config field '{field_name}' must contain only strings")
        text = item.strip()
        if text:
            normalized.append(text)
    return normalized


def normalize_locale_code(locale: str) -> str:
    raw = str(locale or "").strip()
    if not raw:
        return ""
    canonical = raw.replace("_", "-")
    if canonical in SUPPORTED_LOCALES:
        return canonical
    lower = canonical.lower()
    if lower in LOCALE_ALIASES:
        return LOCALE_ALIASES[lower]
    parts = canonical.split("-")
    if parts and parts[0].lower() == "zh":
        script = (parts[1] if len(parts) > 1 else "").lower()
        region = (parts[1] if len(parts) > 1 else (parts[2] if len(parts) > 2 else "")).lower()
        if script == "hant" or region in {"tw", "hk", "mo"}:
            return "zh-HK" if region in {"hk", "mo"} else "zh-TW"
        return "zh-CN"
    base = parts[0].lower() if parts else ""
    for code in SUPPORTED_LOCALES:
        if code.lower() == base:
            return code
    return ""


def validate_and_normalize_config(cfg: dict, path: Path) -> Dict:
    if not isinstance(cfg, dict):
        raise ValueError("Config root must be a JSON object")

    if "root" not in cfg:
        raise ValueError("Missing root in config")

    cfg["root"] = _normalize_string_list(cfg.get("root"), "root")
    cfg["private_folder"] = _normalize_string_list(cfg.get("private_folder", []), "private_folder")

    try:
        cfg["port"] = int(cfg.get("port", DEFAULT_PORT))
    except Exception as exc:
        raise ValueError("Config field 'port' must be an integer") from exc
    if not (1 <= cfg["port"] <= 65535):
        raise ValueError("Config field 'port' must be between 1 and 65535")

    _ensure_string_field(cfg, "host")
    _ensure_string_field(cfg, "private_passcode")
    _ensure_string_field(cfg, "mount_script")
    _ensure_string_field(cfg, "transcode_video_codec")

    locale = normalize_locale_code(str(cfg.get("locale", "auto") or "auto").strip())
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(
            "Config field 'locale' must be one of: "
            + ", ".join(sorted(SUPPORTED_LOCALES))
        )
    cfg["locale"] = locale

    for key in (
        "transcode",
        "on_demand_transcode",
        "on_demand_hls",
        "enable_plex_server",
        "auto_scan_on_start",
        "debug_enabled",
    ):
        _ensure_bool_field(cfg, key)

    direct_playback = cfg.get("direct_playback")
    if not isinstance(direct_playback, dict):
        raise ValueError("Config field 'direct_playback' must be an object")
    if not isinstance(direct_playback.get("enabled"), bool):
        raise ValueError("Config field 'direct_playback.enabled' must be true or false")
    direct_playback["audio_whitelist"] = _normalize_string_list(
        direct_playback.get("audio_whitelist", []),
        "direct_playback.audio_whitelist",
    )
    cfg["direct_playback"] = direct_playback

    plex = cfg.get("plex")
    if not isinstance(plex, dict):
        raise ValueError("Config field 'plex' must be an object")
    if not isinstance(plex.get("prefer_transcode"), bool):
        raise ValueError("Config field 'plex.prefer_transcode' must be true or false")
    _ensure_string_field(plex, "base_url")
    _ensure_string_field(plex, "token")
    try:
        plex["timeout_seconds"] = int(plex.get("timeout_seconds", 8))
        plex["refresh_interval_seconds"] = int(plex.get("refresh_interval_seconds", 120))
    except Exception as exc:
        raise ValueError("Plex timeout and refresh interval must be integers") from exc
    if plex["timeout_seconds"] <= 0:
        raise ValueError("Config field 'plex.timeout_seconds' must be greater than 0")
    if plex["refresh_interval_seconds"] <= 0:
        raise ValueError("Config field 'plex.refresh_interval_seconds' must be greater than 0")
    cfg["plex"] = plex

    thumbs_dir = cfg.get("thumbs_dir")
    if thumbs_dir is None:
        cfg["thumbs_dir"] = str(path.parent / "cache" / "thumbnails")
    elif not isinstance(thumbs_dir, str):
        raise ValueError("Config field 'thumbs_dir' must be a string")
    else:
        cfg["thumbs_dir"] = thumbs_dir.strip() or str(path.parent / "cache" / "thumbnails")

    return cfg


def load_config(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        cfg = json.load(handle)
    cfg.setdefault("port", DEFAULT_PORT)
    cfg.setdefault("host", "0.0.0.0")
    cfg.setdefault("private_folder", [])
    cfg.setdefault("private_passcode", "")
    cfg.setdefault("transcode", True)
    cfg.setdefault("on_demand_transcode", False)
    cfg.setdefault("on_demand_hls", False)
    cfg.setdefault("transcode_video_codec", "h264_videotoolbox")
    cfg.setdefault("enable_plex_server", False)
    cfg.setdefault("auto_scan_on_start", True)
    cfg.setdefault("debug_enabled", False)
    cfg.setdefault("mount_script", "")
    cfg.setdefault("locale", "auto")
    cfg.setdefault(
        "direct_playback",
        {
            "enabled": True,
            "audio_whitelist": ["aac", "mp3"],
        },
    )
    cfg.setdefault(
        "plex",
        {
            "base_url": "http://127.0.0.1:32400",
            "token": "",
            "timeout_seconds": 8,
            "refresh_interval_seconds": 120,
            "prefer_transcode": False,
        },
    )
    return validate_and_normalize_config(cfg, path)


def setup_logging(flush_interval_seconds: int = 60):
    from logging.handlers import MemoryHandler

    log_path = Path.home() / ".openclaw" / "logs" / "movies.launchd.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s"))

    mem_handler = MemoryHandler(capacity=10000, flushLevel=logging.ERROR, target=file_handler)
    mem_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = []
    root.addHandler(mem_handler)

    def periodic_flush():
        while True:
            time.sleep(max(1, int(flush_interval_seconds)))
            try:
                mem_handler.flush()
            except Exception:
                pass

    threading.Thread(target=periodic_flush, daemon=True).start()
    return mem_handler
