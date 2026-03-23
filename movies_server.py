#!/usr/bin/env python3
"""Movies server entrypoint and Flask route wiring."""

from __future__ import annotations

import argparse
import logging
import math
import mimetypes
import re
import subprocess
import threading
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict

from flask import Flask, Response, abort, jsonify, redirect, request, send_file
from waitress import serve

from movies_catalog import (
    Catalog,
    FFMPEG,
    SOURCE_EXTENSIONS,
    load_html_template,
)
from movies_resources import load_asset_bytes
from movies_server_core import (
    AUTH_STATE_PATH,
    DEFAULT_PORT,
    PRIVATE_STATE_PATH,
    StripPrefixMiddleware,
    app_url,
    apply_device_cookie,
    apply_public_image_cache,
    clear_unlock_failures,
    client_identity,
    extract_device_id,
    is_unlock_locked,
    load_auth_state,
    load_config,
    load_private_state,
    normalize_mount_prefix,
    parse_bool,
    register_unlock_failure,
    resolve_app_root,
    save_auth_state,
    save_private_state,
    setup_logging,
    verify_passcode,
)
from movies_server_auth import (
    can_access_private as auth_can_access_private,
    require_media_access as auth_require_media_access,
    resolve_private_visibility as auth_resolve_private_visibility,
)
from movies_server_locale import SUPPORTED_LOCALES, ServerLocalizer
from movies_server_media import (
    build_plex_hls_proxy_url,
    ensure_media_id_ready as media_ensure_media_id_ready,
    ensure_media_path_ready as media_ensure_media_path_ready,
    extract_video_id_from_referer,
    normalize_subtitle_to_vtt,
)
from movies_server_overlay import PlexOverlayCoordinator
from movies_server_plex import PlexAdapter

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.wsgi_app = StripPrefixMiddleware(app.wsgi_app)

catalog = None
plex_adapter: PlexAdapter | None = None
APP_INSTANCE = None
ON_DEMAND_TRANSCODE = False
HWACCEL_CODEC = "h264_videotoolbox"
cfg_runtime = {
    "on_demand_hls": False,
    "direct_playback_enabled": True,
    "direct_audio_whitelist": {"aac", "mp3"},
    "debug_enabled": False,
    "mount_script": "",
    "plex_enabled": False,
    "plex_base_url": "",
    "locale": "auto",
}
APPROVED_PRIVATE_DEVICES: set[str] = set()
PRIVATE_STATE_LOCK = threading.Lock()
AUTH_STATE_LOCK = threading.Lock()
AUTH_FAILURES: dict = {}
localizer = ServerLocalizer()
plex_overlay = PlexOverlayCoordinator(min_interval=3.0)


@app.after_request
def add_csp_headers(resp):
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self' data: blob:; img-src 'self' data: blob:; media-src 'self' data: blob:; "
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "connect-src 'self' data: blob: https://cdn.jsdelivr.net; worker-src 'self' blob:;",
    )
    return resp


@app.after_request
def persist_device_cookie(resp):
    device_id = extract_device_id()
    if device_id:
        resp = apply_device_cookie(resp, device_id=device_id)
    return resp


def can_access_private(device_id: str, passcode: str = "") -> bool:
    return auth_can_access_private(
        catalog,
        APPROVED_PRIVATE_DEVICES,
        verify_passcode,
        device_id,
        passcode=passcode,
    )


def resolve_private_visibility() -> tuple[bool, bool]:
    return auth_resolve_private_visibility(
        catalog,
        APPROVED_PRIVATE_DEVICES,
        verify_passcode,
        extract_device_id,
    )


def localized_message(message_key: str) -> str:
    return localizer.localized_message(cfg_runtime.get("locale", "auto"), message_key)


def localized_json_error(error_key: str, status: int, **extra):
    return localizer.localized_json_error(
        cfg_runtime.get("locale", "auto"),
        error_key,
        status,
        **extra,
    )


def require_media_access(video_id: str) -> tuple[bool, tuple]:
    return auth_require_media_access(
        catalog,
        APPROVED_PRIVATE_DEVICES,
        verify_passcode,
        extract_device_id,
        localized_json_error,
        video_id,
    )


def ensure_media_path_ready(media_path: Path | None) -> tuple[Path | None, tuple[str, int] | None]:
    return media_ensure_media_path_ready(
        media_path,
        str(cfg_runtime.get("mount_script", "") or "").strip(),
        localized_message,
    )


