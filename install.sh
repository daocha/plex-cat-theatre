#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="plex-cat-theatre"
BIN_DIR="${HOME}/.local/bin"
CONFIG_PATH="${HOME}/movies_config.json"

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

require_cmd python3 "Install Python 3 first."

mkdir -p "${BIN_DIR}"

python3 -m pip install --user --upgrade pip >/dev/null
python3 -m pip install --user --upgrade "${PACKAGE_NAME}"

case "${SHELL##*/}" in
  zsh)
    append_path_to_profile "${HOME}/.zprofile"
    ;;
  bash)
    append_path_to_profile "${HOME}/.bash_profile"
    ;;
esac

if [[ ! -f "${CONFIG_PATH}" ]]; then
  "${BIN_DIR}/plex-cat-theatre-init" --config "${CONFIG_PATH}"
fi

echo "Installed ${PACKAGE_NAME} with python user-site packages"
echo "Commands are expected in ${BIN_DIR}"
echo "Config: ${CONFIG_PATH}"
echo
echo "If your current shell does not see the command yet, run:"
echo "export PATH=\"${BIN_DIR}:\$PATH\""
echo
echo "Start the server with:"
echo "plex-cat-theatre --config ${CONFIG_PATH}"
