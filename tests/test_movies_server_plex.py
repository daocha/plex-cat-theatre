import unittest

from movies_server_plex import PlexAdapter


class PlexAdapterTests(unittest.TestCase):
    def test_build_transcode_playlist_url_uses_cat_theatre_session_prefix(self):
        adapter = PlexAdapter(
            True,
            {
                "base_url": "http://127.0.0.1:32400",
                "token": "abc123",
            },
        )
        adapter._by_video_id = {
            "vid-1": {
                "rating_key": "42",
            }
        }

        url = adapter.build_transcode_playlist_url("vid-1")

        self.assertIsNotNone(url)
        assert url is not None
        self.assertIn("session=cat_theatre-", url)
        self.assertIn("X-Plex-Token=abc123", url)
        self.assertIn("/video/:/transcode/universal/start.m3u8", url)

    def test_build_transcode_playlist_url_returns_none_without_rating_key(self):
        adapter = PlexAdapter(True, {})
        adapter._by_video_id = {"vid-1": {}}

        self.assertIsNone(adapter.build_transcode_playlist_url("vid-1"))


if __name__ == "__main__":
    unittest.main()
