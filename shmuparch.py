#!/usr/bin/env python3
"""
ShmupArch Linux Launcher
Based on ShmupArch 7.0 by Mark-MSX / The Electric Underground

A TUI launcher for low-latency arcade shmup emulation.
"""

import curses
import os
import subprocess
import sys
from pathlib import Path

# Configuration
SHMUPARCH_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = SHMUPARCH_DIR / "retroarch.cfg"
FBNEO_CORE = SHMUPARCH_DIR / "cores" / "fbneo_libretro.so"
MAME_CORE = SHMUPARCH_DIR / "cores" / "mame_libretro.so"
ROM_DIR = Path("/mnt/z/roms/arcade")

# MiSTer mode: stream to CRT via GroovyMister
MISTER_MODE = False
MISTER_RETROARCH_BIN = Path("/home/fbs/src/RetroArch/retroarch")
MISTER_CONFIG_FILE = SHMUPARCH_DIR / "retroarch-mister.cfg"

# NVIDIA GPU environment variables (force discrete GPU on hybrid systems)
NVIDIA_ENV = {
    "__NV_PRIME_RENDER_OFFLOAD": "1",
    "__GLX_VENDOR_LIBRARY_NAME": "nvidia",
    "__VK_LAYER_NV_optimus": "NVIDIA_only",
    "VK_ICD_FILENAMES": "/usr/share/vulkan/icd.d/nvidia_icd.json",
}

# CachyOS game-performance wrapper (sets CPU governor, power profile, scheduler)
GAME_PERFORMANCE_CMD = "/usr/bin/game-performance"

