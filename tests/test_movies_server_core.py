import json
import tempfile
import unittest
from pathlib import Path

from movies_server_core import DEFAULT_PORT, load_config, startup_console_summary


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
        self.assertEqual(cfg["log_dir"], str(path.parent / "logs"))

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

    def test_load_config_normalizes_common_locale_variants(self):
        path = self.write_config(
            {
                "root": ["~/Movies"],
                "locale": "fr_FR",
            }
        )
        cfg = load_config(path)
        self.assertEqual(cfg["locale"], "fr")

        path = self.write_config(
            {
                "root": ["~/Movies"],
                "locale": "zh-cn",
            }
        )
        cfg = load_config(path)
        self.assertEqual(cfg["locale"], "zh-CN")

    def test_load_config_resolves_relative_storage_paths_from_config_dir(self):
        path = self.write_config(
            {
                "root": ["~/Movies"],
                "thumbs_dir": "./cache/thumbnails",
                "log_dir": "./logs",
            }
        )

        cfg = load_config(path)

        self.assertEqual(cfg["thumbs_dir"], str(path.parent / "cache" / "thumbnails"))
        self.assertEqual(cfg["log_dir"], str(path.parent / "logs"))

    def test_startup_console_summary_uses_log_path_and_access_url(self):
        summary = startup_console_summary(
            {
                "host": "0.0.0.0",
                "port": 9245,
                "log_dir": "/tmp/cat-theatre-logs",
            }
        )

        self.assertEqual(
            summary["log_path"],
            str((Path("/tmp/cat-theatre-logs").expanduser().resolve() / "movies.log")),
        )
        self.assertEqual(summary["access_url"], "http://localhost:9245")


if __name__ == "__main__":
    unittest.main()
