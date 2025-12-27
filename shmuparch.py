#!/usr/bin/env python3
"""
ShmupArch Linux Launcher
Based on ShmupArch 7.0 by Mark-MSX / The Electric Underground

A TUI launcher for low-latency arcade shmup emulation.
"""

import curses
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

# Import game database
from games_db import GAMES as GAMES_DB, Platform, Routing

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


class SortMode(Enum):
    """Sort modes for game list."""
    DEVELOPER = "developer"
    QUALITY = "quality"
    DIFFICULTY = "difficulty"
    NAME = "name"


@dataclass
class GameVersion:
    """A specific version/ROM of a game."""
    rom_name: str
    suffix: str  # e.g., "Japan", "Arrange 1.1", "" for parent
    exists: bool = False  # Whether ROM exists on disk


@dataclass
class GameInfo:
    """Game information for display and sorting."""
    rom_name: str
    name: str
    developer: str
    runahead: int
    quality: Optional[int]        # 1-10, higher = better
    difficulty_1cc: Optional[int]  # 1-10, higher = harder
    difficulty_jp: Optional[int]   # 0-45 scale
    routing: Routing
    requires_mame: bool
    notes: str = ""
    versions: list = None  # List of GameVersion objects

    def __post_init__(self):
        if self.versions is None:
            self.versions = []

    def available_versions(self) -> list:
        """Get versions that exist on disk."""
        return [v for v in self.versions if v.exists]

    def version_count(self) -> int:
        """Count of available versions."""
        return len(self.available_versions())


def check_rom_exists(rom_name):
    """Check if ROM file exists."""
    return (ROM_DIR / f"{rom_name}.zip").exists()


def _build_games_dict():
    """Build GAMES dict from games_db.

    Format: base_name -> GameInfo (with versions list)
    Groups all ROM versions under a single game entry.
    """
    games = {}

    for game in GAMES_DB.values():
        # Skip non-arcade games
        if game.platform not in (Platform.ARCADE, Platform.NEOGEO):
            continue

        if not game.rom_name:
            continue

        # Build list of versions
        versions = []
        seen_roms = set()

        # Add versions from game.versions (may include parent)
        for version in game.versions:
            if version.rom_name and version.rom_name not in seen_roms:
                seen_roms.add(version.rom_name)
                ver_exists = check_rom_exists(version.rom_name)
                versions.append(GameVersion(
                    rom_name=version.rom_name,
                    suffix=version.suffix or "",
                    exists=ver_exists,
                ))

        # If no versions defined, use parent ROM
        if not versions:
            parent_exists = check_rom_exists(game.rom_name)
            versions.append(GameVersion(
                rom_name=game.rom_name,
                suffix="",
                exists=parent_exists,
            ))

        # Create single GameInfo with all versions
        games[game.name] = GameInfo(
            rom_name=game.rom_name,  # Primary ROM
            name=game.name,
            developer=game.developer,
            runahead=game.runahead_frames,
            quality=game.quality,
            difficulty_1cc=game.difficulty_1cc,
            difficulty_jp=game.difficulty_jp,
            routing=game.routing,
            requires_mame=game.requires_mame,
            notes=game.notes,
            versions=versions,
        )

    return games


def _build_mame_games():
    """Build MAME_GAMES set from games_db (games with requires_mame=True)."""
    mame_games = set()

    for game in GAMES_DB.values():
        if game.requires_mame:
            mame_games.add(game.rom_name)
            for version in game.versions:
                mame_games.add(version.rom_name)

    # Add hardware-specific games not in the shmup database
    mame_games.update({
        "cotton2",     # Cotton 2 (ST-V)
        "cottonbm",    # Cotton Boomerang (ST-V)
        "elandore",    # Elan Doree (ST-V)
        "sss",         # Steep Slope Sliders (ST-V, not a shmup)
        "batmanfr",    # Batman Forever (ST-V, not a shmup)
    })

    return mame_games


