#!/bin/bash
# ShmupArch Linux Launcher
# Based on ShmupArch 7.0 by Mark-MSX / The Electric Underground
#
# Usage:
#   ./shmuparch.sh                    # Launch TUI game selector
#   ./shmuparch.sh /path/to/rom.zip   # Launch specific ROM with FBNeo
#   ./shmuparch.sh --mame /path/to/rom.zip  # Launch ROM with MAME core
#   ./shmuparch.sh --menu             # Launch RetroArch menu directly

SHMUPARCH_DIR="$(dirname "$(readlink -f "$0")")"

# If --menu flag, launch RetroArch directly
if [[ "$1" == "--menu" ]]; then
    retroarch --config "${SHMUPARCH_DIR}/retroarch.cfg"
    exit $?
fi

# Otherwise use Python TUI launcher
exec python3 "${SHMUPARCH_DIR}/shmuparch.py" "$@"