def ensure_media_id_ready(video_id: str) -> tuple[Path | None, tuple[str, int] | None]:
    return media_ensure_media_id_ready(
        catalog.video_map,
        video_id,
        str(cfg_runtime.get("mount_script", "") or "").strip(),
        localized_message,
    )


def ensure_plex_catalog_binding(force_refresh: bool = False):
    plex_overlay._ensure_binding(plex_adapter, catalog, force_refresh=force_refresh)


def schedule_plex_overlay_refresh(
    persist_index: bool = False,
    force_refresh: bool = False,
):
    plex_overlay.schedule(
        plex_adapter,
        catalog,
        persist_index=persist_index,
        force_refresh=force_refresh,
    )


@app.route("/")
def index():
    return Response(load_html_template(), mimetype="text/html; charset=utf-8")


@app.route("/movies.css")
@app.route("/movies_server.css")
def static_movies_css():
    return Response(
        load_asset_bytes("movies.css"),
        mimetype="text/css; charset=utf-8",
    )


@app.route("/movies.js")
@app.route("/movies_server.js")
def static_movies_js():
    return Response(
        load_asset_bytes("movies.js"),
        mimetype="application/javascript; charset=utf-8",
    )


@app.route("/movies.min.js")
@app.route("/movies_server.min.js")
def static_movies_min_js():
    return Response(
        load_asset_bytes("movies.min.js"),
        mimetype="application/javascript; charset=utf-8",
    )


@app.route("/locales/<path:fname>")
def static_locale_js(fname):
    safe_name = Path(fname).name
    try:
        payload = load_asset_bytes(safe_name, subdir="locales")
    except FileNotFoundError:
        abort(404)
    return Response(
        payload,
        mimetype="application/javascript; charset=utf-8",
    )


@app.route("/plex.svg")
def static_plex_logo():
    return Response(
        load_asset_bytes("plex.svg"),
        mimetype="image/svg+xml",
    )


@app.route("/api/private/unlock", methods=["POST"])
def api_private_unlock():
    data = request.get_json(silent=True) or {}
    passcode = str(
        data.get("passcode", "")
        or request.form.get("passcode", "")
        or request.args.get("passcode", "")
    ).strip()
    device_id = extract_device_id(data)
    if not device_id:
        return localized_json_error("missing_device_id", 400)

    identity = client_identity(data)
    with AUTH_STATE_LOCK:
        locked, retry_after = is_unlock_locked(AUTH_FAILURES, identity)
        if locked:
            return localized_json_error(
                "too_many_attempts",
                429,
                retry_after=retry_after,
            )

    if not verify_passcode(passcode, catalog.private_passcode):
        with AUTH_STATE_LOCK:
            register_unlock_failure(AUTH_FAILURES, identity)
            save_auth_state(AUTH_STATE_PATH, AUTH_FAILURES)
        return localized_json_error("invalid_passcode", 403)

    with AUTH_STATE_LOCK:
        clear_unlock_failures(AUTH_FAILURES, identity)
        save_auth_state(AUTH_STATE_PATH, AUTH_FAILURES)

    with PRIVATE_STATE_LOCK:
        APPROVED_PRIVATE_DEVICES.add(device_id)
        save_private_state(PRIVATE_STATE_PATH, APPROVED_PRIVATE_DEVICES)
    return apply_device_cookie(jsonify({"ok": True}), device_id=device_id)


@app.route("/api/private/lock", methods=["POST"])
def api_private_lock():
    data = request.get_json(silent=True) or {}
    device_id = extract_device_id(data)
    with PRIVATE_STATE_LOCK:
        if device_id:
            APPROVED_PRIVATE_DEVICES.discard(device_id)
        save_private_state(PRIVATE_STATE_PATH, APPROVED_PRIVATE_DEVICES)
    return apply_device_cookie(jsonify({"ok": True}), clear=True)