# Build game database from games_db
GAMES = _build_games_dict()
MAME_GAMES = _build_mame_games()

# Category display order (developers in preferred order)
CATEGORY_ORDER = [
    "Cave",
    "Toaplan",
    "Raizing",
    "Psikyo",
    "Takumi",
    "Capcom",
    "Irem",
    "Taito",
    "Seibu Kaihatsu",
    "Konami",
    "Technosoft",
    "Treasure",
    "NMK",
    "Video System",
    "Yumekobo",
    "Aicom",
    "SNK",
    "ADK",
    "Visco",
    "Athena",
    "Allumer",
    "Gazelle",
    "G.rev",
    "Milestone",
    "Alfa System",
    "Success",
    "Warashi",
    "Face",
    "Namco",
    "Banpresto",
    "Jaleco",
    "Nichibutsu",
]


def get_games_by_category():
    """Organize games by category (developer)."""
    by_category = {cat: [] for cat in CATEGORY_ORDER}
    for rom, info in sorted(GAMES.items(), key=lambda x: x[1].name):
        if info.developer in by_category:
            by_category[info.developer].append(info)
    return by_category


def get_normalized_difficulty(info: GameInfo) -> Optional[float]:
    """Get normalized difficulty on 1-10 scale from either Western or JP rating.

    Western 1CC difficulty (1-10) is used directly.
    Japanese difficulty (0-45) is scaled: 1 + (jp_diff * 9 / 45)

    Returns:
        Normalized difficulty 1.0-10.0, or None if no rating
    """
    if info.difficulty_1cc is not None:
        return float(info.difficulty_1cc)
    elif info.difficulty_jp is not None:
        # Scale 0-45 to 1-10: jp=0->1, jp=45->10
        return 1.0 + (info.difficulty_jp * 9.0 / 45.0)
    return None


def get_sorted_games(sort_mode: SortMode, filter_fn=None, show_missing: bool = True):
    """Get games sorted by the specified mode.

    Args:
        sort_mode: How to sort games
        filter_fn: Optional filter function (GameInfo -> bool)
        show_missing: If False, hide games whose ROMs are not found

    Returns:
        List of (category_name, list[GameInfo]) tuples
    """
    all_games = list(GAMES.values())

    # Apply filter if provided
    if filter_fn:
        all_games = [g for g in all_games if filter_fn(g)]

    # Hide games with no available versions if requested
    if not show_missing:
        all_games = [g for g in all_games if g.version_count() > 0]

    if sort_mode == SortMode.DEVELOPER:
        # Group by developer, sort games by name within each
        by_cat = {cat: [] for cat in CATEGORY_ORDER}
        for info in sorted(all_games, key=lambda x: x.name):
            if info.developer in by_cat:
                by_cat[info.developer].append(info)
        return [(cat, games) for cat, games in by_cat.items() if games]

    elif sort_mode == SortMode.QUALITY:
        # Sort by quality descending (best first), group by quality tier
        def q_key(g):
            return (-(g.quality or 0), g.name)
        sorted_games = sorted(all_games, key=q_key)
        # Group into tiers: 9-10 (Excellent), 7-8 (Great), 5-6 (Good), 1-4 (Fair), None
        tiers = [
            ("★★★ Excellent (9-10)", [g for g in sorted_games if g.quality and g.quality >= 9]),
            ("★★ Great (7-8)", [g for g in sorted_games if g.quality and 7 <= g.quality < 9]),
            ("★ Good (5-6)", [g for g in sorted_games if g.quality and 5 <= g.quality < 7]),
            ("Fair (1-4)", [g for g in sorted_games if g.quality and g.quality < 5]),
            ("Unrated", [g for g in sorted_games if g.quality is None]),
        ]
        return [(name, games) for name, games in tiers if games]

    elif sort_mode == SortMode.DIFFICULTY:
        # Sort by normalized difficulty ascending (easiest first)
        def d_key(g):
            norm = get_normalized_difficulty(g)
            if norm is not None:
                return (norm, g.name)
            return (99.0, g.name)  # Unrated at end

        sorted_games = sorted(all_games, key=d_key)

        # Group into difficulty tiers using normalized difficulty
        def in_tier(g, low, high):
            norm = get_normalized_difficulty(g)
            return norm is not None and low <= norm <= high

        tiers = [
            ("🟢 Easy (1-3)", [g for g in sorted_games if in_tier(g, 1.0, 3.99)]),
            ("🟡 Medium (4-6)", [g for g in sorted_games if in_tier(g, 4.0, 6.99)]),
            ("🟠 Hard (7-8)", [g for g in sorted_games if in_tier(g, 7.0, 8.99)]),
            ("🔴 Expert (9-10)", [g for g in sorted_games if in_tier(g, 9.0, 10.0)]),
            ("Unrated", [g for g in sorted_games if get_normalized_difficulty(g) is None]),
        ]
        return [(name, games) for name, games in tiers if games]

    elif sort_mode == SortMode.NAME:
        # Alphabetical by name
        sorted_games = sorted(all_games, key=lambda x: x.name.lower())
        # Group by first letter
        groups = {}
        for g in sorted_games:
            first = g.name[0].upper()
            if first.isdigit():
                first = "0-9"
            if first not in groups:
                groups[first] = []
            groups[first].append(g)
        return [(letter, games) for letter, games in sorted(groups.items())]

    return []


