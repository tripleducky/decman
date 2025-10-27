"""
Minimal decman configuration focused on declarative lists and settings.

This file intentionally contains no imperative logic; all behavior is handled
by decman itself. Adjust the lists and config flags below as desired.
"""

import decman
from decman import File
import decman.config as conf

# --- Packages ---
# Pacman packages you want explicitly installed on this system.
# Keep this minimal at first; add more as you go.
decman.packages += [
    "base",
    "base-devel",
    "bluez",
    "bluez-utils",
    "efibootmgr",
    "grub",
    "gst-plugin-pipewire",
    "intel-ucode",
    "libpulse",
    "linux",
    "linux-firmware",
    "pipewire",
    "pipewire-alsa",
    "pipewire-jack",
    "pipewire-pulse",
    "wireplumber",
    "zram-generator",
    
    "git",
    "networkmanager",
    "msedit",      # editor example; change/remove as you like
    "curl",
    # Required for building AUR packages in a clean chroot via devtools
    "devtools",
    
    "ly",
    "alacritty",
    "fuzzel",
    "niri",
    "swww",
    "xdg-desktop-portal-gnome",
    "kanshi",
    "ttf-nerd-fonts-symbols",
    "just",
    
    # Dependencies for qml-niri plugin
    "qt6-base",
    "qt6-declarative",
    "cmake",
]

decman.aur_packages += [
  "decman",
  "helium-browser-bin",
  "quickshell",
  "visual-studio-code-bin",
  "github-desktop-bin",
]

# Packages you want decman to ignore (won't install or remove).
# Useful for tools you prefer to manage manually.
decman.ignored_packages += ["yay-bin"]

"""
Behavioral settings (optional)
"""

# Prefer using yay for AUR packages if available (run as SUDO_USER) instead of decman's builder.
conf.use_yay_for_aur_if_available = True

# Install pacman/yay guard wrappers to block manual sync/remove/upgrade outside decman runs.
conf.enable_pkgmgr_wrappers = True

# After package operations, show pacman cache info and optionally offer `pacman -Sc`.
conf.prompt_clean_pacman_cache = True

# --- AUR packages ---
# To let decman manage itself from AUR after it's installed:
# decman.aur_packages += ["decman"]

# If you add AUR packages that require PGP verification and you have custom keys,
# you can configure the build user and GPG home like this:
# import os, decman.config
# os.environ["GNUPGHOME"] = "/home/youruser/.gnupg"
# decman.config.makepkg_user = "youruser"

"""
Files to ensure exist
"""

decman.files["/etc/vconsole.conf"] = File(content="KEYMAP=us", encoding="utf-8")

# --- Directories ---
# Example (uncomment and adjust) to copy a dotfiles dir recursively to target:
# from decman import Directory
# decman.directories["/home/youruser/.config/app/"] = Directory(
#     source_directory="./files/app-config", owner="youruser"
# )


# --- systemd units ---
# Decman will enable these units if not already enabled. It does NOT start them automatically.
# Start them once manually or reboot.
decman.enabled_systemd_units += ["NetworkManager.service", "ly.service"]

"""
No modules defined here on purpose. Keep behavior declarative in this file.
"""
