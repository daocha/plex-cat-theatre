import json
import tempfile
import unittest
from pathlib import Path

from movies_server_core import DEFAULT_PORT, load_config


class LoadConfigTests(unittest.TestCase):
    def write_config(self, payload: dict) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "movies_config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_load_config_applies_defaults_and_normalizes_lists(self):
        path = self.write_config(
            {
                "root": "~/Movies",
                "private_folder": "Private",
            }
        )

        cfg = load_config(path)

        self.assertEqual(cfg["port"], DEFAULT_PORT)
        self.assertEqual(cfg["host"], "0.0.0.0")
        self.assertEqual(cfg["root"], ["~/Movies"])
        self.assertEqual(cfg["private_folder"], ["Private"])
        self.assertEqual(cfg["direct_playback"]["audio_whitelist"], ["aac", "mp3"])
        self.assertEqual(cfg["thumbs_dir"], str(path.parent / "cache" / "thumbnails"))

    def test_load_config_rejects_invalid_port(self):
        path = self.write_config(
            {
                "root": ["~/Movies"],
                "port": 70000,
            }
        )

        with self.assertRaisesRegex(ValueError, "port"):
            load_config(path)

    def test_load_config_rejects_invalid_direct_playback_type(self):
        path = self.write_config(
            {
                "root": ["~/Movies"],
                "direct_playback": [],
            }
        )

        with self.assertRaisesRegex(ValueError, "direct_playback"):
            load_config(path)

    def test_load_config_rejects_invalid_locale(self):
        path = self.write_config(
            {
                "root": ["~/Movies"],
                "locale": "es",
            }
        )

        with self.assertRaisesRegex(ValueError, "locale"):
            load_config(path)


if __name__ == "__main__":
    unittest.main()
