"""
Module containing the CLI Application.
"""

import argparse
import os
import shutil
import subprocess
import sys
import traceback

import decman
import decman.config as conf
import decman.error as err
import decman.lib as l
from decman.lib import fpm


def main():
    """
    Main entry for the CLI app
    """

    sys.pycache_prefix = os.path.join(conf.pkg_cache_dir, "python/")

    parser = argparse.ArgumentParser(
        prog="decman",
        description="Declarative package & configuration manager for Arch Linux",
        epilog="See more help at: https://github.com/kiviktnm/decman",
    )

    parser.add_argument(
        "--source", action="store", help="python file containing configuration"
    )
    parser.add_argument(
        "--print",
        "--dry-run",
        action="store_true",
        default=False,
        help="print what would happen as a result of running decman",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="show debug output"
    )
    parser.add_argument(
        "--no-packages",
        action="store_true",
        default=False,
        help="don't upgrade any packages (including foreign packages)",
    )
    parser.add_argument(
        "--no-foreign-packages",
        action="store_true",
        default=False,
        help="don't upgrade foreign packages",
    )
    parser.add_argument(
        "--no-files", action="store_true", default=False, help="don't install any files"
    )
    parser.add_argument(
        "--no-systemd-units",
        action="store_true",
        default=False,
        help="don't enable/disable systemd units",
    )
    parser.add_argument(
        "--no-commands",
        action="store_true",
        default=False,
        help="don't run user specified commands",
    )
    parser.add_argument(
        "--upgrade-devel",
        action="store_true",
        default=False,
        help="upgrade devel packages",
    )
    parser.add_argument(
        "--force-build",
        action="store_true",
        default=False,
        help="force building of packages that are already cached",
    )

    args = parser.parse_args()

    if not _is_root():
        l.print_error("Not running as root. Please run decman as root.")
        sys.exit(1)

    original_wd = os.getcwd()

    try:
        store = l.Store.restore()
    except err.UserFacingError as error:
        l.print_error(error.user_facing_msg)
        for line in traceback.format_exc().splitlines():
            l.print_debug(line)
        sys.exit(1)

    errored = False

    try:
        opts = _set_up(store, args)
        # Override debug_output if cli option is used
        if args.debug:
            conf.debug_output = True
            conf.suppress_command_output = False
        # When print cli option is used, show info output
        if args.print:
            conf.quiet_output = False
        Core(store, opts).run()
    except err.UserFacingError as error:
        l.print_error(error.user_facing_msg)
        for line in traceback.format_exc().splitlines():
            l.print_debug(line)
        errored = True
    except decman.UserRaisedError as user_error:
        l.print_error(f"Error encountered while running the source: {user_error}")
        errored = True

    # Save even when an error has occurred, since this avoids repeating steps like building pkgs.
    try:
        store.save()
    except err.UserFacingError as error:
        l.print_error(error.user_facing_msg)
        for line in traceback.format_exc().splitlines():
            l.print_debug(line)
        errored = True

    os.chdir(original_wd)
    if errored:
        sys.exit(2)


def _set_up(store: l.Store, args):
    source = store.source_file
    source_changed = False
    if args.source is not None:
        source = args.source
        source_changed = True

    if source is None:
        l.print_error(
            "Source was not specified. Please specify a source with the '--source' argument."
        )
        l.print_info("Decman will remember the previously specified source.")
        sys.exit(1)

    if source_changed or not store.allow_running_source_without_prompt:
        l.print_warning(f"Decman will run the file '{source}' as root!")
        l.print_warning(
            "Only proceed if you trust the file completely. The file can also import other files."
        )

        if not l.prompt_confirm("Proceed?", default=False):
            sys.exit(1)

        if l.prompt_confirm("Remember this choice?", default=False):
            store.allow_running_source_without_prompt = True

    source_path = os.path.abspath(source)
    source_dir = os.path.dirname(source_path)
    store.source_file = source_path

    try:
        with open(source_path, "rt", encoding="utf-8") as file:
            content = file.read()
    except OSError as e:
        raise err.UserFacingError(
            f"Failed to read source file '{store.source_file}'."
        ) from e

    os.chdir(source_dir)
    sys.path.append(".")
    exec(content)

    return (
        args.print,
        not args.no_packages,
        not args.no_foreign_packages,
        not args.no_files,
        not args.no_systemd_units,
        not args.no_commands,
        args.upgrade_devel,
        args.force_build,
    )


