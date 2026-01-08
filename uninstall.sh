#!/bin/bash
# Evil Crow RF V2 TUI - Uninstaller

echo "========================================"
echo "Evil Crow RF V2 TUI - Uninstaller"
echo "========================================"
echo ""

# Check if installed with pipx
if command -v pipx &> /dev/null && pipx list | grep -q evilcrow-tui; then
    echo "🗑️  Removing pipx installation..."
    pipx uninstall evilcrow-tui
    echo "✅ Uninstalled from pipx"
else
    echo "🗑️  Removing pip installation..."
    pip uninstall -y evilcrow-tui
    echo "✅ Uninstalled from pip"
fi

echo ""
echo "⚠️  User data preserved in ~/.evilcrow/"
echo "   To remove data: rm -rf ~/.evilcrow/"
echo ""
