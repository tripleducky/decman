"""
Minimal decman configuration focused on declarative lists and settings.

This file intentionally contains no imperative logic; all behavior is handled
by decman itself. Adjust the lists and config flags below as desired.
"""

import decman
from decman import File
import decman.config as conf
conf.auto_clean_pacman_cache = True
conf.auto_remove_orphans = True

# --- Packages ---
# Pacman packages you want explicitly installed on this system.
# Keep this minimal at first; add more as you go.
decman.packages += [
    "accountsservice", 
    "adobe-source-han-sans-cn-fonts", 
    "adobe-source-han-sans-jp-fonts", 
    "adobe-source-han-sans-kr-fonts", 
   "alsa-firmware", 
    "alsa-plugins", 
    "alsa-utils", 
    "amd-ucode", 
    "awesome-terminal-fonts", 
    "base", 
    "base-devel", 
    "bash-completion", 
    "bind", 
    "bluez", 
    "bluez-hid2hci", 
    "bluez-libs", 
    "bluez-utils", 
    "btop", 
    "btrfs-progs", 
    "cachyos-grub-theme", 
    "cachyos-hello", 
    "cachyos-hooks", 
    "cachyos-kernel-manager", 
    "cachyos-keyring", 
    "cachyos-micro-settings", 
    "cachyos-mirrorlist", 
    "cachyos-packageinstaller", 
    "cachyos-plymouth-bootanimation", 
    "cachyos-rate-mirrors", 
    "cachyos-settings", 
    "cachyos-v3-mirrorlist", 
    "cachyos-v4-mirrorlist", 
    "cachyos-wallpapers", 
    "chwd", 
    "cpupower", 
    "cryptsetup",
    "device-mapper", 
    "dhclient", 
    "diffutils", 
    "dmidecode", 
    "dmraid", 
    "dnsmasq", 
    "dosfstools", 
    "duf", 
    "e2fsprogs", 
    "efibootmgr", 
    "efitools", 
    "egl-wayland", 
    "ethtool", 
    "exfatprogs", 
    "f2fs-tools", 
    "fastfetch", 
    "ffmpegthumbnailer",
    "fsarchiver",
    "glances",
    "grub", 
    "grub-hook", 
    "gst-libav", 
    "gst-plugin-pipewire", 
    "gst-plugin-va", 
    "gst-plugins-bad", 
    "gst-plugins-ugly", 
    "haveged", 
    "hdparm", 
    "hwdetect", 
    "hwinfo", 
    "inetutils", 
    "iptables-nft", 
    "iwd", 
    "jfsutils", 
    "less", 
    "lib32-mesa",
    "lib32-nvidia-utils", 
    "lib32-opencl-nvidia", 
    "lib32-vulkan-radeon", 
    "libdvdcss", 
    "libgsf", 
    "libopenraw", 
    "libva-nvidia-driver", 
    "libwnck3", 
    "linux-cachyos", 
    "linux-cachyos-headers", 
    "linux-cachyos-lts", 
    "linux-cachyos-lts-headers", 
    "linux-cachyos-lts-nvidia-open", 
    "linux-cachyos-nvidia-open", 
    "linux-firmware", 
    "logrotate", 
    "lsb-release",
    "lsscsi",
    "lvm2", 
    "man-db", 
    "man-pages", 
    "mdadm", 
    "meld",
    "mesa", 
    "mesa-utils", 
    "micro",
    "mkinitcpio", 
    "modemmanager",
    "mtools", 
    "nano",
    "nano-syntax-highlighting", 
    "netctl", 
    "networkmanager", 
    "networkmanager-openvpn", 
    "nfs-utils", 
    "nilfs-utils", 
    "niri", 
    "noto-color-emoji-fontconfig", 
    "noto-fonts", 
    "noto-fonts-cjk", 
    "noto-fonts-emoji", 
    "nss-mdns", 
    "ntp", 
    "nvidia-prime", 
    "nvidia-settings", 
    "nvidia-utils", 
    "octopi", 
    "opencl-nvidia", 
    "opendesktop-fonts", 
    "openssh", 
    "os-prober", 
    "pacman-contrib",
    "paru",
    "pavucontrol", 
    "perl", 
    "pipewire-alsa", 
    "pipewire-pulse", 
    "pkgfile", 
    "plocate", 
    "plymouth", 
    "poppler-glib", 
    "power-profiles-daemon", 
    "pv", 
    "python", 
    "python-defusedxml", 
    "python-packaging", 
    "rebuild-detector", 
    "reflector", 
    "ripgrep", 
    "rsync", 
    "rtkit", 
    "s-nail", 
    "sg3_utils",
    "smartmontools", 
    "sof-firmware", 
    "sudo", 
    "switcheroo-control", 
    "sysfsutils", 
    "texinfo", 
    "ttf-bitstream-vera", 
    "ttf-dejavu", 
    "ttf-liberation", 
    "ttf-meslo-nerd", 
    "ttf-opensans", 
    "ufw", 
    "unrar", 
    "unzip", 
    "upower", 
    "usb_modeswitch", 
    "usbutils",
    "vlc-plugins-all", 
    "vulkan-radeon", 
    "wget", 
    "which", 
    "wireless-regdb",  
    "wireplumber", 
    "wpa_supplicant", 
    "xdg-user-dirs", 
    "xdg-utils", 
    "xf86-input-libinput", 
    "xf86-video-amdgpu", 
    "xfsprogs", 
    "xl2tpd", 
    "xorg-server", 
    "xorg-xdpyinfo",
    "xorg-xinit", 
    "xorg-xinput", 
    "xorg-xkill", 
    "xorg-xrandr",
    "helium-browser-bin",
    
    "git",
    "curl",
    "python-requests",
    # Required for building AUR packages in a clean chroot via devtools
    "devtools",
    "xwayland-satellite",
    
    "ly",
    "alacritty",
    "fuzzel",
    "swww",
    "kanshi",
    "ttf-nerd-fonts-symbols",
    "just",
    
    # Dependencies for qml-niri plugin
    "qt6-base",
    "qt6-declarative",
    "cmake",
]

decman.aur_packages += [
  "quickshell",
  "visual-studio-code-bin",
  "github-desktop-bin",
]

# Packages you want decman to ignore (won't install or remove).
# Useful for tools you prefer to manage manually.
decman.ignored_packages += []

"""
Behavioral settings (optional)
"""

# Select preferred AUR helper ("yay" or "paru"). Decman will auto-install the
# helper package (yay-bin/paru-bin) via its builder if missing, and then use it
# to install/upgrade declared AUR packages.
conf.aur_helper = "paru"
conf.aur_helper_package = "paru-bin"
conf.use_aur_helper_for_aur = True

# Install pacman/yay guard wrappers to block manual sync/remove/upgrade outside decman runs.
conf.enable_pkgmgr_wrappers = True

# After package operations, show pacman cache info and optionally offer `pacman -Sc`.
conf.prompt_clean_pacman_cache = True

# niri-qml installation options
#   "off"    - do nothing (default)
#   "aur"    - install via AUR (set conf.qml_niri_aur_package)
#   "source" - build from source (uses conf.qml_niri_repo_url, *_local_clone, *_build_dir)
# Examples:
conf.qml_niri_install = "source"
conf.qml_niri_repo_url = "https://github.com/tripleducky/qml-niri.git"

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
