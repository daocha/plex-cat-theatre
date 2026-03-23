import threading
import time
import unittest

from movies_server_overlay import PlexOverlayCoordinator


class _Adapter:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self._items_by_file = {}
        self.refresh_calls = 0
        self.bound_maps = []

    def refresh(self):
        self.refresh_calls += 1
        self._items_by_file = {"ready": True}

    def bind_catalog(self, video_map):
        self.bound_maps.append(video_map)

    def overlay_item(self, video_id, video):
        item = dict(video)
        item["overlay_from"] = video_id
        return item


class _Catalog:
    def __init__(self, name):
        self.name = name
        self.video_map = {name: f"/tmp/{name}.mp4"}
        self._videos = [{"id": name, "name": name}]
        self._public_videos = []
        self._public_private_video_ids = set()
        self._lock = threading.Lock()
        self.is_scanning = False
        self.saved = 0

    def _is_private_video(self, video):
        return False

    def _save_index(self, path):
        self.saved += 1


class OverlayCoordinatorTests(unittest.TestCase):
    def test_schedule_uses_latest_catalog_and_adapter_on_rerun(self):
        coordinator = PlexOverlayCoordinator(min_interval=0.0)
        first_adapter = _Adapter()
        second_adapter = _Adapter()
        first_catalog = _Catalog("first")
        second_catalog = _Catalog("second")
        started = threading.Event()
        release = threading.Event()

        original_rebuild = coordinator._rebuild_overlay

        def gated_rebuild(adapter, catalog, persist_index=True):
            if catalog is first_catalog:
                started.set()
                release.wait(timeout=1.0)
            return original_rebuild(adapter, catalog, persist_index=persist_index)

        coordinator._rebuild_overlay = gated_rebuild

        coordinator.schedule(first_adapter, first_catalog, persist_index=False, force_refresh=False)
        self.assertTrue(started.wait(timeout=1.0))
        coordinator.schedule(second_adapter, second_catalog, persist_index=True, force_refresh=True)
        release.set()

        deadline = time.time() + 1.0
        while time.time() < deadline and not second_catalog.saved:
            time.sleep(0.01)

        self.assertGreaterEqual(second_adapter.refresh_calls, 1)
        self.assertIn(second_catalog.video_map, second_adapter.bound_maps)
        self.assertEqual(second_catalog._videos[0]["id"], "second")
        self.assertEqual(second_catalog.saved, 1)


if __name__ == "__main__":
    unittest.main()
