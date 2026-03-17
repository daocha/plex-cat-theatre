#!/usr/bin/env python3
"""Update movies_config.json private_passcode with sha256 hash.

Usage:
  python passcode.py <new_passcode>
  python passcode.py <new_passcode> --config /path/to/movies_config.json
"""

import argparse
import json
from pathlib import Path
from movies_server_core import hash_passcode_sha256


def main() -> int:
    parser = argparse.ArgumentParser(description="Update movies_config.json private_passcode")
    parser.add_argument("passcode", help="new plaintext passcode")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).with_name("movies_config.json")),
        help="path to movies config json",
    )
    parser.add_argument(
        "--state",
        default=str(Path(__file__).with_name("movies_state.json")),
        help="path to movies state json (approved devices)",
    )
    args = parser.parse_args()

    cfg_path = Path(args.config).expanduser().resolve()
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found: {cfg_path}")

    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    data["private_passcode"] = hash_passcode_sha256(args.passcode)

    cfg_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    state_path = Path(args.state).expanduser().resolve()
    state_data = {"approved_devices": []}
    if state_path.exists():
        try:
            state_data = json.loads(state_path.read_text(encoding="utf-8"))
            if not isinstance(state_data, dict):
                state_data = {"approved_devices": []}
        except Exception:
            state_data = {"approved_devices": []}
    state_data["approved_devices"] = []
    state_path.write_text(json.dumps(state_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Updated private_passcode in: {cfg_path}")
    print("Cleared approved_devices in:", state_path)
    print(f"private_passcode = {data['private_passcode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