class Core:
    """
    Contains the main logic of decman.
    """

    def __init__(self, store: l.Store, opts):
        (
            self.only_print,
            self.update_packages,
            self.update_foreign_packages,
            self.update_files,
            self.update_units,
            self.run_commands,
            self.upgrade_devel,
            self.force_build,
        ) = opts

        self.store = store
        self.source = _resolve_source()
        self.pacman = l.Pacman()
        self.systemctl = l.Systemd(store)
        self.fpkg_search = fpm.ExtendedPackageSearch(self.pacman)

        for upkg in self.source.all_user_pkgs():
            self.fpkg_search.add_user_pkg(
                fpm.PackageInfo.from_user_package(upkg, self.pacman)
            )

        self.fpm = fpm.ForeignPackageManager(store, self.pacman, self.fpkg_search)

    def run(self):
        """
        Run the main logic of decman.
        """
        if self.update_units:
            self._disable_units()

        if self.update_files:
            self._create_and_remove_files()

        if self.update_packages:
            self._remove_pkgs()
            self._upgrade_pkgs()
            self._install_pkgs()
            # Offer to remove orphan packages after package operations
            if not self.only_print:
                self._offer_remove_orphans()

        if self.update_units:
            self._enable_units()

        if self.run_commands:
            self._run_modules()
            all_enabled_modules = {}
            for mod, version in self.source.all_enabled_modules():
                all_enabled_modules[mod] = version
            # Enabled modules are really only stored for commands,
            # so they can be set only when the commands were exacuted.
            self.store.enabled_modules = all_enabled_modules

    def _disable_units(self):
        to_disable = self.source.units_to_disable(self.store)
        l.print_list("Disabling systemd units:", to_disable)
        if to_disable:
            l.print_info("Disabled systemd units won't be stopped automatically.")
        if not self.only_print:
            self.systemctl.disable_units(to_disable)

        user_units_to_disable = self.source.user_units_to_disable(self.store)
        for user, units in user_units_to_disable.items():
            l.print_list(f"Disabling systemd units for {user}:", units)
            if not self.only_print:
                self.systemctl.disable_user_units(units, user)

    def _remove_pkgs(self):
        currently_installed = self.pacman.get_installed()
        to_remove = self.source.packages_to_remove(currently_installed)
        l.print_list("Removing packages:", to_remove)
        if not self.only_print:
            self.pacman.remove(to_remove)

    def _upgrade_pkgs(self):
        l.print_summary("Upgrading packages.")
        if not self.only_print:
            self.pacman.upgrade()
            # Prefer built-in FPM unless disabled or yay is preferred
            if conf.enable_fpm and self.update_foreign_packages:
                self.fpm.upgrade(
                    self.upgrade_devel, self.force_build, self.source.ignored_packages
                )
            elif (
                self.update_foreign_packages
                and conf.use_yay_for_aur_if_available
                and shutil.which("yay") is not None
            ):
                # Ensure declared AUR packages are up to date via yay (skips up-to-date)
                sudo_user = os.environ.get("SUDO_USER")
                if sudo_user:
                    aur_list = sorted(list(self.source.aur_packages))
                    if aur_list:
                        l.print_summary(
                            "Installing/upgrading declared AUR packages with yay (skips up-to-date):"
                        )
                        l.print_list("AUR packages:", aur_list)
                        decman.prg(["yay", "-S", "--needed"] + aur_list, user=sudo_user)
                else:
                    l.print_warning(
                        "SUDO_USER not set; cannot run yay as a regular user. Skipping yay upgrade."
                    )

    def _install_pkgs(self):
        currently_installed = self.pacman.get_installed()
        to_install_pacman = self.source.pacman_packages_to_install(currently_installed)
        to_install_fpm = self.source.foreign_packages_to_install(currently_installed)

        l.print_list("Installing pacman packages:", to_install_pacman)

        # fpm prints a summary so no need to print it twice
        if self.only_print:
            l.print_list("Installing foreign packages:", to_install_fpm)

        if not self.only_print:
            self.pacman.install(to_install_pacman)
            if self.update_foreign_packages:
                # Split foreign packages to AUR and user packages
                aur_declared = self.source.aur_packages
                aur_to_install = [p for p in to_install_fpm if p in aur_declared]
                user_pkg_to_install = [p for p in to_install_fpm if p not in aur_declared]

                used_yay = False
                if conf.use_yay_for_aur_if_available and shutil.which("yay") is not None and aur_to_install:
                    sudo_user = os.environ.get("SUDO_USER")
                    if sudo_user:
                        l.print_summary(
                            "Installing declared AUR packages with yay (skips up-to-date):"
                        )
                        l.print_list("AUR packages:", aur_to_install)
                        decman.prg(["yay", "-S", "--needed"] + aur_to_install, user=sudo_user)
                        used_yay = True
                    else:
                        l.print_warning(
                            "SUDO_USER not set; cannot run yay as a regular user. Falling back to decman's builder if enabled."
                        )

                remaining = user_pkg_to_install + ([] if used_yay else aur_to_install)
                if remaining:
                    if conf.enable_fpm:
                        self.fpm.install(remaining, force=self.force_build)
                    else:
                        # Can't install remaining via fpm; warn the user
                        l.print_warning(
                            "Foreign package installation skipped because both decman FPM is disabled and yay was not used."
                        )

    def _create_and_remove_files(self):
        l.print_summary("Installing files.")

        all_created = self.source.create_all_files(self.only_print)
        # Optionally add pacman/yay guard wrappers
        all_created.extend(self._maybe_install_pkgmgr_wrappers())
        to_remove = self.source.files_to_remove(self.store, all_created)

        l.print_list("Ensured files are up to date:", all_created, elements_per_line=1)
        l.print_list("Removing files:", to_remove, elements_per_line=1)

        if self.only_print:
            return

        for file in to_remove:
            try:
                os.remove(file)
            except OSError as e:
                l.print_error(f"{e}")
                l.print_warning(f"Failed to remove file: {file}")

        self.store.created_files = all_created

    def _maybe_install_pkgmgr_wrappers(self) -> list[str]:
        """
        Installs pacman/yay guard wrappers into /usr/local/bin if enabled.
        Returns the list of created file paths (for tracking/removal).
        """
        created: list[str] = []
        if self.only_print or not conf.enable_pkgmgr_wrappers:
            return created

        src_path = self.store.source_file or "/path/to/source.py"

        pacman_wrapper_content = (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "PACMAN_BIN=/usr/bin/pacman\n\n"
            "check_tree() {\n"
            "  local p=$PPID\n"
            "  local depth=0\n"
            "  while [[ $p -gt 1 && $depth -lt 12 ]]; do\n"
            "    if grep -qa 'decman' \"/proc/$p/cmdline\" 2>/dev/null; then\n"
            "      return 0\n"
            "    fi\n"
            "    p=$(awk '{print $4}' \"/proc/$p/stat\" 2>/dev/null || echo 1)\n"
            "    depth=$((depth+1))\n"
            "  done\n"
            "  return 1\n"
            "}\n\n"
            "if [[ \"${DECMAN_ALLOW:-}\" == \"1\" ]] || check_tree; then\n"
            "  exec \"$PACMAN_BIN\" \"$@\"\n"
            "fi\n\n"
            "block=false\n"
            "for arg in \"$@\"; do\n"
            "  if [[ \"$arg\" == \"--\" ]]; then break; fi\n"
            "  if [[ \"$arg\" == --sync || \"$arg\" == --remove || \"$arg\" == --upgrade ]]; then\n"
            "    block=true\n"
            "  fi\n"
            "  if [[ \"$arg\" == -* ]]; then\n"
            "    [[ \"$arg\" == *S* ]] && block=true\n"
            "    [[ \"$arg\" == *U* ]] && block=true\n"
            "    [[ \"$arg\" == *R* ]] && block=true\n"
            "  fi\n"
            "done\n\n"
            "if $block; then\n"
            "  cat >&2 <<'EOF'\n"
            "Manual pacman install/remove/upgrade blocked by decman guard (pre-download).\n\n"
            "Please update your decman source and run:\n"
            f"  sudo decman --source {src_path}\n\n"
            "To bypass once (not recommended):\n"
            "  sudo DECMAN_ALLOW=1 pacman <args>\n"
            "EOF\n"
            "  exit 1\n"
            "fi\n\n"
            "exec \"$PACMAN_BIN\" \"$@\"\n"
        )

        yay_wrapper_content = (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "YAY_BIN=/usr/bin/yay\n\n"
            "check_tree() {\n"
            "  local p=$PPID\n"
            "  local depth=0\n"
            "  while [[ $p -gt 1 && $depth -lt 12 ]]; do\n"
            "    if grep -qa 'decman' \"/proc/$p/cmdline\" 2>/dev/null; then\n"
            "      return 0\n"
            "    fi\n"
            "    p=$(awk '{print $4}' \"/proc/$p/stat\" 2>/dev/null || echo 1)\n"
            "    depth=$((depth+1))\n"
            "  done\n"
            "  return 1\n"
            "}\n\n"
            "if [[ \"${DECMAN_ALLOW:-}\" == \"1\" ]] || check_tree; then\n"
            "  exec \"$YAY_BIN\" \"$@\"\n"
            "fi\n\n"
            "block=false\n"
            "for arg in \"$@\"; do\n"
            "  if [[ \"$arg\" == \"--\" ]]; then break; fi\n"
            "  if [[ \"$arg\" == --sync || \"$arg\" == --remove || \"$arg\" == --upgrade ]]; then\n"
            "    block=true\n"
            "  fi\n"
            "  if [[ \"$arg\" == -* ]]; then\n"
            "    [[ \"$arg\" == *S* ]] && block=true\n"
            "    [[ \"$arg\" == *U* ]] && block=true\n"
            "    [[ \"$arg\" == *R* ]] && block=true\n"
            "  fi\n"
            "done\n\n"
            "if $block; then\n"
            "  cat >&2 <<'EOF'\n"
            "Manual yay install/remove/upgrade blocked by decman guard (pre-download).\n\n"
            "Please update your decman source and run:\n"
            f"  sudo decman --source {src_path}\n\n"
            "To bypass once (not recommended):\n"
            "  sudo DECMAN_ALLOW=1 yay <args>\n"
            "EOF\n"
            "  exit 1\n"
            "fi\n\n"
            "exec \"$YAY_BIN\" \"$@\"\n"
        )

        wrappers = {
            "/usr/local/bin/pacman": pacman_wrapper_content,
            "/usr/local/bin/yay": yay_wrapper_content,
        }

        for target, content in wrappers.items():
            try:
                file = decman.File(content=content, permissions=0o755)
                file.copy_to(target)
                created.append(target)
            except OSError as e:
                l.print_error(f"{e}")
                l.print_warning(f"Failed to install wrapper: {target}")
        return created

    def _offer_clean_pkg_cache(self):
        """
        Show pacman cache summary and optionally prompt to clean uninstalled/old packages.
        """
        if self.only_print or not conf.prompt_clean_pacman_cache:
            return

        cache_dir = "/var/cache/pacman/pkg"
        try:
            # Get cache size
            result = subprocess.run(
                ["du", "-sh", cache_dir],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode == 0:
                cache_size = result.stdout.decode().strip().split()[0]
                l.print_summary(f"Package cache size: {cache_size}")

            # Count cached packages
            cache_files = len(
                [
                    f
                    for f in os.listdir(cache_dir)
                    if f.endswith((".pkg.tar.zst", ".pkg.tar.xz", ".pkg.tar.gz", ".pkg.tar"))
                ]
            )
            if cache_files == 0:
                return

            l.print_summary(f"Found {cache_files} cached package file(s).")
            if l.prompt_confirm(
                "Clean uninstalled and old cached packages? (pacman -Sc)", default=False
            ):
                decman.prg(["pacman", "-Sc", "--noconfirm"])
                l.print_summary("Package cache cleaned.")
        except Exception as e:  # pylint: disable=broad-except
            l.print_warning(f"Failed to check/clean package cache: {e}")

    def _enable_units(self):
        to_enable = self.source.units_to_enable(self.store)
        l.print_list("Enabling systemd units:", to_enable)
        if to_enable:
            l.print_info("Enabled systemd units won't be started automatically.")
        if not self.only_print:
            self.systemctl.enable_units(to_enable)

        user_units_to_enable = self.source.user_units_to_enable(self.store)
        for user, units in user_units_to_enable.items():
            l.print_list(f"Enabling systemd units for {user}:", units)
            if not self.only_print:
                self.systemctl.enable_user_units(units, user)

    def _run_modules(self):
        l.print_summary("Running on enable hooks.")
        if not self.only_print:
            self.source.run_on_enable(self.store)

        l.print_summary("Running after version change hooks.")
        if not self.only_print:
            self.source.run_after_version_change(self.store)

        l.print_summary("Running on disable hooks.")
        if not self.only_print:
            self.source.run_on_disable(self.store)

        l.print_summary("Running after update hooks.")
        if not self.only_print:
            self.source.run_after_update()

    def _offer_remove_orphans(self):
        """
        Interactively offer to remove orphaned packages.
        """
        orphans = self.pacman.list_orphans()
        if not orphans:
            return
        l.print_list(
            "Orphan packages detected (installed as deps, no longer required):",
            orphans,
        )
        if l.prompt_confirm("Remove these orphan packages now?", default=False):
            self.pacman.remove_orphans(orphans)


def _resolve_source() -> l.Source:
    enabled_systemd_user_units = {}
    for user, units in decman.enabled_systemd_user_units.items():
        enabled_systemd_user_units[user] = set(units)

    return l.Source(
        pacman_packages=set(decman.packages),
        aur_packages=set(decman.aur_packages),
        user_packages=set(decman.user_packages),
        ignored_packages=set(decman.ignored_packages),
        systemd_units=set(decman.enabled_systemd_units),
        systemd_user_units=enabled_systemd_user_units,
        files=decman.files,
        directories=decman.directories,
        modules=set(decman.modules),
    )


def _is_root() -> bool:
    return os.geteuid() == 0
