#!/usr/bin/env python3
"""Helpers for loading bundled runtime assets from source or installed package data."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Optional

ASSET_PACKAGE = "cat_theatre_assets"
ROOT = Path(__file__).resolve().parent
SOURCE_ASSET_ROOT = ROOT / ASSET_PACKAGE


def _local_asset_path(name: str, subdir: Optional[str] = None) -> Path:
    if subdir:
        package_local = SOURCE_ASSET_ROOT / subdir / name
        if package_local.exists():
            return package_local
        return ROOT / subdir / name
    return ROOT / name


def load_asset_bytes(name: str, subdir: Optional[str] = None) -> bytes:
    local_path = _local_asset_path(name, subdir)
    if local_path.exists():
        return local_path.read_bytes()
    target = resources.files(ASSET_PACKAGE)
    if subdir:
        target = target.joinpath(subdir)
    return target.joinpath(name).read_bytes()


def load_asset_text(name: str, subdir: Optional[str] = None, encoding: str = "utf-8") -> str:
    local_path = _local_asset_path(name, subdir)
    if local_path.exists():
        return local_path.read_text(encoding=encoding)
    target = resources.files(ASSET_PACKAGE)
    if subdir:
        target = target.joinpath(subdir)
    return target.joinpath(name).read_text(encoding=encoding)