def build_video_response_item(item: dict) -> dict:
    response_item = dict(item)
    if plex_adapter and plex_adapter.enabled:
        try:
            response_item = plex_adapter.overlay_item(
                str(response_item.get("id", "")),
                response_item,
            )
        except Exception:
            pass
    video_path = catalog.video_map.get(response_item.get("id", ""))
    suffix = video_path.suffix.lower() if video_path else ""
    if (
        ON_DEMAND_TRANSCODE
        and cfg_runtime.get("on_demand_hls", False)
        and suffix in SOURCE_EXTENSIONS
    ):
        response_item["stream_url"] = f"/hls/{response_item['id']}/index.m3u8"
        response_item["desktop_stream_url"] = f"/video/{response_item['id']}?fmp4=1"
    else:
        response_item["stream_url"] = response_item.get("video_url")
        response_item["desktop_stream_url"] = response_item.get("stream_url")

    if ON_DEMAND_TRANSCODE and suffix in SOURCE_EXTENSIONS:
        response_item["soft_stream_url"] = f"/video/{response_item['id']}?fmp4=1"

    audio_codes = []
    for codec in response_item.get("audio_codecs", []):
        normalized = str(codec or "").strip().lower()
        if normalized:
            audio_codes.append(normalized)
    response_item["audio_codecs"] = audio_codes
    whitelist = cfg_runtime.get("direct_audio_whitelist", set()) or set()
    direct_enabled = bool(cfg_runtime.get("direct_playback_enabled", True))
    response_item["direct_play_safe"] = (
        direct_enabled and bool(audio_codes) and whitelist.issuperset(audio_codes)
    )

    return response_item


@app.route("/api/videos")
def api_videos():
    allow_private, _authorized = resolve_private_visibility()
    items = catalog.list(include_private=allow_private, allow_approved=allow_private)

    folder = str(request.args.get("folder", "") or "").strip()
    keyword = str(request.args.get("q", "") or "").strip().lower()
    if folder:
        items = [item for item in items if str(item.get("folder", "")) == folder]
    if keyword:
        items = [
            item for item in items if keyword in str(item.get("name", "")).lower()
        ]

    limit_raw = request.args.get("limit")
    offset_raw = request.args.get("offset", "0")
    use_page = bool(limit_raw)
    if use_page:
        try:
            limit = max(1, min(500, int(limit_raw)))
        except Exception:
            limit = 200
        try:
            offset = max(0, int(offset_raw))
        except Exception:
            offset = 0
        total = len(items)
        items = items[offset : offset + limit]

    if plex_adapter and plex_adapter.enabled:
        try:
            plex_adapter.bind_catalog(catalog.video_map)
        except Exception:
            pass

    out = [build_video_response_item(item) for item in items]

    if use_page:
        return jsonify({"items": out, "total": total, "offset": offset, "limit": limit})
    return jsonify(out)


@app.route("/api/videos/count")
def api_videos_count():
    allow_private, _authorized = resolve_private_visibility()
    items = catalog.list(include_private=allow_private, allow_approved=allow_private)
    folder = str(request.args.get("folder", "") or "").strip()
    keyword = str(request.args.get("q", "") or "").strip().lower()
    if folder:
        items = [item for item in items if str(item.get("folder", "")) == folder]
    if keyword:
        items = [
            item for item in items if keyword in str(item.get("name", "")).lower()
        ]
    return jsonify({"total": len(items)})


@app.route("/api/folders")
def api_folders():
    allow_private, _authorized = resolve_private_visibility()
    items = catalog.list(include_private=allow_private, allow_approved=allow_private)
    visible_folders = sorted(
        {str(item.get("folder", "")) for item in items if str(item.get("folder", "")).strip()}
    )

    all_items = catalog.list(include_private=True, allow_approved=True)
    folder_private_map: dict[str, bool] = {}
    for item in all_items:
        folder_name = str(item.get("folder", "")).strip()
        if not folder_name:
            continue
        is_private = catalog.is_private_id(str(item.get("id", "")))
        folder_private_map[folder_name] = bool(
            folder_private_map.get(folder_name, False) or is_private
        )

    visible_set = set(visible_folders)
    folders_struct = [
        {
            "name": folder_name,
            "private": bool(folder_private_map.get(folder_name, False)),
            "visible": folder_name in visible_set,
        }
        for folder_name in sorted(folder_private_map.keys())
    ]

    return jsonify(
        {
            "folders": visible_folders,
            "folders_struct": folders_struct,
            "total": len(visible_folders),
            "total_all": len(folders_struct),
        }
    )


@app.route("/api/status")
def api_status():
    status = catalog.status()
    device_id = extract_device_id()
    status["private_authorized"] = bool(
        device_id and device_id in APPROVED_PRIVATE_DEVICES
    )
    if plex_adapter:
        status["plex"] = plex_adapter.status()
    return jsonify(status)


@app.route("/api/config")
def api_config():
    whitelist = cfg_runtime.get("direct_audio_whitelist", set()) or set()
    return jsonify(
        {
            "debug_enabled": bool(cfg_runtime.get("debug_enabled", False)),
            "direct_playback_enabled": bool(
                cfg_runtime.get("direct_playback_enabled", True)
            ),
            "direct_audio_whitelist": sorted(whitelist),
            "plex_enabled": bool(cfg_runtime.get("plex_enabled", False)),
            "plex_base_url": str(cfg_runtime.get("plex_base_url", "") or "").strip(),
            "locale": str(cfg_runtime.get("locale", "auto") or "auto"),
            "supported_locales": sorted(SUPPORTED_LOCALES),
        }
    )


