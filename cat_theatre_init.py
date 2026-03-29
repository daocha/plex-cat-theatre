#!/usr/bin/env python3
"""Interactive first-run bootstrap for installed Cat Theatre users."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import pwd
import shutil
import sys
from pathlib import Path

from movies_resources import load_asset_text


def resolve_default_home() -> Path:
    sudo_user = os.getenv("SUDO_USER", "").strip()
    if sudo_user and sudo_user != "root":
        try:
            return Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            pass
    return Path.home()


DEFAULT_CONFIG_PATH = resolve_default_home() / "movies_config.json"
PASSCODE_PLACEHOLDER = "sha256:replace-with-your-passcode-hash"


def hash_passcode_sha256(passcode: str) -> str:
    return "sha256:" + hashlib.sha256((passcode or "").encode("utf-8")).hexdigest()


def prompt_yes_no(message: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{message} {suffix} ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def prompt_passcode() -> str:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return ""
    print()
    print("Private mode setup:")
    print("- Leave this empty if you do not want to set a passcode right now.")
    first = getpass.getpass("Enter a new private-mode passcode: ")
    if not first:
        return ""
    second = getpass.getpass("Confirm the private-mode passcode: ")
    if first != second:
        raise SystemExit("Passcodes did not match.")
    return first


def load_sample_config() -> dict:
    return json.loads(load_asset_text("movies_config.sample.json"))


def write_config(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def print_next_steps(config_path: Path):
    print()
    print(f"Config created at: {config_path}")
    print()
    print("Before starting the server, review these fields in your config:")
    print("- root")
    print("- thumbs_dir")
    print("- private_folder")
    print("- private_passcode")
    print("- enable_plex_server, plex.base_url, plex.token")
    print("- mount_script")
    print()
    print("Required system binaries:")
    print("- ffmpeg")
    print("- ffprobe")
    print()
    print("Start the server with:")
    print(f"plex-cat-theatre --config {config_path}")
    print()
    print("Then open:")
    print("http://localhost:9245")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an initial Cat Theatre config in your home directory.")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="target config path (default: ~/movies_config.json)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing config without prompting",
    )
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    if config_path.exists() and not args.force:
        if not sys.stdin.isatty() or not prompt_yes_no(f"{config_path} already exists. Overwrite it?"):
            print(f"Keeping existing config: {config_path}")
            print_next_steps(config_path)
            return 0

    cfg = load_sample_config()
    passcode = prompt_passcode()
    if passcode:
        cfg["private_passcode"] = hash_passcode_sha256(passcode)
    elif str(cfg.get("private_passcode", "")).strip() == PASSCODE_PLACEHOLDER:
        cfg["private_passcode"] = ""

    write_config(config_path, cfg)

    cache_dir = str(cfg.get("thumbs_dir", "") or "").strip()
    if cache_dir:
        thumbs_path = Path(cache_dir).expanduser()
        if not thumbs_path.is_absolute():
            thumbs_path = (config_path.parent / thumbs_path).resolve()
        thumbs_path.mkdir(parents=True, exist_ok=True)

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print()
        print("Warning: ffmpeg and ffprobe are not both available in PATH yet.")

    print_next_steps(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
