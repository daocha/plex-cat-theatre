#!/usr/bin/env python3
"""Plex overlay refresh coordination for movies server."""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path


class PlexOverlayCoordinator:
    def __init__(self, min_interval: float = 3.0):
        self._lock = threading.Lock()
        self._running = False
        self._pending = False
        self._pending_persist = False
        self._pending_force = False
        self._last_run = 0.0
        self._min_interval = float(min_interval)

    def _ensure_binding(self, adapter, catalog, force_refresh: bool = False):
        if not adapter or not adapter.enabled or not catalog:
            return
        try:
            if force_refresh or not getattr(adapter, "_items_by_file", None):
                adapter.refresh()
            adapter.bind_catalog(catalog.video_map)
        except Exception:
            try:
                adapter.bind_catalog(catalog.video_map)
            except Exception:
                pass

    def _rebuild_overlay(self, adapter, catalog, persist_index: bool = True):
        if not adapter or not adapter.enabled:
            return
        try:
            adapter.bind_catalog(catalog.video_map)
            with catalog._lock:
                base_items = list(catalog._videos)
            merged_items = [
                adapter.overlay_item(str(video.get("id", "")), video)
                for video in base_items
            ]
            with catalog._lock:
                catalog._videos = merged_items
                if not catalog.is_scanning:
                    catalog._public_videos = list(merged_items)
                    catalog._public_private_video_ids = {
                        video.get("id", "")
                        for video in merged_items
                        if catalog._is_private_video(video)
                    }
            if persist_index:
                catalog._save_index(Path(__file__).with_name("movies_catalog_index.json"))
        except Exception as exc:
            logging.warning("Plex overlay rebuild failed: %s", exc)

    def schedule(
        self,
        adapter,
        catalog,
        persist_index: bool = False,
        force_refresh: bool = False,
    ):
        if not adapter or not adapter.enabled:
            return

        def _run():
            while True:
                with self._lock:
                    now = time.time()
                    if (not self._pending_force) and (
                        now - self._last_run < self._min_interval
                    ):
                        delay = self._min_interval - (now - self._last_run)
                    else:
                        delay = 0.0
                if delay > 0:
                    time.sleep(delay)
                with self._lock:
                    pending_persist = self._pending_persist
                    pending_force = self._pending_force
                    self._pending = False
                    self._pending_persist = False
                    self._pending_force = False
                try:
                    self._ensure_binding(adapter, catalog, force_refresh=pending_force)
                    self._rebuild_overlay(adapter, catalog, persist_index=pending_persist)
                finally:
                    with self._lock:
                        self._last_run = time.time()
                        rerun = bool(self._pending)
                        if not rerun:
                            self._running = False
                if not rerun:
                    break

        with self._lock:
            self._pending = True
            self._pending_persist = self._pending_persist or persist_index
            self._pending_force = self._pending_force or force_refresh
            if self._running:
                return
            self._running = True
        threading.Thread(target=_run, daemon=True).start()
