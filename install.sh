#!/bin/bash
# Evil Crow RF V2 TUI - Easy Installer

set -e

echo "========================================"
echo "Evil Crow RF V2 TUI - Installer"
echo "========================================"
echo ""

# Check if pipx is available (recommended)
if command -v pipx &> /dev/null; then
    echo "✅ pipx found - using pipx for installation (recommended)"
    echo ""

    cd tui
    pipx install .

    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Run with: evilcrow"
    echo ""

# Otherwise use pip with user install
else
    echo "⚠️  pipx not found, using pip --user instead"
    echo "   (Install pipx for better isolation: sudo pacman -S python-pipx)"
    echo ""

    cd tui
    pip install --user .

    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "Run with: evilcrow"
    echo ""
    echo "⚠️  If 'evilcrow' command not found, add ~/.local/bin to PATH:"
    echo "   echo 'export PATH=\$PATH:~/.local/bin' >> ~/.bashrc"
    echo "   source ~/.bashrc"
    echo ""
fi

echo "📚 Next steps:"
echo "   1. Flash firmware: cd firmware && pio run --target upload"
echo "   2. Run TUI: evilcrow"
echo ""
