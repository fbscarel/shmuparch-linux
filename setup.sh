#!/bin/bash
# ShmupArch Linux Setup Script
# Downloads cores and creates necessary directories

set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "   ShmupArch Linux Setup"
echo "   Based on ShmupArch 7.0 by Mark-MSX"
echo "=============================================="
echo ""

# Check for required tools
if ! command -v curl &> /dev/null; then
    echo "ERROR: curl is required but not installed."
    exit 1
fi

if ! command -v unzip &> /dev/null; then
    echo "ERROR: unzip is required but not installed."
    exit 1
fi

if ! command -v retroarch &> /dev/null; then
    echo "WARNING: RetroArch not found. Install with:"
    echo "  Arch/CachyOS: sudo pacman -S retroarch"
    echo "  Ubuntu: sudo apt install retroarch"
    echo ""
fi

# Create directories
echo "[1/3] Creating directories..."
mkdir -p cores saves states screenshots recordings logs playlists system roms

# Download FBNeo core
echo ""
echo "[2/3] Downloading FBNeo core..."
if [[ ! -f "cores/fbneo_libretro.so" ]]; then
    curl -L "https://buildbot.libretro.com/nightly/linux/x86_64/latest/fbneo_libretro.so.zip" -o /tmp/fbneo.zip
    unzip -o /tmp/fbneo.zip -d cores/
    rm /tmp/fbneo.zip
    echo "  -> FBNeo core downloaded ($(du -h cores/fbneo_libretro.so | cut -f1))"
else
    echo "  -> FBNeo core already exists, skipping"
fi

# Download MAME core (optional, large)
echo ""
echo "[3/3] Downloading MAME core (optional, ~110MB)..."
if [[ ! -f "cores/mame_libretro.so" ]]; then
    read -p "Download MAME core? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        curl -L "https://buildbot.libretro.com/nightly/linux/x86_64/latest/mame_libretro.so.zip" -o /tmp/mame.zip
        unzip -o /tmp/mame.zip -d cores/
        rm /tmp/mame.zip
        echo "  -> MAME core downloaded ($(du -h cores/mame_libretro.so | cut -f1))"
    else
        echo "  -> Skipped MAME core"
    fi
else
    echo "  -> MAME core already exists, skipping"
fi

# Update ROM directory in config if needed
echo ""
echo "=============================================="
echo "   Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Edit retroarch.cfg and set your ROM directory:"
echo "     rgui_browser_directory = \"/path/to/your/roms\""
echo ""
echo "  2. Also update shmuparch.py line 20:"
echo "     ROM_DIR = Path(\"/path/to/your/roms\")"
echo ""
echo "  3. Launch: ./shmuparch.sh"
echo ""
echo "For CachyOS/Arch users with NVIDIA hybrid GPU:"
echo "  The launcher auto-detects game-performance and NVIDIA offload."
echo ""
