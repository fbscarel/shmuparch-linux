# ShmupArch Linux

A Linux port of [ShmupArch](https://www.youtube.com/watch?v=Sec3r6RKAPg) by Mark-MSX / [The Electric Underground](https://www.youtube.com/@TheElectricUnderground).

ShmupArch is a RetroArch configuration optimized for **minimal input latency** when playing arcade shmups (shoot 'em ups). This makes a noticeable difference in games where frame-perfect reactions matter.

## Features

- **TUI Game Launcher** - Browse 156 preconfigured shmups organized by developer
- **Version Grouping** - Multiple ROM variants grouped under one entry with picker
- **Smart Sorting** - Sort by developer, quality, difficulty, or name (Tab to cycle)
- **Advanced Filtering** - Filter by text, quality (`q>7`), difficulty (`d<5`), routing (`r:low`)
- **Normalized Difficulty** - Western (1-10) and Japanese (0-45) ratings unified
- **Run-ahead enabled** - Reduces input lag by 1-4 frames depending on game
- **Game-specific configs** - Optimized DIP switches and run-ahead per game
- **NVIDIA hybrid GPU support** - Auto-detects and uses discrete GPU
- **CachyOS game-performance** - Auto-wraps with performance governor

## Quick Start

```bash
# Clone the repository
git clone https://github.com/fbscarel/shmuparch-linux
cd shmuparch-linux

# Run setup (downloads cores)
./setup.sh

# Install RetroArch if needed
sudo pacman -S retroarch  # Arch/CachyOS

# Edit ROM path in shmuparch.py (line 27) and retroarch.cfg
# Then launch:
./shmuparch.sh
```

## Usage

```bash
./shmuparch.sh              # TUI game selector
./shmuparch.sh bgaregga     # Launch specific game by ROM name
./shmuparch.sh --mame rom   # Use MAME core instead of FBNeo
./shmuparch.sh --mister     # Stream to MiSTer FPGA (CRT output)
./shmuparch.sh --help       # Show all options
```

### TUI Controls

| Key | Action |
|-----|--------|
| ↑/↓ or j/k | Navigate |
| Enter | Launch game (or show version picker) |
| Tab | Cycle sort mode (Developer → Quality → Difficulty → Name) |
| V | Toggle showing missing ROMs |
| Type | Filter games |
| Escape | Clear filter / Quit |
| Q | Quit |
| PgUp/PgDn | Fast scroll |

### Filter Syntax

| Filter | Example | Description |
|--------|---------|-------------|
| Text | `battle` | Match game name or ROM |
| Quality | `q>7` `q=9` | Quality rating (1-10) |
| Difficulty | `d<5` `d>8` | 1CC difficulty (normalized) |
| Routing | `r:low` `r:med` `r:high` | Route complexity |
| Developer | `dev:cave` | Filter by developer |
| Combined | `dev:cave q>8 d<7` | Multiple filters |

## Game Database

Games are defined in `games_db.py` with metadata from multiple sources:

- **FBNeo DAT files** - ROM names, manufacturers, orientation
- **1CC Difficulty Index** - Quality ratings (1-10), difficulty, routing
- **Japanese Difficulty Index** - 0-45 scale difficulty ratings
- **ROM variants** - All regional/version variants grouped together

### Included Games (156)

| Developer | Games |
|-----------|-------|
| Cave | DonPachi, DoDonPachi series, ESP Ra.De., Espgaluda 1/2, Guwange, Ketsui, Mushihimesama series, Ibara, Pink Sweets, Akai Katana, Deathsmiles |
| Raizing | Battle Garegga, Armed Police Batrider, Battle Bakraid, Mahou Daisakusen series |
| Toaplan | Truxton 1/2, Fire Shark, Batsugun, Zero Wing, Hellfire, Out Zone, Vimana |
| Psikyo | Gunbird 1/2, Strikers 1945 I/II/III, Tengai, Dragon Blaze, Sol Divide |
| Capcom | 1941-1944, Giga Wing 1/2, Progear, Mars Matrix, Varth, Dimahoo |
| Irem | R-Type series, Image Fight, Air Duel, X-Multiply |
| Taito | Rayforce, Metal Black, Darius series, G-Darius, Layer Section |
| Seibu Kaihatsu | Raiden series, Raiden Fighters series, Viper Phase 1 |
| Konami | Gradius series, Salamander, Parodius, Twin Bee, Thunder Cross |
| SNK | Metal Slug 1-5/X, Blazing Star, Pulstar, Last Resort |
| And more... | NMK, Treasure, Technosoft, Video System, Athena, Allumer, etc. |

## Key Latency Settings

These settings in `retroarch.cfg` minimize input lag:

```ini
run_ahead_enabled = "true"        # THE key feature
run_ahead_frames = "1"            # Default (game-specific: 2-4)
run_ahead_secondary_instance = "true"
video_vsync = "false"
video_hard_sync = "true"
video_frame_delay = "0"
input_poll_type_behavior = "0"    # Early polling
```

FBNeo core settings in `config/FinalBurn Neo/FinalBurn Neo.opt`:
```ini
fbneo-cpu-speed-adjust = "400%"   # Mark-MSX's secret sauce
fbneo-force-60hz = "enabled"
```

## NVIDIA Hybrid GPU Support

For systems with Intel + NVIDIA GPUs, the launcher automatically sets:

```bash
__NV_PRIME_RENDER_OFFLOAD=1
__GLX_VENDOR_LIBRARY_NAME=nvidia
__VK_LAYER_NV_optimus=NVIDIA_only
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
```

## CachyOS Integration

On CachyOS, the launcher auto-detects `/usr/bin/game-performance` and wraps
RetroArch with it, enabling:
- CPU governor set to performance
- Power profile set to performance
- scx scheduler switched to gaming mode

## MiSTer CRT Streaming

For authentic CRT output, use `--mister` to stream to a MiSTer FPGA:

```bash
./shmuparch.sh --mister           # TUI with MiSTer output
./shmuparch.sh --mister bgaregga  # Direct launch to MiSTer
```

Requires GroovyMister setup and custom RetroArch build with switchres support.

## File Structure

```
shmuparch-linux/
├── shmuparch.py          # TUI launcher (Python)
├── games_db.py           # Master game database
├── shmuparch.sh          # Shell wrapper
├── setup.sh              # Downloads cores
├── retroarch.cfg         # Low-latency RetroArch config
├── retroarch-mister.cfg  # MiSTer streaming config
├── config/
│   ├── FinalBurn Neo/
│   │   ├── FinalBurn Neo.opt   # Core options + DIP switches
│   │   └── *.cfg               # Per-game run-ahead overrides
│   ├── MAME/
│   │   └── MAME.opt
│   └── remaps/
│       └── FinalBurn Neo/      # Controller remaps
├── cores/                # Downloaded by setup.sh
│   ├── fbneo_libretro.so
│   └── mame_libretro.so
└── roms/                 # Your ROMs go here
```

## Credits

- **Mark-MSX** / [The Electric Underground](https://www.youtube.com/@TheElectricUnderground) - Original ShmupArch
- **[shmuparchify](https://github.com/zmnpl/shmuparchify)** - Reference for game configs
- **[Libretro](https://www.libretro.com/)** - RetroArch and cores
- **[mdk.cab](https://mdk.cab)** - ROM availability checking

## License

Configuration files based on ShmupArch 7.0 by Mark-MSX.
Launcher scripts are MIT licensed.
