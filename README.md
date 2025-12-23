# ShmupArch Linux

A Linux port of [ShmupArch](https://www.youtube.com/watch?v=Sec3r6RKAPg) by Mark-MSX / [The Electric Underground](https://www.youtube.com/@TheElectricUnderground).

ShmupArch is a RetroArch configuration optimized for **minimal input latency** when playing arcade shmups (shoot 'em ups). This makes a noticeable difference in games where frame-perfect reactions matter.

## Features

- **TUI Game Launcher** - Browse 64 preconfigured shmups with pretty names
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

# Edit ROM path in shmuparch.py (line 20) and retroarch.cfg
# Then launch:
./shmuparch.sh
```

## Usage

```bash
./shmuparch.sh              # TUI game selector
./shmuparch.sh bgaregga     # Launch specific game by ROM name
./shmuparch.sh --mame rom   # Use MAME core instead of FBNeo
./shmuparch.sh --menu       # Open RetroArch menu directly
```

### TUI Controls

| Key | Action |
|-----|--------|
| ↑/↓ or j/k | Navigate |
| Enter | Launch game |
| Type | Filter games |
| Escape | Clear filter / Quit |
| Q | Quit |
| PgUp/PgDn | Fast scroll |

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

## Included Games (64)

### Cave (19)
DonPachi, DoDonPachi, DoDonPachi II, DoDonPachi Dai-Ou-Jou (+ Black Label),
DoDonPachi Dai-Fukkatsu, DoDonPachi SaiDaiOuJou, ESP Ra.De., Espgaluda,
Guwange, Ketsui (+ Arrange), Akai Katana, Mushihimesama Futari 1.5

### Raizing (4)
Battle Garegga, Armed Police Batrider, Battle Bakraid

### Toaplan (3)
Truxton, Fire Shark, Batsugun

### Psikyo (7)
Gunbird 1/2, Strikers 1945 I/II/III

### Capcom (9)
1941, 1942, 1943, Giga Wing, Progear, Mars Matrix

### Irem (4)
R-Type, R-Type II, R-Type Leo

### Taito (6)
Rayforce, Metal Black, Darius, Darius Gaiden Extra

### SNK (7)
Metal Slug 1-5, Metal Slug X, Blazing Star

### Others
Gradius, Gradius II, Raiden, Cotton, P-47

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

## File Structure

```
shmuparch-linux/
├── shmuparch.py          # TUI launcher (Python)
├── shmuparch.sh          # Shell wrapper
├── setup.sh              # Downloads cores
├── retroarch.cfg         # Low-latency RetroArch config
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

## License

Configuration files based on ShmupArch 7.0 by Mark-MSX.
Launcher scripts are MIT licensed.