def parse_filter(filter_text: str):
    """Parse filter text and return a filter function.

    Supports:
        - Plain text: matches name or rom
        - q>N, q<N, q=N: quality filter
        - d>N, d<N, d=N: difficulty filter
        - r:low, r:med, r:high: routing filter
        - dev:name: developer filter

    Multiple filters can be combined with spaces.

    Returns:
        Function (GameInfo) -> bool
    """
    if not filter_text.strip():
        return None

    parts = filter_text.lower().split()
    conditions = []

    for part in parts:
        # Quality filter: q>7, q<5, q=8
        if m := re.match(r'^q([<>=])(\d+)$', part):
            op, val = m.groups()
            val = int(val)
            if op == '>':
                conditions.append(lambda g, v=val: g.quality is not None and g.quality > v)
            elif op == '<':
                conditions.append(lambda g, v=val: g.quality is not None and g.quality < v)
            else:
                conditions.append(lambda g, v=val: g.quality == v)

        # Difficulty filter: d>5, d<3, d=7 (uses normalized difficulty from either source)
        elif m := re.match(r'^d([<>=])(\d+)$', part):
            op, val = m.groups()
            val = float(val)
            if op == '>':
                conditions.append(lambda g, v=val: (n := get_normalized_difficulty(g)) is not None and n > v)
            elif op == '<':
                conditions.append(lambda g, v=val: (n := get_normalized_difficulty(g)) is not None and n < v)
            else:
                conditions.append(lambda g, v=val: (n := get_normalized_difficulty(g)) is not None and int(n) == int(v))

        # Routing filter: r:low, r:med, r:high
        elif m := re.match(r'^r:(low|med|high)$', part):
            routing_map = {'low': Routing.LOW, 'med': Routing.MED, 'high': Routing.HIGH}
            r = routing_map[m.group(1)]
            conditions.append(lambda g, r=r: g.routing == r)

        # Developer filter: dev:cave, dev:toaplan
        elif m := re.match(r'^dev:(.+)$', part):
            dev = m.group(1)
            conditions.append(lambda g, d=dev: d in g.developer.lower())

        # Plain text filter: matches name or rom
        else:
            conditions.append(
                lambda g, p=part: p in g.name.lower() or p in g.rom_name.lower()
            )

    if not conditions:
        return None

    def combined_filter(g):
        return all(cond(g) for cond in conditions)

    return combined_filter


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


