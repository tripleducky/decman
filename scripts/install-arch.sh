#!/usr/bin/env bash
set -euo pipefail

# Convenience installer for Arch / Cachy OS
# - If a .pkg.tar.zst exists under pkg/, installs it with pacman -U
# - If no package is present and a PKGBUILD exists, runs makepkg -si
# Usage:
#   ./scripts/install-arch.sh        # installs pkg if present, otherwise builds+installs
#   ./scripts/install-arch.sh --install
#   ./scripts/install-arch.sh --build
#   ./scripts/install-arch.sh --pkg /path/to/decman-git-0.3.4-1-any.pkg.tar.zst

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG_DIR="$REPO_ROOT/pkg"
PKG_FILE=""

shopt -s nullglob
files=("$PKG_DIR"/*.pkg.tar.zst)
if [ ${#files[@]} -gt 0 ]; then
  PKG_FILE="${files[0]}"
fi

BUILD=false
INSTALL=false

print_usage() {
  cat <<EOF
Usage: $0 [--build] [--install] [--pkg <path>]

Default: if a .pkg.tar.zst is found in pkg/ the script installs it; otherwise it will build+install using PKGBUILD.

Options:
  --build       Only build the package with makepkg (does not force install)
  --install     Only install an existing .pkg.tar.zst (either auto-found or provided with --pkg)
  --pkg <path>  Use the provided package file when installing
  -h, --help    Show this help
EOF
}

if [ $# -eq 0 ]; then
  if [ -n "$PKG_FILE" ]; then
    INSTALL=true
  else
    BUILD=true
    INSTALL=true
  fi
else
  while [ $# -gt 0 ]; do
    case "$1" in
      --build) BUILD=true; shift ;;
      --install) INSTALL=true; shift ;;
      --pkg) PKG_FILE="$2"; shift 2 ;;
      -h|--help) print_usage; exit 0 ;;
      *) echo "Unknown arg: $1"; print_usage; exit 1 ;;
    esac
  done
fi

if $BUILD; then
  if [ ! -f "$REPO_ROOT/PKGBUILD" ]; then
    echo "No PKGBUILD found in repository root; cannot build." >&2
    exit 2
  fi

  echo "Building package with makepkg (run in $REPO_ROOT)..."
  (cd "$REPO_ROOT" && makepkg -s)

  # try to detect built package
  built=("$REPO_ROOT"/*.pkg.tar.zst)
  if [ ${#built[@]} -gt 0 ]; then
    PKG_FILE="${built[0]}"
    echo "Built package: $PKG_FILE"
  else
    echo "No .pkg.tar.zst produced in repository root after makepkg." >&2
  fi
fi

if $INSTALL; then
  if [ -z "$PKG_FILE" ]; then
    echo "No package file specified or found to install." >&2
    exit 3
  fi

  echo "Installing package: $PKG_FILE"
  sudo pacman -U "$PKG_FILE"
fi

echo "Done."