# Game database: rom_name -> (pretty_name, category, run_ahead_frames)
GAMES = {
    # === CAVE ===
    "akatana":    ("Akai Katana", "Cave", 1),
    "deathsml":   ("Deathsmiles", "Cave", 1),
    "dsmbl":      ("Deathsmiles MegaBlack Label", "Cave", 1),
    "dfeveron":   ("Dangun Feveron", "Cave", 1),
    "donpachi":   ("DonPachi", "Cave", 1),
    "donpachij":  ("DonPachi (Japan)", "Cave", 1),
    "ddonpach":   ("DoDonPachi", "Cave", 1),
    "ddp2":       ("DoDonPachi II: Bee Storm", "Cave", 1),
    "ddp3":       ("DoDonPachi Dai-Ou-Jou", "Cave", 1),
    "ddpdoj":     ("DoDonPachi Dai-Ou-Jou", "Cave", 1),
    "ddpdojblk":  ("DoDonPachi Dai-Ou-Jou Black Label", "Cave", 1),
    "ddpdojp":    ("DoDonPachi Dai-Ou-Jou (Prototype)", "Cave", 1),
    "ddpdfk":     ("DoDonPachi Dai-Fukkatsu", "Cave", 1),
    "ddpdfk10":   ("DoDonPachi Dai-Fukkatsu Ver 1.0", "Cave", 1),
    "ddpsdoj":    ("DoDonPachi SaiDaiOuJou", "Cave", 1),
    "espgal":     ("Espgaluda", "Cave", 1),
    "espgal2":    ("Espgaluda II", "Cave", 1),
    "esprade":    ("ESP Ra.De.", "Cave", 2),
    "futari15":   ("Mushihimesama Futari 1.5", "Cave", 1),
    "guwange":    ("Guwange", "Cave", 2),
    "ibara":      ("Ibara", "Cave", 1),
    "ibarablk":   ("Ibara Kuro Black Label", "Cave", 1),
    "ket":        ("Ketsui: Kizuna Jigoku Tachi", "Cave", 1),
    "ketarr":     ("Ketsui Arrange", "Cave", 1),
    "ketarr151":  ("Ketsui Arrange Ver 1.51", "Cave", 1),
    "mmpork":     ("Muchi Muchi Pork!", "Cave", 1),
    "mushisam":   ("Mushihimesama", "Cave", 1),
    "pinkswts":   ("Pink Sweets: Ibara Sorekara", "Cave", 1),

    # === TOAPLAN ===
    "batsugun":   ("Batsugun", "Toaplan", 1),
    "fireshrk":   ("Fire Shark (Same! Same! Same!)", "Toaplan", 1),
    "truxton":    ("Truxton (Tatsujin)", "Toaplan", 1),

    # === RAIZING / 8ING ===
    "batrider":   ("Armed Police Batrider", "Raizing", 3),
    "batriderj":  ("Armed Police Batrider (Japan)", "Raizing", 3),
    "bbakraidj":  ("Battle Bakraid (Japan)", "Raizing", 3),
    "bgaregga":   ("Battle Garegga", "Raizing", 3),

    # === PSIKYO ===
    "gunbird":    ("Gunbird", "Psikyo", 4),
    "gunbird2":   ("Gunbird 2", "Psikyo", 4),
    "gunbirdj":   ("Gunbird (Japan)", "Psikyo", 4),
    "s1945":      ("Strikers 1945", "Psikyo", 4),
    "s1945ii":    ("Strikers 1945 II", "Psikyo", 1),
    "s1945j":     ("Strikers 1945 (Japan)", "Psikyo", 4),
    "1945kiii":   ("Strikers 1945 III", "Psikyo", 1),

    # === CAPCOM ===
    "1941j":      ("1941: Counter Attack (Japan)", "Capcom", 3),
    "1942":       ("1942", "Capcom", 1),
    "1943j":      ("1943: The Battle of Midway (Japan)", "Capcom", 1),
    "gigawing":   ("Giga Wing", "Capcom", 3),
    "gigawingj":  ("Giga Wing (Japan)", "Capcom", 3),
    "progear":    ("Progear", "Capcom", 3),
    "progearj":   ("Progear (Japan)", "Capcom", 3),
    "mmatrix":    ("Mars Matrix", "Capcom", 4),
    "mmatrixj":   ("Mars Matrix (Japan)", "Capcom", 4),

    # === IREM ===
    "rtype":      ("R-Type", "Irem", 2),
    "rtype2":     ("R-Type II", "Irem", 2),
    "rtypeleo":   ("R-Type Leo", "Irem", 3),
    "rtypeleoj":  ("R-Type Leo (Japan)", "Irem", 3),

    # === TAITO ===
    "darius":     ("Darius", "Taito", 1),
    "dariusgx":   ("Darius Gaiden Extra", "Taito", 1),
    "metalb":     ("Metal Black", "Taito", 2),
    "metalbj":    ("Metal Black (Japan)", "Taito", 2),
    "rayforce":   ("Rayforce (Gunlock)", "Taito", 2),
    "rayforcej":  ("Rayforce (Japan)", "Taito", 2),

    # === SNK / NEO GEO ===
    "blazstar":   ("Blazing Star", "SNK", 2),
    "mslug":      ("Metal Slug", "SNK", 4),
    "mslug2":     ("Metal Slug 2", "SNK", 3),
    "mslug3":     ("Metal Slug 3", "SNK", 2),
    "mslug4":     ("Metal Slug 4", "SNK", 2),
    "mslug5":     ("Metal Slug 5", "SNK", 2),
    "mslugx":     ("Metal Slug X", "SNK", 3),

    # === KONAMI ===
    "gradius":    ("Gradius", "Konami", 1),
    "gradius2":   ("Gradius II: Gofer no Yabou", "Konami", 1),

    # === OTHER ===
    "cottonj":    ("Cotton: Fantastic Night Dreams (Japan)", "Sega/Success", 1),
    "p47j":       ("P-47: The Phantom Fighter (Japan)", "Jaleco", 2),
    "raiden":     ("Raiden", "Seibu", 1),
}

# Category display order
CATEGORY_ORDER = [
    "Cave", "Toaplan", "Raizing", "Psikyo", "Capcom",
    "Irem", "Taito", "SNK", "Konami", "Sega/Success", "Jaleco", "Seibu"
]


def get_games_by_category():
    """Organize games by category."""
    by_category = {cat: [] for cat in CATEGORY_ORDER}
    for rom, (name, cat, frames) in sorted(GAMES.items(), key=lambda x: x[1][0]):
        if cat in by_category:
            by_category[cat].append((rom, name, frames))
    return by_category


def check_rom_exists(rom_name):
    """Check if ROM file exists."""
    return (ROM_DIR / f"{rom_name}.zip").exists()