def launch_game(rom_name, use_mame=None):
    """Launch a game with RetroArch.

    Args:
        rom_name: ROM filename without extension
        use_mame: Force MAME core (True), FBNeo (False), or auto-detect (None)
    """
    rom_path = ROM_DIR / f"{rom_name}.zip"
    if not rom_path.exists():
        return False, f"ROM not found: {rom_path}"

    config = get_config_file()
    if not config.exists():
        return False, f"Config not found: {config}"

    # Auto-detect core if not specified
    if use_mame is None:
        use_mame = rom_name in MAME_GAMES

    core = MAME_CORE if use_mame else FBNEO_CORE
    if not core.exists():
        return False, f"Core not found: {core}"

    # Build command (add verbose in MiSTer mode for debugging)
    retroarch_cmd = [
        get_retroarch_cmd(),
        "--config",
        str(config),
        "-L",
        str(core),
        str(rom_path),
    ]
    if MISTER_MODE:
        retroarch_cmd.insert(1, "-v")  # Verbose for MiSTer debugging

    # Wrap with game-performance if available (desktop mode only - conflicts with MiSTer)
    if not MISTER_MODE and Path(GAME_PERFORMANCE_CMD).exists():
        cmd = [GAME_PERFORMANCE_CMD] + retroarch_cmd
    else:
        cmd = retroarch_cmd

    # Show mode indicator
    mode = "MiSTer CRT" if MISTER_MODE else "Desktop"
    core_name = "MAME" if use_mame else "FBNeo"
    print(f"Launching [{mode}] [{core_name}]: {rom_name}")

    subprocess.run(cmd, env=get_launch_env())
    return True, None


def format_ratings(info: GameInfo, compact: bool = True) -> str:
    """Format game ratings for display.

    Args:
        info: Game information
        compact: If True, use compact format (Q7 D5 R:M)

    Returns:
        Formatted ratings string
    """
    parts = []

    # Quality
    if info.quality is not None:
        parts.append(f"Q{info.quality}")

    # Difficulty (prefer 1CC, show normalized D~ for JP-only games)
    if info.difficulty_1cc is not None:
        parts.append(f"D{info.difficulty_1cc}")
    elif info.difficulty_jp is not None:
        # Show normalized difficulty with ~ to indicate it's derived from JP
        norm = get_normalized_difficulty(info)
        parts.append(f"D~{int(norm)}")

    # Routing
    routing_map = {Routing.LOW: "L", Routing.MED: "M", Routing.HIGH: "H"}
    if info.routing != Routing.LOW or info.quality is not None:
        parts.append(f"R:{routing_map[info.routing]}")

    return " ".join(parts) if parts else ""