@app.route("/rescan")
def rescan():
    force_full = parse_bool(request.args.get("full", "0"))
    with catalog._lock:
        if catalog.is_scanning:
            return jsonify(
                {
                    "ok": False,
                    "reason": "scan_in_progress",
                    "message": localized_message("scan_in_progress"),
                }
            ), 202
        catalog.is_scanning = True

    def reload_and_scan():
        try:
            if APP_INSTANCE:
                APP_INSTANCE.reload_from_disk()
            if force_full:
                catalog.invalidate_scan_state()
            catalog.scan()
            schedule_plex_overlay_refresh(persist_index=True, force_refresh=True)
        except Exception as exc:
            try:
                with catalog._lock:
                    catalog.is_scanning = False
            except Exception:
                pass
            logging.warning("Background rescan failed: %s", exc)
    logging.info(
        "Start scanning directories... mode=%s",
        "full" if force_full else "incremental",
    )
    threading.Thread(target=reload_and_scan, daemon=True).start()
    return jsonify({"ok": True, "started": True, "mode": "full" if force_full else "incremental"})


@app.route("/thumbs/placeholder.jpg")
@app.route("/<prefix>/thumbs/placeholder.jpg")
def thumb_placeholder(prefix=None):
    svg = (
        b"<svg xmlns='http://www.w3.org/2000/svg' width='512' height='288'>"
        b"<rect width='100%' height='100%' fill='#1c1d27'/>"
        b"<text x='50%' y='50%' fill='#8f93ad' dominant-baseline='middle' "
        b"text-anchor='middle' font-size='28'>Cat Theatre</text></svg>"
    )
    return apply_public_image_cache(
        Response(svg, mimetype="image/svg+xml"),
        max_age=7 * 24 * 60 * 60,
    )


@app.route("/thumbs/prev/<vid>/<fname>")
@app.route("/<prefix>/thumbs/prev/<vid>/<fname>")
def thumb_preview(vid, fname, prefix=None):
    preview_dir = catalog.preview_dir_map.get(urllib.parse.unquote(vid))
    if preview_dir:
        preview_path = preview_dir / urllib.parse.unquote(fname)
        if preview_path.exists():
            resp = send_file(
                preview_path,
                mimetype="image/jpeg",
                max_age=30 * 24 * 60 * 60,
            )
            return apply_public_image_cache(resp)
    return thumb_placeholder()


@app.route("/thumbs/<tid>.jpg")
@app.route("/<prefix>/thumbs/<tid>.jpg")
def thumb(tid, prefix=None):
    thumb_path = catalog.thumb_map.get(tid)
    if thumb_path and thumb_path.exists():
        resp = send_file(
            thumb_path,
            mimetype="image/jpeg",
            max_age=30 * 24 * 60 * 60,
        )
        return apply_public_image_cache(resp)
    return thumb_placeholder()


@app.route("/subtitle/<sid>.vtt")
def subtitle(sid):
    ok, deny = require_media_access(urllib.parse.unquote(sid))
    if not ok:
        return deny
    subtitle_path = catalog.subtitle_map.get(urllib.parse.unquote(sid))
    if subtitle_path and subtitle_path.exists():
        return send_file(subtitle_path, mimetype="text/vtt")
    return localized_message("subtitle_not_found"), 404


@app.route("/hls/<vid>/index.m3u8")
def hls_playlist(vid):
    ok, deny = require_media_access(urllib.parse.unquote(vid))
    if not ok:
        return deny
    video_path, err = ensure_media_id_ready(vid)
    if err:
        return err
    if not ON_DEMAND_TRANSCODE or video_path.suffix.lower() not in SOURCE_EXTENSIONS:
        return localized_message("hls_not_enabled"), 400

    segment_length = 2
    duration = catalog._probe_duration(video_path) or 0.0
    total = max(1, int(math.ceil(duration / segment_length))) if duration > 0 else 1
    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
        f"#EXT-X-TARGETDURATION:{segment_length}",
        "#EXT-X-MEDIA-SEQUENCE:0",
        "#EXT-X-PLAYLIST-TYPE:VOD",
    ]
    for seq in range(total):
        chunk_dur = (
            segment_length
            if duration <= 0
            else max(0.1, min(segment_length, duration - (seq * segment_length)))
        )
        lines.append(f"#EXTINF:{chunk_dur:.3f},")
        lines.append(f"{seq}.ts")
    lines.append("#EXT-X-ENDLIST")
    return Response(
        "\n".join(lines) + "\n",
        mimetype="application/vnd.apple.mpegurl",
    )


