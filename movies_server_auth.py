#!/usr/bin/env python3
"""Private-access helper functions for movies server."""

from __future__ import annotations

from flask import request


def can_access_private(
    catalog,
    approved_private_devices: set[str],
    verify_passcode_fn,
    device_id: str,
    passcode: str = "",
) -> bool:
    if not catalog.private_folders:
        return True
    if device_id and device_id in approved_private_devices:
        return True
    if passcode and verify_passcode_fn(passcode, catalog.private_passcode):
        return True
    return False


def resolve_private_visibility(
    catalog,
    approved_private_devices: set[str],
    verify_passcode_fn,
    extract_device_id_fn,
) -> tuple[bool, bool]:
    device_id = extract_device_id_fn()
    passcode = str(
        request.args.get("passcode", "")
        or request.headers.get("X-Private-Passcode", "")
    ).strip()
    authorized = bool(device_id and device_id in approved_private_devices)
    allow_private = authorized or bool(
        passcode and verify_passcode_fn(passcode, catalog.private_passcode)
    )
    return allow_private, authorized


def require_media_access(
    catalog,
    approved_private_devices: set[str],
    verify_passcode_fn,
    extract_device_id_fn,
    localized_json_error_fn,
    video_id: str,
) -> tuple[bool, tuple]:
    if not catalog.is_private_id(video_id):
        return True, (None, None)
    device_id = extract_device_id_fn()
    passcode = str(
        request.args.get("passcode", "")
        or request.headers.get("X-Private-Passcode", "")
    ).strip()
    if can_access_private(
        catalog,
        approved_private_devices,
        verify_passcode_fn,
        device_id,
        passcode=passcode,
    ):
        return True, (None, None)
    return False, localized_json_error_fn("forbidden_private", 403)
