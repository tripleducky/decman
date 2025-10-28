# decman

Declarative package & configuration manager for Arch Linux.

This repository contains `decman` (pkg: `decman-git`, version 0.3.4) — a small tool to help manage packages and configuration in a declarative way. The project includes a `PKGBUILD` and a prebuilt package in the `pkg/` directory, so installing on Arch Linux or Arch-based distributions such as Cachy OS is straightforward.

## Highlights

- Package name: `decman-git`
- Version: `0.3.4`
- License: see `LICENSE`

## Installation (recommended: Arch Linux / Cachy-OS)

Cachy OS is Arch-based; the same pacman/makepkg workflow applies.

Choose one of the options below depending on whether you have a prebuilt package, want to build locally from this repository, or prefer an AUR helper.

### 1) Install from the packaged file included in this repo

This repo contains a built package under `pkg/decman-git/`. If you already have the `.pkg.tar.zst` file (example: `decman-git-0.3.4-1-any.pkg.tar.zst`), install it with pacman:

```bash
sudo pacman -U /path/to/decman-git-0.3.4-1-any.pkg.tar.zst
```

Example (from this repository root): locate the package file and install it:

```bash
ls pkg
sudo pacman -U pkg/<the-package-file>.pkg.tar.zst
```

### Helper script: quick install/build wrapper

For convenience this repository includes a small helper script that automates the common flows: `scripts/install-arch.sh`.

- Make the script executable and run it from the repo root:

```bash
chmod +x scripts/install-arch.sh
./scripts/install-arch.sh
```

Behavior:
- If a `.pkg.tar.zst` exists under `pkg/` the script will install it with `sudo pacman -U`.
- If no package is found and a `PKGBUILD` is present the script will run `makepkg -s` to build, then install the produced package.

Flags:
- `--build` : only build with `makepkg -s` (does not force install)
- `--install` : only install an existing package (auto-detected or use `--pkg`)
- `--pkg <path>` : specify the package file to install

This script is intended to make local installs on Arch and Cachy OS fast and repeatable.

### 2) Build and install locally using the included `PKGBUILD`

If you prefer building from the repository (recommended if you want reproducible local builds), use `makepkg`:

```bash
sudo pacman -S --needed base-devel
makepkg -si
```

This will create a package file and optionally install it (`-s` installs dependencies, `-i` installs the package after building).

### 3) Install using an AUR helper (if an AUR package exists)

If an AUR package named `decman-git` exists, you can use an AUR helper such as `yay` or `paru`:

```bash
yay -S decman-git
```

### 4) Install with pip (developer / fallback)

You can also install the Python package manually (for development or testing). From the repo root:

```bash
python -m pip install --user .
```

This is not the recommended path for system-wide package management on Arch/Cachy OS — use the package-built flows above for system integration.

## Usage

After installation, the `decman` CLI should be available on your PATH (usually `/usr/bin/decman`). Get help with:

```bash
decman --help
python -m decman --help
```

For common operations, run the commands you normally use with the tool. If you installed via `makepkg` or `pacman -U`, the installed entrypoint is the `decman` script distributed under `/usr/bin/decman`.

## Uninstall

To remove the package installed via pacman:

```bash
sudo pacman -Rns decman-git
```

If you installed with pip:

```bash
python -m pip uninstall decman
```

## Troubleshooting

- If pacman reports missing dependencies when installing a package built outside your system, run `sudo pacman -Syu` and ensure `base-devel` is installed before `makepkg`.
- When installing/upgrading system packages use `sudo` or run commands as root.
- If the CLI is not found after installation, check `/usr/bin/` or the output of `pacman -Ql decman-git` to list installed files.

## Contributing

Development files live in `src/decman/`. The repo also contains tests in `tests/`.

Small ways to help:

- Run the test suite and add tests for regressions.
- Improve the `PKGBUILD` or add CI packaging workflows.
- Fix bugs and open PRs on the upstream repository: https://github.com/tripleducky/decman

## Files of interest in this repo

- `PKGBUILD` — Arch package build script (used by `makepkg`).
- `pkg/` — packaged layout and a built package tree.
- `LICENSE` — license text.

## License

See the `LICENSE` file in this repository for license details.

---

If you want, I can add a tiny helper script to install the built package from `pkg/` automatically, or add a small `scripts/install-arch.sh` wrapper; tell me which you prefer.
