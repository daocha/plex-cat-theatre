#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="plex-cat-theatre"
PYTHON_BIN="python3"

require_cmd() {
  local cmd="$1"
  local help_text="$2"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: Missing required command: ${cmd}"
    echo "Hint: ${help_text}"
    exit 1
  fi
}

require_cmd "${PYTHON_BIN}" "Install Python 3 first."

"${PYTHON_BIN}" -m pip install --upgrade pip >/dev/null
"${PYTHON_BIN}" -m pip install --upgrade "${PACKAGE_NAME}"

BIN_DIR="$("${PYTHON_BIN}" - <<'PY'
import sysconfig
print(sysconfig.get_path("scripts"))
PY
)"

CONFIG_PATH="$("${PYTHON_BIN}" - <<'PY'
from cat_theatre_init import DEFAULT_CONFIG_PATH
print(DEFAULT_CONFIG_PATH)
PY
)"

if [[ ! -f "${CONFIG_PATH}" ]]; then
  "${BIN_DIR}/plex-cat-theatre-init"
fi

echo "Installed ${PACKAGE_NAME} using the active python3 environment"
echo "Commands are expected in ${BIN_DIR}"
echo "Config: ${CONFIG_PATH}"
echo
echo "Start the server with:"
echo "plex-cat-theatre --config ${CONFIG_PATH}"