@app.route("/hls/<vid>/<int:seq>.ts")
def hls_segment(vid, seq):
    ok, deny = require_media_access(urllib.parse.unquote(vid))
    if not ok:
        return deny
    video_path, err = ensure_media_id_ready(vid)
    if err:
        return err
    if not ON_DEMAND_TRANSCODE or video_path.suffix.lower() not in SOURCE_EXTENSIONS:
        return localized_message("hls_not_enabled"), 400
    if not FFMPEG:
        return localized_message("ffmpeg_not_found"), 500

    segment_length = 2
    start = max(0, int(seq)) * segment_length

    def run_seg_stream(vcodec: str):
        cmd = [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(start),
            "-t",
            str(segment_length),
            "-i",
            str(video_path),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-c:v",
            vcodec,
        ]
        if vcodec == "libx264":
            cmd += [
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-profile:v",
                "main",
                "-level",
                "4.0",
                "-g",
                "48",
                "-keyint_min",
                "48",
                "-sc_threshold",
                "0",
            ]
        cmd += [
            "-b:v",
            "3200k",
            "-maxrate",
            "4200k",
            "-bufsize",
            "8400k",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-f",
            "mpegts",
            "pipe:1",
        ]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    proc = run_seg_stream(HWACCEL_CODEC)

    def stream_with_codec_fallback(primary_proc):
        process = primary_proc
        used_fallback = False
        try:
            first = process.stdout.read(65536)
            if not first:
                try:
                    if process.poll() is None:
                        process.kill()
                except Exception:
                    pass
                process = run_seg_stream("libx264")
                used_fallback = True
                first = process.stdout.read(65536)
            if first:
                yield first
            while True:
                chunk = process.stdout.read(65536)
                if not chunk:
                    break
                yield chunk
        finally:
            try:
                if process.poll() is None:
                    process.kill()
            except Exception:
                pass
            if used_fallback:
                logging.debug("HLS segment %s for %s used libx264 fallback", seq, video_path.name)

    return Response(
        stream_with_codec_fallback(proc),
        mimetype="video/mp2t",
        headers={"Cache-Control": "no-store"},
    )


@app.route("/plex/poster/<vid>.jpg")
def plex_poster(vid):
    decoded_vid = urllib.parse.unquote(vid)
    if not plex_adapter or not plex_adapter.enabled:
        thumb_path = catalog.thumb_map.get(decoded_vid)
        if thumb_path and thumb_path.exists():
            return apply_public_image_cache(
                send_file(thumb_path, mimetype="image/jpeg")
            )
        return thumb_placeholder()
    try:
        plex_adapter.bind_catalog(catalog.video_map)
    except Exception:
        pass
    try:
        req_w = int(request.args.get("w", "360") or 360)
    except Exception:
        req_w = 360
    try:
        req_h = int(request.args.get("h", "540") or 540)
    except Exception:
        req_h = 540
    resp, err = plex_adapter.proxy_resized_poster(
        decoded_vid,
        req_w,
        req_h,
    )
    if not resp:
        thumb_path = catalog.thumb_map.get(decoded_vid)
        if thumb_path and thumb_path.exists():
            return apply_public_image_cache(
                send_file(thumb_path, mimetype="image/jpeg")
            )
        return thumb_placeholder()
    try:
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "image/jpeg")
        return apply_public_image_cache(Response(body, mimetype=ctype))
    finally:
        resp.close()


@app.route("/plex/subtitle/<vid>.vtt")
def plex_subtitle(vid):
    ok, deny = require_media_access(urllib.parse.unquote(vid))
    if not ok:
        return deny
    if not plex_adapter or not plex_adapter.enabled:
        return localized_message("subtitle_not_found"), 404
    try:
        plex_adapter.bind_catalog(catalog.video_map)
    except Exception:
        pass
    resp, err = plex_adapter.proxy_binary_by_kind(urllib.parse.unquote(vid), "subtitle")
    if not resp:
        return localized_message("subtitle_not_found"), 404
    try:
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "text/vtt")
        normalized = normalize_subtitle_to_vtt(body, ctype)
        return Response(normalized, mimetype="text/vtt")
    finally:
        resp.close()


