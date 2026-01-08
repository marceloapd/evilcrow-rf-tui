#!/bin/bash

# Evil Crow RF V2 - Firmware Flash Script

set -e

cd "$(dirname "$0")/../firmware"

echo "🔧 Evil Crow RF V2 - Firmware Flash"
echo "===================================="
echo ""

# Check if platformio is installed
if ! command -v pio &> /dev/null; then
    echo "❌ PlatformIO not found!"
    echo ""
    echo "Install it with:"
    echo "  sudo pacman -S platformio    # Arch Linux"
    echo "  or"
    echo "  pipx install platformio       # Universal"
    exit 1
fi

# Build firmware
echo "📦 Building firmware..."
pio run

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""

# Flash firmware
echo "📤 Flashing to device..."
pio run --target upload

if [ $? -ne 0 ]; then
    echo "❌ Flash failed!"
    echo ""
    echo "Make sure:"
    echo "  - Evil Crow is connected via USB"
    echo "  - /dev/ttyUSB0 exists (or update platformio.ini)"
    echo "  - You have permission to access the port"
    exit 1
fi

echo "✅ Flash successful!"
echo ""

# Start monitor
read -p "📡 Start serial monitor? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Starting monitor... (Press Ctrl+C to exit)"
    echo ""
    pio device monitor
fi
