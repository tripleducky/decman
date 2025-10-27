#!/usr/bin/env bash
set -euo pipefail

# Run decman from this repository without installing it system-wide.
# Usage: ./scripts/run-decman.sh --source /path/to/source.py [other options]

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  exec sudo --preserve-env=PYTHONPATH "$0" "$@"
fi

# Resolve repo dir from this script path
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd)"

export PYTHONPATH="${REPO_DIR}/src:${PYTHONPATH-}"
exec python -m decman "$@"
