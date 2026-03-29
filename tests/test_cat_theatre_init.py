import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cat_theatre_init import resolve_default_home


class ResolveDefaultHomeTests(unittest.TestCase):
    def test_uses_sudo_user_home_when_available(self):
        with patch.dict("os.environ", {"SUDO_USER": "alice"}, clear=False):
            with patch("pwd.getpwnam", return_value=SimpleNamespace(pw_dir="/Users/alice")):
                with patch("pathlib.Path.home", return_value=Path("/Users/current")):
                    self.assertEqual(resolve_default_home(), Path("/Users/alice"))

    def test_falls_back_to_path_home_when_sudo_user_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("pathlib.Path.home", return_value=Path("/Users/current")):
                self.assertEqual(resolve_default_home(), Path("/Users/current"))

    def test_falls_back_to_path_home_when_sudo_user_lookup_fails(self):
        with patch.dict("os.environ", {"SUDO_USER": "missing-user"}, clear=False):
            with patch("pwd.getpwnam", side_effect=KeyError("missing-user")):
                with patch("pathlib.Path.home", return_value=Path("/Users/current")):
                    self.assertEqual(resolve_default_home(), Path("/Users/current"))


if __name__ == "__main__":
    unittest.main()
