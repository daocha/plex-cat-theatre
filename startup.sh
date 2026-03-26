#!/usr/bin/env bash
set -euo pipefail

# Starter bootstrap script for Cat Theatre.
# It prepares a local Python virtual environment, installs dependencies,
# creates a working config from the sample on first run, and starts the server.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
CONFIG_PATH="${SCRIPT_DIR}/movies_config.json"
SAMPLE_CONFIG_PATH="${SCRIPT_DIR}/movies_config.sample.json"
VENV_PATH="${SCRIPT_DIR}/.venv"
PYTHON_BIN="${VENV_PATH}/bin/python"
PIP_BIN="${VENV_PATH}/bin/pip"
INSTALL_STATE_FILE_NAME=".plex-cat-theatre-install-state"
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"
LOCAL_PRETEND_VERSION="${SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PLEX_CAT_THEATRE:-0.0.dev0}"

require_cmd() {
  local cmd="$1"
  local help_text="$2"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: Missing required command: ${cmd}"
    echo "Hint: ${help_text}"
    exit 1
  fi
}

compute_install_fingerprint() {
  local files=()
  local file
  for file in pyproject.toml setup.py; do
    if [[ -f "${SCRIPT_DIR}/${file}" ]]; then
      files+=("${SCRIPT_DIR}/${file}")
    fi
  done
  if [[ "${#files[@]}" -eq 0 ]]; then
    printf 'no-packaging-files\n'
    return
  fi
  shasum -a 256 "${files[@]}" | shasum -a 256 | awk '{print $1}'
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

ensure_thumbs_dir_from_config() {
  "${PYTHON_BIN}" - "${CONFIG_PATH}" <<'PY'
import json
import sys
from pathlib import Path

cfg_path = Path(sys.argv[1]).expanduser().resolve()
with cfg_path.open("r", encoding="utf-8") as handle:
    cfg = json.load(handle)

thumbs_dir = str(cfg.get("thumbs_dir", "") or "").strip()
if not thumbs_dir:
    thumbs_path = cfg_path.parent / "cache" / "thumbnails"
else:
    thumbs_path = Path(thumbs_dir).expanduser()
    if not thumbs_path.is_absolute():
        thumbs_path = cfg_path.parent / thumbs_path

thumbs_path.mkdir(parents=True, exist_ok=True)
print(thumbs_path.resolve())
PY
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

if [[ ! -d "${VENV_PATH}" ]]; then
  echo "Creating local virtual environment at ${VENV_PATH}"
  python3 -m venv "${VENV_PATH}"
fi

# Upgrade pip first so a clean machine can install the project reliably.
"${PYTHON_BIN}" -m pip install --upgrade pip >/dev/null
INSTALL_STATE_FILE="${VENV_PATH}/${INSTALL_STATE_FILE_NAME}"
CURRENT_INSTALL_FINGERPRINT="$(compute_install_fingerprint)"
STORED_INSTALL_FINGERPRINT=""
if [[ -f "${INSTALL_STATE_FILE}" ]]; then
  STORED_INSTALL_FINGERPRINT="$(<"${INSTALL_STATE_FILE}")"
fi

NEEDS_REINSTALL=0
if [[ "${FORCE_REINSTALL}" == "1" ]]; then
  NEEDS_REINSTALL=1
elif ! "${PYTHON_BIN}" -c "import cat_theatre_init, movies_server, passcode" >/dev/null 2>&1; then
  NEEDS_REINSTALL=1
elif [[ "${CURRENT_INSTALL_FINGERPRINT}" != "${STORED_INSTALL_FINGERPRINT}" ]]; then
  NEEDS_REINSTALL=1
fi

if [[ "${NEEDS_REINSTALL}" == "1" ]]; then
  echo "Installing local package into ${VENV_PATH}"
  SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PLEX_CAT_THEATRE="${LOCAL_PRETEND_VERSION}" \
    "${PIP_BIN}" install -e "${SCRIPT_DIR}"
  printf '%s\n' "${CURRENT_INSTALL_FINGERPRINT}" > "${INSTALL_STATE_FILE}"
else
  echo "Existing editable install detected; skipping reinstall."
fi

THUMBS_PATH="$(ensure_thumbs_dir_from_config)"

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
echo "- thumbs_dir: ${THUMBS_PATH:-<empty>}"
echo
echo "Open Cat Theatre at:"
echo "- http://${DISPLAY_HOST}:${PORT}"
echo
echo "Starting server..."
exec "${PYTHON_BIN}" "${SCRIPT_DIR}/movies_server.py" --config "${CONFIG_PATH}"
