#!/usr/bin/env bash
set -euo pipefail

# Starter bootstrap script for Cat Theatre.
# It prepares a local Python virtual environment, installs dependencies,
# creates a working config from the sample on first run, and starts the server.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="${SCRIPT_DIR}/movies_config.json"
SAMPLE_CONFIG_PATH="${SCRIPT_DIR}/movies_config.sample.json"
VENV_PATH="${SCRIPT_DIR}/.venv"
PYTHON_BIN="${VENV_PATH}/bin/python"
PIP_BIN="${VENV_PATH}/bin/pip"

require_cmd() {
  local cmd="$1"
  local help_text="$2"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: Missing required command: ${cmd}"
    echo "Hint: ${help_text}"
    exit 1
  fi
}

read_config_value() {
  local expr="$1"
  "${PYTHON_BIN}" - "${CONFIG_PATH}" "${expr}" <<'PY'
import json
import sys
from pathlib import Path

cfg_path = Path(sys.argv[1])
expr = sys.argv[2]

with cfg_path.open("r", encoding="utf-8") as handle:
    cfg = json.load(handle)

value = cfg
for part in expr.split("."):
    if isinstance(value, dict):
        value = value.get(part)
    else:
        value = None
        break

if isinstance(value, list):
    print(", ".join(str(item) for item in value))
elif isinstance(value, bool):
    print("true" if value else "false")
elif value is None:
    print("")
else:
    print(value)
PY
}

write_private_passcode() {
  local passcode="$1"
  "${PYTHON_BIN}" "${SCRIPT_DIR}/passcode.py" "${passcode}" --config "${CONFIG_PATH}" >/dev/null
}

echo "== Cat Theatre startup =="

require_cmd python3 "Install Python 3 first."
require_cmd ffmpeg "Install ffmpeg so thumbnails, previews, and local transcoding can work."
require_cmd ffprobe "Install ffprobe so metadata such as aspect ratio and codecs can be detected."

if [[ ! -f "${SAMPLE_CONFIG_PATH}" ]]; then
  echo "ERROR: Sample config not found: ${SAMPLE_CONFIG_PATH}"
  exit 1
fi

if [[ ! -f "${CONFIG_PATH}" ]]; then
  cp "${SAMPLE_CONFIG_PATH}" "${CONFIG_PATH}"
  echo "Created movies_config.json from movies_config.sample.json"
  echo "Edit the config before real use if you have not done so yet."
  echo
fi

mkdir -p "${SCRIPT_DIR}/cache/thumbnails"

if [[ ! -d "${VENV_PATH}" ]]; then
  echo "Creating local virtual environment at ${VENV_PATH}"
  python3 -m venv "${VENV_PATH}"
fi

# Upgrade pip first so a clean machine can install requirements more reliably.
"${PYTHON_BIN}" -m pip install --upgrade pip >/dev/null
"${PIP_BIN}" install -r "${SCRIPT_DIR}/requirements.txt"

CURRENT_PRIVATE_PASSCODE="$(read_config_value "private_passcode")"
if [[ -t 0 && -t 1 ]] && [[ -z "${CURRENT_PRIVATE_PASSCODE}" || "${CURRENT_PRIVATE_PASSCODE}" == "sha256:replace-with-your-passcode-hash" ]]; then
  echo
  echo "Private mode setup:"
  echo "- You can set a private-mode passcode now."
  echo "- This script will hash it and write the sha256 value into movies_config.json."
  echo "- Leave it empty if you want to skip for now."
  read -r -s -p "Enter a new private-mode passcode: " FIRST_PASSCODE
  echo
  if [[ -n "${FIRST_PASSCODE}" ]]; then
    read -r -s -p "Confirm the private-mode passcode: " SECOND_PASSCODE
    echo
    if [[ "${FIRST_PASSCODE}" != "${SECOND_PASSCODE}" ]]; then
      echo "ERROR: Passcodes did not match."
      exit 1
    fi
    write_private_passcode "${FIRST_PASSCODE}"
    echo "Private-mode passcode hash has been written to movies_config.json"
  fi
fi

HOST="$(read_config_value "host")"
PORT="$(read_config_value "port")"
ROOTS="$(read_config_value "root")"
PRIVATE_FOLDER="$(read_config_value "private_folder")"
PLEX_ENABLED="$(read_config_value "enable_plex_server")"
PLEX_BASE_URL="$(read_config_value "plex.base_url")"
MOUNT_SCRIPT="$(read_config_value "mount_script")"
AUTO_SCAN="$(read_config_value "auto_scan_on_start")"

if [[ -z "${HOST}" ]]; then
  HOST="0.0.0.0"
fi

if [[ -z "${PORT}" ]]; then
  PORT="9245"
fi

DISPLAY_HOST="${HOST}"
if [[ "${DISPLAY_HOST}" == "0.0.0.0" ]]; then
  DISPLAY_HOST="localhost"
fi

echo
echo "Config reminders:"
echo "- Set root to the folders you want Cat Theatre to scan."
echo "- Set private_folder if you want some folders hidden behind private mode."
echo "- Set private_passcode before using private mode. This script can generate the sha256 hash for you."
echo "- If you want Plex integration, enable enable_plex_server and fill plex.base_url plus plex.token."
echo "- If your media lives on sleeping or removable drives, set mount_script."
echo "- Keep transcode false unless you really want catalog-side sidecar files generated beside source media."
echo
echo "Current config summary:"
echo "- root: ${ROOTS:-<empty>}"
echo "- private_folder: ${PRIVATE_FOLDER:-<empty>}"
echo "- enable_plex_server: ${PLEX_ENABLED:-false}"
echo "- plex.base_url: ${PLEX_BASE_URL:-<empty>}"
echo "- mount_script: ${MOUNT_SCRIPT:-<empty>}"
echo "- auto_scan_on_start: ${AUTO_SCAN:-false}"
echo
echo "Open Cat Theatre at:"
echo "- http://${DISPLAY_HOST}:${PORT}"
echo
echo "Starting server..."
exec "${PYTHON_BIN}" "${SCRIPT_DIR}/movies_server.py" --config "${CONFIG_PATH}"