@app.route("/plex/video/<vid>")
def plex_video_legacy(vid):
    raw_vid = urllib.parse.unquote(vid)
    if raw_vid.endswith(".m3u8"):
        return plex_video(raw_vid[:-5])
    return redirect(app_url(f"/plex/video/{urllib.parse.quote(raw_vid)}.m3u8"), code=302)


@app.route("/plex/video/<vid>.m3u8")
def plex_video(vid):
    ok, deny = require_media_access(urllib.parse.unquote(vid))
    if not ok:
        return deny
    if not plex_adapter or not plex_adapter.enabled:
        return localized_message("not_found"), 404
    video_path, err = ensure_media_id_ready(vid)
    if err:
        return err

    ensure_plex_catalog_binding(
        force_refresh=not bool(getattr(plex_adapter, "_by_video_id", None))
    )

    video_id = urllib.parse.unquote(vid)
    playlist_url = plex_adapter.build_transcode_playlist_url(video_id)
    if not playlist_url:
        try:
            ensure_plex_catalog_binding(force_refresh=True)
            playlist_url = plex_adapter.build_transcode_playlist_url(video_id)
        except Exception:
            playlist_url = None
    if not playlist_url:
        return localized_message("not_found"), 404

    try:
        with plex_adapter.open_absolute(
            playlist_url,
            headers={"Accept": "application/vnd.apple.mpegurl,application/x-mpegURL"},
        ) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return localized_message("not_found"), 404

    mount_root = resolve_app_root()
    base = playlist_url.rsplit("/", 1)[0] + "/"
    out_lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue
        abs_url = urllib.parse.urljoin(base, stripped)
        out_lines.append(
            build_plex_hls_proxy_url(
                abs_url,
                mount_root=mount_root,
                relative_mode="from_video",
            )
        )

    return Response(
        "\n".join(out_lines) + "\n",
        mimetype="application/vnd.apple.mpegurl",
        headers={"Cache-Control": "no-store"},
    )


