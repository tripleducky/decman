#!/usr/bin/env bash
set -euo pipefail

# Bootstrap minimal dependencies and run decman from this repo
# This script will:
# - install python and git if missing
# - run decman with the provided source (defaults to example/my_source.py)
# Usage: ./scripts/bootstrap-arch.sh [--source /path/to/source.py]

if [ "$#" -eq 0 ]; then
  args=("--source" "example/my_source.py")
else
  args=("$@")
fi

if ! command -v python &>/dev/null || ! command -v git &>/dev/null; then
  echo "[BOOTSTRAP] Installing required packages: python git"
  sudo pacman -Sy --noconfirm --needed python git
fi

# Delegate to run-decman.sh which re-execs with sudo
"$(dirname "$0")/run-decman.sh" "${args[@]}"
