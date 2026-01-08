#!/bin/bash
# Install Evil Crow TUI from local repository (for development)

set -e

echo "=========================================="
echo "Evil Crow RF V2 TUI - Local Install"
echo "=========================================="
echo ""

# Clean old builds
echo "🧹 Cleaning old builds..."
rm -rf src pkg tui/dist tui/build tui/src/*.egg-info
rm -f evilcrow-tui-git-*.pkg.tar.zst

echo "📦 Building package from local files..."
makepkg -f -p PKGBUILD.local

echo ""
echo "📥 Installing package..."
PACKAGE=$(ls -1 evilcrow-tui-git-*.pkg.tar.zst | head -1)
sudo pacman -U --noconfirm "$PACKAGE"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Add user to uucp group (if not done):"
echo "      sudo usermod -a -G uucp \$USER"
echo ""
echo "   2. Reload udev rules (if not done):"
echo "      sudo udevadm control --reload-rules && sudo udevadm trigger"
echo ""
echo "   3. Logout/login (if first install)"
echo ""
echo "   4. Flash firmware:"
echo "      cd /usr/share/evilcrow-tui-git/firmware && pio run --target upload"
echo ""
echo "   5. Run TUI:"
echo "      evilcrow"
echo ""