@app.route("/plex/hls/proxy")
def plex_hls_proxy():
    raw = str(request.args.get("u", "") or "").strip()
    if not raw:
        return localized_message("bad_request"), 400
    mount_root = normalize_mount_prefix(request.args.get("root", "") or "") or resolve_app_root()
    try:
        target = urllib.parse.unquote(raw)
        parsed = urllib.parse.urlparse(target)
        if parsed.scheme not in {"http", "https"}:
            return localized_message("bad_request"), 400
        base = urllib.parse.urlparse(plex_adapter.base_url if plex_adapter else "")
        if not base.netloc or parsed.netloc != base.netloc:
            return localized_message("forbidden"), 403
        if plex_adapter and plex_adapter.token:
            query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            if not any(key == "X-Plex-Token" for key, _ in query_pairs):
                query_pairs.append(("X-Plex-Token", plex_adapter.token))
                target = urllib.parse.urlunparse(
                    parsed._replace(query=urllib.parse.urlencode(query_pairs))
                )
    except Exception:
        return localized_message("bad_request"), 400

    upstream_headers = {}
    for header_name in (
        "Accept",
        "Range",
        "If-Range",
        "User-Agent",
        "Origin",
        "Referer",
    ):
        value = request.headers.get(header_name)
        if value:
            upstream_headers[header_name] = value
    if "Accept" not in upstream_headers:
        upstream_headers["Accept"] = "*/*"

    try:
        upstream = (
            plex_adapter.open_absolute(target, headers=upstream_headers)
            if plex_adapter
            else None
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            referer_video_id = extract_video_id_from_referer(request.headers.get("Referer", ""))
            if referer_video_id:
                _, err = ensure_media_id_ready(referer_video_id)
                if err and err[0] == localized_message("media_folder_not_mounted"):
                    return err
                try:
                    upstream = (
                        plex_adapter.open_absolute(target, headers=upstream_headers)
                        if plex_adapter
                        else None
                    )
                except Exception:
                    upstream = None
            else:
                upstream = None
        else:
            upstream = None
    except Exception:
        upstream = None
    if not upstream:
        return localized_message("not_found"), 404

    ctype = upstream.headers.get("Content-Type", "application/octet-stream")
    upstream_status = int(
        getattr(upstream, "status", None)
        or getattr(upstream, "code", None)
        or 200
    )
    if "mpegurl" in ctype or target.endswith(".m3u8"):
        try:
            text = upstream.read().decode("utf-8", errors="ignore")
        finally:
            try:
                upstream.close()
            except Exception:
                pass
        base = target.rsplit("/", 1)[0] + "/"
        out_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                out_lines.append(line)
                continue
            abs_url = urllib.parse.urljoin(base, stripped)
            out_lines.append(
                build_plex_hls_proxy_url(
                    abs_url,
                    mount_root=mount_root,
                    relative_mode="from_proxy",
                )
            )
        return Response(
            "\n".join(out_lines) + "\n",
            status=upstream_status,
            mimetype="application/vnd.apple.mpegurl",
            headers={"Cache-Control": "no-store"},
        )

    passthrough_headers = {"Cache-Control": "no-store"}
    for header_name in (
        "Content-Length",
        "Content-Range",
        "Accept-Ranges",
        "Content-Disposition",
        "ETag",
        "Last-Modified",
    ):
        value = upstream.headers.get(header_name)
        if value:
            passthrough_headers[header_name] = value

    def generate():
        try:
            while True:
                chunk = upstream.read(65536)
                if not chunk:
                    break
                yield chunk
        finally:
            try:
                upstream.close()
            except Exception:
                pass

    return Response(
        generate(),
        status=upstream_status,
        mimetype=ctype,
        headers=passthrough_headers,
        direct_passthrough=True,
    )


@app.route("/video/<vid>")
def video(vid):
    ok, deny = require_media_access(urllib.parse.unquote(vid))
    if not ok:
        return deny
    video_path, err = ensure_media_id_ready(vid)
    if err:
        return err
    suffix = video_path.suffix.lower()
    ctype = "video/mp2t" if suffix == ".ts" else (
        mimetypes.guess_type(video_path.name)[0] or "application/octet-stream"
    )

    force_fmp4 = parse_bool(request.args.get("fmp4", "0"))
    if (
        ON_DEMAND_TRANSCODE
        and suffix in SOURCE_EXTENSIONS
        and FFMPEG
        and (force_fmp4 or not cfg_runtime.get("on_demand_hls", False))
    ):

        def generate_transcoded():
            cmd = [
                FFMPEG,
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(video_path),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-profile:v",
                "main",
                "-level",
                "4.0",
                "-g",
                "48",
                "-keyint_min",
                "48",
                "-sc_threshold",
                "0",
                "-b:v",
                "4500k",
                "-maxrate",
                "6000k",
                "-bufsize",
                "12000k",
                "-c:a",
                "aac",
                "-b:a",
                "160k",
                "-ac",
                "2",
                "-ar",
                "48000",
                "-movflags",
                "+frag_keyframe+empty_moov+default_base_moof",
                "-f",
                "mp4",
                "pipe:1",
            ]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            try:
                while True:
                    chunk = proc.stdout.read(65536)
                    if not chunk:
                        break
                    yield chunk
            except GeneratorExit:
                try:
                    proc.kill()
                except Exception:
                    pass
                raise
            finally:
                try:
                    if proc.poll() is None:
                        proc.kill()
                except Exception:
                    pass

        return Response(
            generate_transcoded(),
            mimetype="video/mp4",
            headers={
                "Content-Type": "video/mp4",
                "Accept-Ranges": "none",
                "Content-Disposition": "inline",
            },
        )

    range_header = request.headers.get("Range")
    file_size = video_path.stat().st_size
    start, end = 0, file_size - 1
    status = 200

    if range_header:
        match = re.match(r"bytes=(\d*)-(\d*)", range_header)
        if match:
            status = 206
            if match.group(1):
                start = int(match.group(1))
            if match.group(2):
                end = int(match.group(2))
            start = max(0, min(start, file_size - 1))
            end = max(start, min(end, file_size - 1))

    def generate():
        with video_path.open("rb") as handle:
            handle.seek(start)
            remain = end - start + 1
            while remain > 0:
                chunk = handle.read(min(65536, remain))
                if not chunk:
                    break
                yield chunk
                remain -= len(chunk)

    headers = {
        "Content-Type": ctype,
        "Content-Length": str(end - start + 1),
        "Accept-Ranges": "bytes",
        "Content-Disposition": "inline",
    }
    if status == 206:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    return Response(generate(), status=status, headers=headers, direct_passthrough=True)


class App:
    def __init__(self, cfg: Dict):
        global APP_INSTANCE, APPROVED_PRIVATE_DEVICES, AUTH_FAILURES
        self.config_path = (
            Path(cfg.get("_config_path", "")).expanduser()
            if cfg.get("_config_path")
            else None
        )
        self.auto_scan_on_start = bool(cfg.get("auto_scan_on_start", True))
        self._apply_cfg(cfg)
        private_state = load_private_state(PRIVATE_STATE_PATH)
        APPROVED_PRIVATE_DEVICES = set(private_state.get("approved_devices", []))
        auth_state = load_auth_state(AUTH_STATE_PATH)
        AUTH_FAILURES = dict(auth_state.get("unlock_failures", {}))
        APP_INSTANCE = self

    def _apply_cfg(self, cfg: Dict):
        global catalog, plex_adapter, ON_DEMAND_TRANSCODE, HWACCEL_CODEC, cfg_runtime
        root_cfg = cfg.get("root", [])
        root_list = root_cfg if isinstance(root_cfg, list) else [root_cfg]
        roots = [Path(root).expanduser().resolve() for root in root_list if str(root).strip()]
        plex_cfg = cfg.get("plex", {}) if isinstance(cfg.get("plex", {}), dict) else {}
        plex_enabled = bool(cfg.get("enable_plex_server", False))
        catalog = Catalog(
            roots,
            Path(cfg["thumbs_dir"]).expanduser().resolve(),
            private_folders=(
                cfg.get("private_folder", [])
                if isinstance(cfg.get("private_folder", []), list)
                else [cfg.get("private_folder", "")]
            ),
            private_passcode=cfg.get("private_passcode", ""),
            transcode_enabled=cfg.get("transcode", True),
            verify_passcode_fn=verify_passcode,
            generate_thumbs=True,
            scan_checkpoint_cb=(
                (lambda scanning: schedule_plex_overlay_refresh(
                    persist_index=not scanning,
                    force_refresh=False,
                ))
                if plex_enabled
                else None
            ),
        )
        self.host = cfg.get("host", "0.0.0.0")
        self.port = int(cfg.get("port", DEFAULT_PORT))
        ON_DEMAND_TRANSCODE = bool(cfg.get("on_demand_transcode", False))
        HWACCEL_CODEC = str(
            cfg.get("transcode_video_codec", "h264_videotoolbox")
            or "h264_videotoolbox"
        )
        cfg_runtime["on_demand_hls"] = bool(cfg.get("on_demand_hls", False))
        direct_cfg = cfg.get("direct_playback", {}) if isinstance(cfg.get("direct_playback"), dict) else {}
        cfg_runtime["direct_playback_enabled"] = bool(direct_cfg.get("enabled", True))
        cfg_runtime["direct_audio_whitelist"] = {
            str(codec).strip().lower()
            for codec in (direct_cfg.get("audio_whitelist") or [])
            if str(codec or "").strip()
        }
        cfg_runtime["debug_enabled"] = bool(cfg.get("debug_enabled", False))
        cfg_runtime["mount_script"] = str(cfg.get("mount_script", "") or "").strip()
        cfg_runtime["plex_enabled"] = plex_enabled
        cfg_runtime["plex_base_url"] = str(plex_cfg.get("base_url", "") or "").strip()
        cfg_runtime["locale"] = str(cfg.get("locale", "auto") or "auto").strip() or "auto"
        plex_adapter = PlexAdapter(
            enabled=plex_enabled,
            plex_cfg=plex_cfg,
        )

    def reload_from_disk(self):
        if not self.config_path:
            return False
        try:
            cfg = load_config(self.config_path)
            cfg["_config_path"] = str(self.config_path)
            self._apply_cfg(cfg)
            logging.info("Rescan reloaded config from %s", self.config_path)
            return True
        except Exception as exc:
            logging.warning("Rescan config reload failed: %s", exc)
            return False

    def run(self):
        if self.auto_scan_on_start:

            def startup_scan():
                catalog.scan()
                schedule_plex_overlay_refresh(persist_index=True, force_refresh=True)

            threading.Thread(target=startup_scan, daemon=True).start()
        else:
            threading.Thread(
                target=lambda: schedule_plex_overlay_refresh(
                    persist_index=False,
                    force_refresh=True,
                ),
                daemon=True,
            ).start()

        logging.info(
            "Movies Server (Flask + Waitress) starting on %s:%s",
            self.host,
            self.port,
        )
        logging.info("Access: http://localhost:%s", self.port)
        for handler in logging.getLogger().handlers:
            try:
                handler.flush()
            except Exception:
                pass
        serve(app, host=self.host, port=self.port, threads=8, connection_limit=100)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    setup_logging(flush_interval_seconds=60)
    cfg = load_config(args.config)
    cfg["_config_path"] = str(args.config)
    App(cfg).run()


if __name__ == "__main__":
    main()
