#!/usr/bin/env bash
set -euo pipefail

# Copy your decman source to ~/.config/decman and run decman once from this repo.
# This will apply your config and install decman as a system-wide package (via AUR),
# since the example my_source.py declares decman under decman.aur_packages.
#
# Usage:
#   scripts/setup-my-config.sh [--source path/to/source.py] [--force]
#
# Notes:
# - Uses sudo as needed.
# - Runs decman from this repo (not yet installed system-wide).
# - If you enabled pacman/yay wrappers in your source, they will be created.

SOURCE_IN_REPO="example/my_source.py"
FORCE="false"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      SOURCE_IN_REPO="$2"; shift 2 ;;
    --force)
      FORCE="true"; shift ;;
    *) echo "Unknown argument: $1"; exit 2 ;;
  esac
done

# Resolve repo root
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd)"

SRC_PATH="${REPO_DIR}/${SOURCE_IN_REPO}"
if [[ ! -f "${SRC_PATH}" ]]; then
  echo "Source not found: ${SRC_PATH}" >&2
  exit 1
fi

# If running under sudo, install into the invoking user's home rather than /root
if [[ $(id -u) -eq 0 && -n "${SUDO_USER-}" ]]; then
  INVOKER_HOME=$(getent passwd "${SUDO_USER}" | cut -d: -f6)
  TARGET_DIR="${INVOKER_HOME}/.config/decman"
else
  TARGET_DIR="${HOME}/.config/decman"
fi
TARGET_PATH="${TARGET_DIR}/my_source.py"

mkdir -p "${TARGET_DIR}"

# If a target already exists, back it up before replacing
if [[ -e "${TARGET_PATH}" ]]; then
  BACKUP_PATH="${TARGET_PATH}.bak-$(date +%Y%m%d-%H%M%S)"
  mv -f "${TARGET_PATH}" "${BACKUP_PATH}"
  echo "Existing source backed up: ${BACKUP_PATH}"
fi

cp -f "${SRC_PATH}" "${TARGET_PATH}"
echo "Copied ${SRC_PATH} -> ${TARGET_PATH}"

# Ensure minimal deps and run decman from repo
"${REPO_DIR}/scripts/bootstrap-arch.sh" --source "${TARGET_PATH}"
