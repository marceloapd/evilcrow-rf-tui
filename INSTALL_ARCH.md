# Installing on Arch Linux

## Method 1: Build and Install Local Package (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/you/evilcrow-rf-tui.git
cd evilcrow-rf-tui

# Build package
makepkg -si

# This will:
# - Build the package
# - Install it with pacman
# - Handle all dependencies automatically
```

Done! The `evilcrow` command is now available system-wide.

## Method 2: Install from AUR (When Published)

```bash
# Using yay
yay -S evilcrow-tui-git

# Or using paru
paru -S evilcrow-tui-git
```

## After Installation

### 1. Add User to uucp Group

```bash
sudo usermod -a -G uucp $USER
```

### 2. Reload udev Rules

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 3. Logout and Login Again

This is required for group changes to take effect.

### 4. Flash Firmware

```bash
cd /usr/share/evilcrow-tui-git/firmware
pio run --target upload
```

### 5. Run TUI

```bash
evilcrow
```

## Uninstall

```bash
# If installed with makepkg
sudo pacman -R evilcrow-tui-git

# If installed with yay
yay -R evilcrow-tui-git
```

## Updating

### Local Package

```bash
cd evilcrow-rf-tui
git pull
makepkg -si
```

### AUR Package

```bash
yay -Syu evilcrow-tui-git
```

## Troubleshooting

### Permission Denied on /dev/ttyUSB0

Make sure you're in the `uucp` group and logged out/in:

```bash
groups  # Should show 'uucp'
ls -l /dev/ttyUSB0  # Should show 'crw-rw-rw-'
```

### Command Not Found

The package installs the `evilcrow` command to `/usr/bin/`, which should be in your PATH.

Check:
```bash
which evilcrow
```

### Dependencies Missing

Make sure you have the AUR helper and base-devel:

```bash
sudo pacman -S --needed base-devel git
```
