#!/usr/bin/env python3
"""
FBNeo DAT file parser and query utility.

Parses ClrMame Pro XML DAT files to provide ROM metadata lookups.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator

DATS_DIR = Path(__file__).parent


@dataclass
class Game:
    """Represents a game entry from FBNeo DAT."""
    name: str  # ROM name (e.g., "ddonpach")
    description: str  # Full title (e.g., "DoDonPachi (World, 1997 2/ 5 Master Ver.)")
    year: str
    manufacturer: str
    orientation: str  # "vertical" or "horizontal"
    platform: str  # "arcade", "neogeo", "pce", etc.
    sourcefile: str  # Driver source file path
    parent: str | None  # Parent ROM if this is a clone

    @property
    def is_vertical(self) -> bool:
        return self.orientation == "vertical"

    @property
    def is_clone(self) -> bool:
        return self.parent is not None


class FBNeoDatabase:
    """Query interface for FBNeo DAT files."""

    def __init__(self, dats_dir: Path = DATS_DIR):
        self.dats_dir = dats_dir
        self._games: dict[str, Game] = {}
        self._by_manufacturer: dict[str, list[Game]] = {}
        self._loaded_platforms: set[str] = set()

    def load_dat(self, platform: str) -> int:
        """Load a DAT file for a platform. Returns number of games loaded."""
        if platform in self._loaded_platforms:
            return 0

        dat_file = self.dats_dir / f"{platform}.dat"
        if not dat_file.exists():
            raise FileNotFoundError(f"DAT file not found: {dat_file}")

        count = 0
        tree = ET.parse(dat_file)
        root = tree.getroot()

        for game_elem in root.findall("game"):
            name = game_elem.get("name", "")
            if not name:
                continue

            desc_elem = game_elem.find("description")
            year_elem = game_elem.find("year")
            mfr_elem = game_elem.find("manufacturer")
            video_elem = game_elem.find("video")

            orientation = "horizontal"
            if video_elem is not None:
                orientation = video_elem.get("orientation", "horizontal")

            game = Game(
                name=name,
                description=desc_elem.text if desc_elem is not None else name,
                year=year_elem.text if year_elem is not None else "",
                manufacturer=mfr_elem.text if mfr_elem is not None else "",
                orientation=orientation,
                platform=platform,
                sourcefile=game_elem.get("sourcefile", ""),
                parent=game_elem.get("cloneof"),
            )

            self._games[name] = game

            # Index by manufacturer
            mfr_key = game.manufacturer.lower()
            if mfr_key not in self._by_manufacturer:
                self._by_manufacturer[mfr_key] = []
            self._by_manufacturer[mfr_key].append(game)

            count += 1

        self._loaded_platforms.add(platform)
        return count

    def load_all(self) -> int:
        """Load all available DAT files."""
        total = 0
        for dat_file in self.dats_dir.glob("*.dat"):
            platform = dat_file.stem
            total += self.load_dat(platform)
        return total

    def get(self, rom_name: str) -> Game | None:
        """Get a game by ROM name."""
        return self._games.get(rom_name)

    def search(self, query: str, field: str = "description") -> Iterator[Game]:
        """Search games by field content (case-insensitive)."""
        query_lower = query.lower()
        for game in self._games.values():
            value = getattr(game, field, "")
            if query_lower in value.lower():
                yield game

    def search_manufacturer(self, mfr_query: str) -> Iterator[Game]:
        """Search games by manufacturer (case-insensitive partial match)."""
        mfr_lower = mfr_query.lower()
        for mfr_key, games in self._by_manufacturer.items():
            if mfr_lower in mfr_key:
                yield from games

    def get_by_sourcefile(self, path_fragment: str) -> Iterator[Game]:
        """Get games by sourcefile path fragment (e.g., 'cave/' or 'd_dodonpachi')."""
        for game in self._games.values():
            if path_fragment in game.sourcefile:
                yield game

    def get_vertical_games(self) -> Iterator[Game]:
        """Get all vertical (TATE) games."""
        for game in self._games.values():
            if game.is_vertical:
                yield game

    def get_parents_only(self) -> Iterator[Game]:
        """Get only parent ROMs (no clones)."""
        for game in self._games.values():
            if not game.is_clone:
                yield game

    def stats(self) -> dict:
        """Get database statistics."""
        platforms = {}
        for game in self._games.values():
            platforms[game.platform] = platforms.get(game.platform, 0) + 1

        return {
            "total_games": len(self._games),
            "platforms": platforms,
            "manufacturers": len(self._by_manufacturer),
        }


def main():
    """CLI interface for querying the database."""
    import argparse

    parser = argparse.ArgumentParser(description="Query FBNeo DAT files")
    parser.add_argument("query", nargs="?", help="ROM name or search query")
    parser.add_argument("-m", "--manufacturer", help="Search by manufacturer")
    parser.add_argument("-s", "--source", help="Search by sourcefile path")
    parser.add_argument("-v", "--vertical", action="store_true", help="Show only vertical games")
    parser.add_argument("-p", "--parents", action="store_true", help="Show only parent ROMs")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--platform", default="arcade", help="Platform to load (default: arcade)")
    parser.add_argument("--all", action="store_true", help="Load all platforms")
    args = parser.parse_args()

    db = FBNeoDatabase()

    if args.all:
        count = db.load_all()
        print(f"Loaded {count} games from all platforms")
    else:
        count = db.load_dat(args.platform)
        print(f"Loaded {count} games from {args.platform}")

    if args.stats:
        stats = db.stats()
        print(f"\nTotal games: {stats['total_games']}")
        print(f"Manufacturers: {stats['manufacturers']}")
        print("Platforms:")
        for plat, cnt in sorted(stats["platforms"].items()):
            print(f"  {plat}: {cnt}")
        return

    results = []

    if args.query:
        # First try exact ROM name lookup
        game = db.get(args.query)
        if game:
            results = [game]
        else:
            # Fall back to description search
            results = list(db.search(args.query))
    elif args.manufacturer:
        results = list(db.search_manufacturer(args.manufacturer))
    elif args.source:
        results = list(db.get_by_sourcefile(args.source))
    elif args.vertical:
        results = list(db.get_vertical_games())

    if args.parents:
        results = [g for g in results if not g.is_clone]
    if args.vertical and not args.query:
        pass  # Already filtered
    elif args.vertical:
        results = [g for g in results if g.is_vertical]

    # Print results
    for game in sorted(results, key=lambda g: (g.manufacturer, g.name)):
        orient = "V" if game.is_vertical else "H"
        clone = f" (clone of {game.parent})" if game.is_clone else ""
        print(f"{game.name:24} {game.year} {orient} [{game.manufacturer}] {game.description[:50]}{clone}")

    if results:
        print(f"\n{len(results)} games found")


if __name__ == "__main__":
    main()