def get_launch_env():
    """Get environment with NVIDIA GPU variables set (desktop mode only)."""
    env = os.environ.copy()
    if MISTER_MODE:
        # Force X11/XWayland for MiSTer mode - switchres needs xrandr
        env["GDK_BACKEND"] = "x11"
        env["QT_QPA_PLATFORM"] = "xcb"
    else:
        # NVIDIA GPU offload for desktop mode
        env.update(NVIDIA_ENV)
    return env


def get_retroarch_cmd():
    """Get RetroArch binary path based on mode."""
    if MISTER_MODE:
        return str(MISTER_RETROARCH_BIN)
    return "retroarch"


def get_config_file():
    """Get config file path based on mode."""
    if MISTER_MODE:
        return MISTER_CONFIG_FILE
    return CONFIG_FILE


def launch_game(rom_name, use_mame=False):
    """Launch a game with RetroArch."""
    rom_path = ROM_DIR / f"{rom_name}.zip"
    if not rom_path.exists():
        return False, f"ROM not found: {rom_path}"

    config = get_config_file()
    if not config.exists():
        return False, f"Config not found: {config}"

    core = MAME_CORE if use_mame else FBNEO_CORE
    if not core.exists():
        return False, f"Core not found: {core}"

    # Build command (add verbose in MiSTer mode for debugging)
    retroarch_cmd = [get_retroarch_cmd(), "--config", str(config), "-L", str(core), str(rom_path)]
    if MISTER_MODE:
        retroarch_cmd.insert(1, "-v")  # Verbose for MiSTer debugging

    # Wrap with game-performance if available (desktop mode only - conflicts with MiSTer)
    if not MISTER_MODE and Path(GAME_PERFORMANCE_CMD).exists():
        cmd = [GAME_PERFORMANCE_CMD] + retroarch_cmd
    else:
        cmd = retroarch_cmd

    # Show mode indicator
    mode = "MiSTer CRT" if MISTER_MODE else "Desktop"
    print(f"Launching [{mode}]: {rom_name}")

    subprocess.run(cmd, env=get_launch_env())
    return True, None