def draw_menu(stdscr, sort_mode: SortMode, selected_idx, scroll_offset, filter_text="", show_missing: bool = False):
    """Draw the game selection menu.

    Args:
        stdscr: curses screen
        sort_mode: Current sort mode
        selected_idx: Currently selected item index
        scroll_offset: Scroll position
        filter_text: Current filter text
        show_missing: If True, show games with missing ROMs

    Returns:
        List of (item_type, GameInfo or category_name) tuples
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Parse filter and get sorted games
    filter_fn = parse_filter(filter_text)
    sorted_groups = get_sorted_games(sort_mode, filter_fn, show_missing=show_missing)

    # Build flat list of items (categories + games)
    items = []
    for cat_name, games in sorted_groups:
        if not games:
            continue
        items.append(("category", cat_name))
        for info in games:
            items.append(("game", info))

    if not items:
        stdscr.addstr(2, 2, "No games match filter", curses.A_DIM)
        stdscr.addstr(3, 2, "Filters: q>N d<N r:low/med/high dev:name", curses.A_DIM)
        stdscr.refresh()
        return items

    # Header with sort mode and missing indicator
    sort_labels = {
        SortMode.DEVELOPER: "Developer",
        SortMode.QUALITY: "Quality",
        SortMode.DIFFICULTY: "Difficulty",
        SortMode.NAME: "Name",
    }
    missing_indicator = " [+Missing]" if show_missing else ""
    header = f" SHMUPARCH - Sort: {sort_labels[sort_mode]}{missing_indicator} "
    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(0, (width - len(header)) // 2, header)
    stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

    # Filter/help line
    if filter_text:
        filter_str = f" Filter: {filter_text}_ "
        stdscr.addstr(1, 2, filter_str, curses.color_pair(3))
    else:
        help_text = " Type to filter | Tab: Sort | V: Show missing | Enter: Launch | Q: Quit "
        stdscr.addstr(1, 2, help_text[: width - 4], curses.A_DIM)

    # Calculate visible area
    menu_start = 3
    menu_height = height - menu_start - 3  # Leave room for footer

    # Ensure selected item is visible
    if selected_idx < scroll_offset:
        scroll_offset = selected_idx
    elif selected_idx >= scroll_offset + menu_height:
        scroll_offset = selected_idx - menu_height + 1

    # Draw items
    for i, item in enumerate(items[scroll_offset : scroll_offset + menu_height]):
        y = menu_start + i
        if y >= height - 3:
            break

        actual_idx = scroll_offset + i
        is_selected = actual_idx == selected_idx
        item_type = item[0]

        if item_type == "category":
            cat_name = item[1]
            # Category header
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr(y, 2, f"━━━ {cat_name} ━━━"[: width - 4])
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        else:
            info = item[1]
            available_count = info.version_count()
            total_versions = len(info.versions)
            has_any_version = available_count > 0

            # Build display string with ratings
            prefix = "▶ " if is_selected else "  "
            ratings = format_ratings(info)

            # Version count indicator (only if multiple versions exist)
            if total_versions > 1:
                version_str = f"({available_count}/{total_versions})"
            else:
                version_str = ""

            # Runahead indicator
            frames_str = f"[{info.runahead}F]" if info.runahead > 1 else ""

            # Core indicator
            core_str = "[M]" if info.requires_mame else ""

            # Status
            status = " [MISSING]" if not has_any_version else ""

            # Compose display: name + version + ratings + frames + core + status
            name_part = info.name
            suffix_parts = [p for p in [version_str, ratings, frames_str, core_str, status] if p]
            suffix = " " + " ".join(suffix_parts) if suffix_parts else ""

            # Calculate available width for name
            available = width - 4 - len(prefix) - len(suffix)
            if len(name_part) > available:
                name_part = name_part[: available - 3] + "..."

            display = f"{prefix}{name_part}{suffix}"

            # Choose style based on selection and ROM availability
            if is_selected:
                if has_any_version:
                    stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                else:
                    stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(y, 2, display.ljust(width - 4))
                stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
            elif not has_any_version:
                stdscr.addstr(y, 2, display, curses.color_pair(4) | curses.A_DIM)
            else:
                stdscr.addstr(y, 2, display)

    # Footer with detailed game info
    if items and 0 <= selected_idx < len(items):
        item = items[selected_idx]
        if item[0] == "game":
            info = item[1]
            avail = info.available_versions()

            # Line 1: Versions and developer
            if len(info.versions) > 1:
                ver_names = [v.suffix or "World" for v in avail[:3]]
                ver_str = ", ".join(ver_names)
                if len(avail) > 3:
                    ver_str += f", +{len(avail)-3} more"
                footer1 = f" Versions: {ver_str} | {info.developer}"
            else:
                footer1 = f" {info.rom_name}.zip | {info.developer}"
            if info.requires_mame:
                footer1 += " | MAME"
            stdscr.addstr(height - 2, 2, footer1[: width - 4], curses.A_DIM)

            # Line 2: Detailed ratings
            details = []
            if info.quality is not None:
                details.append(f"Quality: {info.quality}/10")
            if info.difficulty_1cc is not None:
                details.append(f"1CC Diff: {info.difficulty_1cc}/10")
            if info.difficulty_jp is not None:
                details.append(f"JP Diff: {info.difficulty_jp}/45")
            routing_names = {Routing.LOW: "Low", Routing.MED: "Medium", Routing.HIGH: "High"}
            details.append(f"Routing: {routing_names[info.routing]}")

            footer2 = " " + " | ".join(details)
            stdscr.addstr(height - 1, 2, footer2[: width - 4], curses.A_DIM)

    stdscr.refresh()
    return items


def draw_version_picker(stdscr, info: GameInfo, selected_idx: int):
    """Draw a version picker submenu for a game with multiple versions.

    Returns:
        Selected GameVersion or None if cancelled
    """
    versions = info.available_versions()
    if not versions:
        return None

    height, width = stdscr.getmaxyx()

    # Calculate popup dimensions
    popup_width = min(60, width - 4)
    popup_height = min(len(versions) + 4, height - 4)
    popup_x = (width - popup_width) // 2
    popup_y = (height - popup_height) // 2

    selected = selected_idx if selected_idx < len(versions) else 0

    while True:
        # Draw popup background
        stdscr.attron(curses.color_pair(1))
        for y in range(popup_y, popup_y + popup_height):
            stdscr.addstr(y, popup_x, " " * popup_width)
        stdscr.attroff(curses.color_pair(1))

        # Draw title
        title = f" Select Version: {info.name} "
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(popup_y, popup_x + (popup_width - len(title)) // 2, title[:popup_width])
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Draw versions
        for i, ver in enumerate(versions):
            y = popup_y + 2 + i
            if y >= popup_y + popup_height - 1:
                break

            is_selected = i == selected
            prefix = "▶ " if is_selected else "  "
            suffix_display = ver.suffix if ver.suffix else "World/International"
            line = f"{prefix}{suffix_display} ({ver.rom_name})"

            if len(line) > popup_width - 4:
                line = line[:popup_width - 7] + "..."

            if is_selected:
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(y, popup_x + 2, line.ljust(popup_width - 4))
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.addstr(y, popup_x + 2, line, curses.color_pair(1))

        # Draw footer
        footer = " Enter: Select | Esc: Cancel "
        stdscr.addstr(popup_y + popup_height - 1, popup_x + (popup_width - len(footer)) // 2,
                      footer[:popup_width], curses.color_pair(1) | curses.A_DIM)

        stdscr.refresh()

        key = stdscr.getch()

        if key == 27:  # Escape
            return None
        elif key == ord("\n") or key == curses.KEY_ENTER:
            return versions[selected]
        elif key == curses.KEY_UP or key == ord("k"):
            selected = max(0, selected - 1)
        elif key == curses.KEY_DOWN or key == ord("j"):
            selected = min(len(versions) - 1, selected + 1)
        elif key == curses.KEY_HOME:
            selected = 0
        elif key == curses.KEY_END:
            selected = len(versions) - 1


def main_menu(stdscr):
    """Main menu loop."""
    # Setup colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Selected
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Category
    curses.init_pair(3, curses.COLOR_GREEN, -1)  # Filter
    curses.init_pair(4, curses.COLOR_RED, -1)  # Missing ROM

    curses.curs_set(0)  # Hide cursor
    stdscr.keypad(True)

    # Sort modes cycle order
    sort_modes = [SortMode.DEVELOPER, SortMode.QUALITY, SortMode.DIFFICULTY, SortMode.NAME]
    sort_mode = SortMode.DEVELOPER
    selected_idx = 1  # Start on first game, not category
    scroll_offset = 0
    filter_text = ""
    show_missing = False  # Hide missing ROMs by default

    while True:
        items = draw_menu(
            stdscr, sort_mode, selected_idx, scroll_offset, filter_text, show_missing
        )

        if not items:
            key = stdscr.getch()
            if key == 27 or key == ord("q") or key == ord("Q"):  # Escape or Q
                break
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                filter_text = filter_text[:-1]
            elif key == ord("\t"):  # Tab to cycle sort
                idx = sort_modes.index(sort_mode)
                sort_mode = sort_modes[(idx + 1) % len(sort_modes)]
            elif key == ord("v") or key == ord("V"):  # Toggle showing missing
                show_missing = not show_missing
            continue

        key = stdscr.getch()

        if key == 27 or key == ord("q") or key == ord("Q"):  # Escape or Q
            if filter_text:
                filter_text = ""
            else:
                break

        elif key == ord("\t"):  # Tab to cycle sort mode
            idx = sort_modes.index(sort_mode)
            sort_mode = sort_modes[(idx + 1) % len(sort_modes)]
            selected_idx = 1  # Reset selection on sort change
            scroll_offset = 0

        elif key == ord("v") or key == ord("V"):  # Toggle showing missing ROMs
            show_missing = not show_missing
            selected_idx = 1  # Reset selection
            scroll_offset = 0

        elif key == curses.KEY_UP or key == ord("k"):
            # Move up, skip categories
            new_idx = selected_idx - 1
            while new_idx >= 0 and items[new_idx][0] == "category":
                new_idx -= 1
            if new_idx >= 0:
                selected_idx = new_idx

        elif key == curses.KEY_DOWN or key == ord("j"):
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
            while (
                selected_idx < len(items) - 1 and items[selected_idx][0] == "category"
            ):
                selected_idx += 1

        elif key == curses.KEY_HOME:
            selected_idx = 0
            while selected_idx < len(items) and items[selected_idx][0] == "category":
                selected_idx += 1

        elif key == curses.KEY_END:
            selected_idx = len(items) - 1
            while selected_idx > 0 and items[selected_idx][0] == "category":
                selected_idx -= 1

        elif key == ord("\n") or key == curses.KEY_ENTER:
            if items[selected_idx][0] == "game":
                info = items[selected_idx][1]
                avail_versions = info.available_versions()

                if not avail_versions:
                    continue  # No versions available, skip

                # Determine which ROM to launch
                rom_to_launch = None
                if len(avail_versions) == 1:
                    # Only one version, launch directly
                    rom_to_launch = avail_versions[0].rom_name
                else:
                    # Multiple versions, show picker
                    selected_version = draw_version_picker(stdscr, info, 0)
                    if selected_version:
                        rom_to_launch = selected_version.rom_name

                if rom_to_launch:
                    # Clear screen before launching
                    stdscr.clear()
                    stdscr.refresh()
                    curses.endwin()

                    # Launch game
                    success, error = launch_game(rom_to_launch)

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
        menu_height = height - 6  # Account for extra footer line
        if selected_idx < scroll_offset:
            scroll_offset = selected_idx
        elif selected_idx >= scroll_offset + menu_height:
            scroll_offset = selected_idx - menu_height + 1


def launch_rom_directly(rom_path, use_mame=None):
    """Launch a ROM file directly.

    Args:
        rom_path: Path to ROM file
        use_mame: Force MAME core (True), FBNeo (False), or auto-detect (None)
    """
    config = get_config_file()
    rom_name = rom_path.stem

    # Auto-detect core if not specified
    if use_mame is None:
        use_mame = rom_name in MAME_GAMES

    core = MAME_CORE if use_mame else FBNEO_CORE
    retroarch_cmd = [
        get_retroarch_cmd(),
        "--config",
        str(config),
        "-L",
        str(core),
        str(rom_path),
    ]
    if MISTER_MODE:
        retroarch_cmd.insert(1, "-v")  # Verbose for MiSTer debugging

    # Skip game-performance in MiSTer mode (conflicts with streaming)
    if not MISTER_MODE and Path(GAME_PERFORMANCE_CMD).exists():
        cmd = [GAME_PERFORMANCE_CMD] + retroarch_cmd
    else:
        cmd = retroarch_cmd

    mode = "MiSTer CRT" if MISTER_MODE else "Desktop"
    core_name = "MAME" if use_mame else "FBNeo"
    print(f"Launching [{mode}] [{core_name}]: {rom_name}")

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
            print(
                "Build with: cd ~/src/RetroArch && ./configure --enable-mister && make"
            )
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
