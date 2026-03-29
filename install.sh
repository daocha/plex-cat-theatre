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

append_path_to_profile() {
  local profile_path="$1"
  local line='export PATH="$HOME/.local/bin:$PATH"'
  touch "${profile_path}"
  if ! grep -Fqx "${line}" "${profile_path}"; then
    printf '\n%s\n' "${line}" >> "${profile_path}"
  fi
}

resolve_user_home() {
  "$PYTHON_BIN" - <<'PY'
from pathlib import Path
import os
import pwd

sudo_user = os.getenv("SUDO_USER", "").strip()
if sudo_user and sudo_user != "root":
    try:
        print(pwd.getpwnam(sudo_user).pw_dir)
    except KeyError:
        print(Path.home())
else:
    print(Path.home())
PY
}

require_cmd "${PYTHON_BIN}" "Install Python 3 first."

TARGET_HOME="$(resolve_user_home)"
CONFIG_PATH="${TARGET_HOME}/movies_config.json"

"${PYTHON_BIN}" -m pip install --upgrade pip >/dev/null
"${PYTHON_BIN}" -m pip install --upgrade "${PACKAGE_NAME}"

BIN_DIR="$("${PYTHON_BIN}" - <<'PY'
import sysconfig
print(sysconfig.get_path("scripts"))
PY
)"

if [[ "${BIN_DIR}" == "${HOME}/.local/bin" ]]; then
  mkdir -p "${BIN_DIR}"
  case "${SHELL##*/}" in
    zsh)
      append_path_to_profile "${HOME}/.zprofile"
      ;;
    bash)
      append_path_to_profile "${HOME}/.bash_profile"
      ;;
  esac
fi

if [[ ! -f "${CONFIG_PATH}" ]]; then
  "${BIN_DIR}/plex-cat-theatre-init" --config "${CONFIG_PATH}"
fi

echo "Installed ${PACKAGE_NAME} using the active python3 environment"
echo "Commands are expected in ${BIN_DIR}"
echo "Config: ${CONFIG_PATH}"
echo
if [[ "${BIN_DIR}" == "${HOME}/.local/bin" ]]; then
  echo "If your current shell does not see the command yet, run:"
  echo "export PATH=\"${BIN_DIR}:\$PATH\""
  echo
fi
echo "Start the server with:"
echo "plex-cat-theatre --config ${CONFIG_PATH}"