def draw_menu(stdscr, games_by_cat, selected_idx, scroll_offset, filter_text=""):
    """Draw the game selection menu."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Build flat list of items (categories + games)
    items = []
    for cat in CATEGORY_ORDER:
        cat_games = games_by_cat.get(cat, [])
        if not cat_games:
            continue

        # Filter games if filter text is set
        if filter_text:
            filtered = [(r, n, f) for r, n, f in cat_games
                       if filter_text.lower() in n.lower() or filter_text.lower() in r.lower()]
            if not filtered:
                continue
            cat_games = filtered

        items.append(("category", cat, None, None))
        for rom, name, frames in cat_games:
            items.append(("game", rom, name, frames))

    if not items:
        stdscr.addstr(2, 2, "No games match filter", curses.A_DIM)
        return items

    # Header
    header = " SHMUPARCH LINUX - Low Latency Arcade "
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(0, (width - len(header)) // 2, header)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

    # Filter indicator
    if filter_text:
        filter_str = f" Filter: {filter_text}_ "
        stdscr.addstr(1, 2, filter_str, curses.color_pair(3))
    else:
        stdscr.addstr(1, 2, " Type to filter | Enter: Launch | Q: Quit ", curses.A_DIM)

    # Calculate visible area
    menu_start = 3
    menu_height = height - menu_start - 2

    # Ensure selected item is visible
    if selected_idx < scroll_offset:
        scroll_offset = selected_idx
    elif selected_idx >= scroll_offset + menu_height:
        scroll_offset = selected_idx - menu_height + 1

    # Draw items
    for i, (item_type, *data) in enumerate(items[scroll_offset:scroll_offset + menu_height]):
        y = menu_start + i
        if y >= height - 2:
            break

        actual_idx = scroll_offset + i
        is_selected = actual_idx == selected_idx

        if item_type == "category":
            cat_name = data[0]
            # Category header
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr(y, 2, f"━━━ {cat_name} ━━━"[:width-4])
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        else:
            rom, name, frames = data
            rom_exists = check_rom_exists(rom)

            # Build display string
            prefix = "▶ " if is_selected else "  "
            frames_str = f"[{frames}F]" if frames > 1 else "    "
            status = "" if rom_exists else " [MISSING]"
            display = f"{prefix}{name} {frames_str}{status}"

            # Truncate if needed
            if len(display) > width - 4:
                display = display[:width-7] + "..."

            # Choose style
            if is_selected:
                if rom_exists:
                    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(y, 2, display.ljust(width-4))
                stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
            elif not rom_exists:
                stdscr.addstr(y, 2, display, curses.color_pair(4) | curses.A_DIM)
            else:
                stdscr.addstr(y, 2, display)

    # Footer with ROM info
    if items and 0 <= selected_idx < len(items):
        item = items[selected_idx]
        if item[0] == "game":
            rom = item[1]
            footer = f" ROM: {rom}.zip | Dir: {ROM_DIR} "
            stdscr.addstr(height-1, 2, footer[:width-4], curses.A_DIM)

    stdscr.refresh()
    return items


def main_menu(stdscr):
    """Main menu loop."""
    # Setup colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Selected
    curses.init_pair(2, curses.COLOR_YELLOW, -1)                   # Category
    curses.init_pair(3, curses.COLOR_GREEN, -1)                    # Filter
    curses.init_pair(4, curses.COLOR_RED, -1)                      # Missing ROM

    curses.curs_set(0)  # Hide cursor
    stdscr.keypad(True)

    games_by_cat = get_games_by_category()
    selected_idx = 1  # Start on first game, not category
    scroll_offset = 0
    filter_text = ""

    while True:
        items = draw_menu(stdscr, games_by_cat, selected_idx, scroll_offset, filter_text)

        if not items:
            key = stdscr.getch()
            if key == 27 or key == ord('q') or key == ord('Q'):  # Escape or Q
                break
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                filter_text = filter_text[:-1]
            continue

        key = stdscr.getch()

        if key == 27 or key == ord('q') or key == ord('Q'):  # Escape or Q
            if filter_text:
                filter_text = ""
            else:
                break

        elif key == curses.KEY_UP or key == ord('k'):
            # Move up, skip categories
            new_idx = selected_idx - 1
            while new_idx >= 0 and items[new_idx][0] == "category":
                new_idx -= 1
            if new_idx >= 0:
                selected_idx = new_idx

        elif key == curses.KEY_DOWN or key == ord('j'):
            # Move down, skip categories
            new_idx = selected_idx + 1
            while new_idx < len(items) and items[new_idx][0] == "category":
                new_idx += 1
            if new_idx < len(items):
                selected_idx = new_idx

        elif key == curses.KEY_PPAGE:  # Page Up
            selected_idx = max(0, selected_idx - 10)
            while selected_idx > 0 and items[selected_idx][0] == "category":
                selected_idx -= 1

        elif key == curses.KEY_NPAGE:  # Page Down
            selected_idx = min(len(items) - 1, selected_idx + 10)
            while selected_idx < len(items) - 1 and items[selected_idx][0] == "category":
                selected_idx += 1

        elif key == curses.KEY_HOME:
            selected_idx = 0
            while selected_idx < len(items) and items[selected_idx][0] == "category":
                selected_idx += 1

        elif key == curses.KEY_END:
            selected_idx = len(items) - 1
            while selected_idx > 0 and items[selected_idx][0] == "category":
                selected_idx -= 1

        elif key == ord('\n') or key == curses.KEY_ENTER:
            if items[selected_idx][0] == "game":
                rom = items[selected_idx][1]
                if check_rom_exists(rom):
                    # Clear screen before launching
                    stdscr.clear()
                    stdscr.refresh()
                    curses.endwin()

                    # Launch game
                    success, error = launch_game(rom)

                    # Reinitialize curses after game exits
                    stdscr = curses.initscr()
                    curses.start_color()
                    curses.use_default_colors()
                    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
                    curses.init_pair(2, curses.COLOR_YELLOW, -1)
                    curses.init_pair(3, curses.COLOR_GREEN, -1)
                    curses.init_pair(4, curses.COLOR_RED, -1)
                    curses.curs_set(0)
                    stdscr.keypad(True)

        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
            filter_text = filter_text[:-1]
            selected_idx = 1  # Reset selection on filter change

        elif 32 <= key <= 126:  # Printable characters
            filter_text += chr(key)
            selected_idx = 1  # Reset selection on filter change

        # Adjust scroll
        height = stdscr.getmaxyx()[0]
        menu_height = height - 5
        if selected_idx < scroll_offset:
            scroll_offset = selected_idx
        elif selected_idx >= scroll_offset + menu_height:
            scroll_offset = selected_idx - menu_height + 1


def launch_rom_directly(rom_path, use_mame=False):
    """Launch a ROM file directly."""
    config = get_config_file()
    core = MAME_CORE if use_mame else FBNEO_CORE
    retroarch_cmd = [get_retroarch_cmd(), "--config", str(config), "-L", str(core), str(rom_path)]
    if MISTER_MODE:
        retroarch_cmd.insert(1, "-v")  # Verbose for MiSTer debugging

    # Skip game-performance in MiSTer mode (conflicts with streaming)
    if not MISTER_MODE and Path(GAME_PERFORMANCE_CMD).exists():
        cmd = [GAME_PERFORMANCE_CMD] + retroarch_cmd
    else:
        cmd = retroarch_cmd

    mode = "MiSTer CRT" if MISTER_MODE else "Desktop"
    print(f"Launching [{mode}]: {rom_path.stem}")

    subprocess.run(cmd, env=get_launch_env())


def main():
    """Entry point."""
    global MISTER_MODE

    # Parse arguments
    args = sys.argv[1:]
    use_mame = False
    rom_arg = None

    # Process flags
    while args:
        if args[0] == "--mister":
            MISTER_MODE = True
            args = args[1:]
        elif args[0] == "--mame":
            use_mame = True
            args = args[1:]
        elif args[0] == "--menu":
            # Just open menu
            break
        elif args[0] == "--help" or args[0] == "-h":
            print("ShmupArch Linux - Low-latency shmup launcher")
            print()
            print("Usage: shmuparch.py [options] [rom_name]")
            print()
            print("Options:")
            print("  --mister    Stream to MiSTer FPGA (CRT output)")
            print("  --mame      Use MAME core instead of FBNeo")
            print("  --menu      Open RetroArch menu directly")
            print("  --help      Show this help")
            print()
            print("Examples:")
            print("  ./shmuparch.py              # TUI game selector (Desktop)")
            print("  ./shmuparch.py --mister     # TUI game selector (MiSTer CRT)")
            print("  ./shmuparch.py bgaregga     # Launch game (Desktop)")
            print("  ./shmuparch.py --mister ket # Launch game (MiSTer CRT)")
            return 0
        else:
            rom_arg = args[0]
            args = args[1:]
            break

    # Show mode
    if MISTER_MODE:
        print("ShmupArch [MiSTer CRT Mode] -> 192.168.30.81")
        if not MISTER_RETROARCH_BIN.exists():
            print(f"Error: MiSTer RetroArch binary not found: {MISTER_RETROARCH_BIN}")
            print("Build with: cd ~/src/RetroArch && ./configure --enable-mister && make")
            return 1
        if not MISTER_CONFIG_FILE.exists():
            print(f"Error: MiSTer config not found: {MISTER_CONFIG_FILE}")
            return 1

    # Handle ROM argument
    if rom_arg:
        # If it's a path, extract ROM name
        if "/" in rom_arg:
            rom_path = Path(rom_arg)
            if rom_path.exists():
                launch_rom_directly(rom_path, use_mame)
                return 0

        # If it's a ROM name, look it up
        rom_name = rom_arg.replace(".zip", "")
        rom_path = ROM_DIR / f"{rom_name}.zip"
        if rom_path.exists():
            launch_rom_directly(rom_path, use_mame)
            return 0
        else:
            print(f"ROM not found: {rom_path}")
            return 1

    # Check dependencies
    config = get_config_file()
    if not config.exists():
        print(f"Error: Config not found: {config}")
        return 1

    if not FBNEO_CORE.exists():
        print(f"Error: FBNeo core not found: {FBNEO_CORE}")
        return 1

    # Check if retroarch is installed (for desktop mode)
    if not MISTER_MODE:
        try:
            subprocess.run(["which", "retroarch"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print("Error: RetroArch not found. Install with: sudo pacman -S retroarch")
            return 1

    # Launch TUI
    mode = "MiSTer CRT" if MISTER_MODE else "Desktop"
    print(f"Starting ShmupArch [{mode}]...")
    try:
        curses.wrapper(main_menu)
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
