#!/usr/bin/env python3
"""
Master Shmup Game Database

Central database of shmups with metadata from multiple sources:
- FBNeo DAT files (ROM names, manufacturers, orientation)
- 1CC Difficulty Index (quality, difficulty, routing)
- Japanese Difficulty Index (0-45 scale)
- Top 25 / Honorable Mentions lists

This file is the single source of truth for both shmupfetch and shmuparch.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Platform(Enum):
    """Game platform."""
    ARCADE = "AC"
    NEOGEO = "NG"
    PCE = "PCE"      # PC Engine / TurboGrafx-16
    GENESIS = "GEN"  # Mega Drive / Genesis
    SNES = "SNES"
    PS1 = "PS1"
    PS2 = "PS2"
    SATURN = "SAT"
    DREAMCAST = "DC"
    X360 = "360"
    PC = "PC"
    NDS = "NDS"
    PSP = "PSP"
    NSW = "NSW"      # Nintendo Switch
    GB = "GB"
    GG = "GG"        # Game Gear
    NES = "NES"
    OTHER = "OTHER"


class Orientation(Enum):
    """Screen orientation."""
    TATE = 1   # Vertical
    YOKO = 0   # Horizontal


class Routing(Enum):
    """Route complexity for 1CC."""
    LOW = 1
    MED = 5
    HIGH = 9


@dataclass
class GameVersion:
    """A specific version/variant of a game."""
    rom_name: str                          # FBNeo ROM name (e.g., "ddonpach", "ddonpachj")
    suffix: str = ""                       # Version suffix (e.g., "Japan", "Black Label")
    difficulty_jp: Optional[int] = None    # Japanese index (0-45)
    goal: str = ""                         # Goal for JP index (e.g., "2-ALL", "Ultra")
    notes: str = ""                        # Additional notes


@dataclass
class Game:
    """A shmup game entry."""
    # Core identification
    name: str                              # Canonical name (e.g., "DoDonPachi")
    developer: str                         # Primary developer
    year: int                              # Release year
    platform: Platform                     # Primary platform

    # FBNeo ROM info (for arcade games)
    rom_name: str = ""                     # Primary ROM name
    orientation: Orientation = Orientation.TATE

    # Emulation settings
    runahead_frames: int = 1               # RetroArch runahead frames for input lag
    requires_mame: bool = False            # Requires MAME core (ST-V, Naomi, etc.)

    # Difficulty ratings (1CC English index, 1-10 scale)
    quality: Optional[int] = None          # Game quality rating
    difficulty_1cc: Optional[int] = None   # 1CC difficulty
    routing: Routing = Routing.LOW         # Route complexity

    # Japanese difficulty index (0-45 scale, higher = harder)
    difficulty_jp: Optional[int] = None
    goal_jp: str = ""                      # Goal for JP rating (e.g., "2-ALL")

    # Clear time (1-ALL in minutes, typical non-speedrun pace)
    clear_time_1all: Optional[int] = None  # Minutes to clear first loop

    # Variants (different versions with potentially different difficulties)
    versions: list[GameVersion] = field(default_factory=list)

    # Metadata
    aliases: list[str] = field(default_factory=list)  # Alternative names
    notes: str = ""


# =============================================================================
# MASTER GAME DATABASE
# =============================================================================

GAMES: dict[str, Game] = {}

def _add(g: Game):
    """Helper to add a game to the database."""
    GAMES[g.rom_name if g.rom_name else g.name.lower().replace(" ", "")] = g
    # Also index by aliases
    for alias in g.aliases:
        key = alias.lower().replace(" ", "").replace("-", "").replace(":", "")
        if key not in GAMES:
            GAMES[key] = g


# =============================================================================
# CAVE GAMES
# =============================================================================

_add(Game(
    name="DonPachi",
    developer="Cave",
    year=1995,
    platform=Platform.ARCADE,
    rom_name="donpachi",
    orientation=Orientation.TATE,
    quality=6, difficulty_1cc=4, routing=Routing.LOW,
    difficulty_jp=16, goal_jp="1-ALL",
    clear_time_1all=18,
    versions=[
        GameVersion("donpachi", "USA"),
        GameVersion("donpachij", "Japan"),
        GameVersion("donpachikr", "Korea"),
        GameVersion("donpachihk", "Hong Kong"),
    ],
    notes="-3 for US version; +2 for Hong Kong version (JP index)",
))

_add(Game(
    name="DoDonPachi",
    developer="Cave",
    year=1997,
    platform=Platform.ARCADE,
    rom_name="ddonpach",
    orientation=Orientation.TATE,
    quality=7, difficulty_1cc=6, routing=Routing.LOW,
    difficulty_jp=17, goal_jp="1-ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("ddonpach", "World"),
        GameVersion("ddonpachj", "Japan"),
        GameVersion("ddonpacha", "Arrange 1.1"),
    ],
))

_add(Game(
    name="DoDonPachi Dai-Ou-Jou",
    developer="Cave",
    year=2002,
    platform=Platform.ARCADE,
    rom_name="ddpdoj",
    orientation=Orientation.TATE,
    quality=9, difficulty_1cc=10, routing=Routing.HIGH,
    difficulty_jp=22, goal_jp="1-ALL",
    clear_time_1all=23,
    versions=[
        GameVersion("ddpdoj", "Master Ver", difficulty_jp=22, goal="1-ALL"),
        GameVersion("ddpdoja", "Master Ver A"),
        GameVersion("ddpdojb", "Master Ver B"),
        GameVersion("ddpdojp", "Prototype"),
        GameVersion("ddpdojblk", "Black Label", difficulty_jp=37, goal="2-ALL"),
        GameVersion("ddpdojblka", "Black Label A"),
        GameVersion("ddpdojblkb", "Black Label B"),
    ],
    aliases=["DoDonPachi DOJ", "ddpdoj", "ddp3"],
    notes="WL 2-ALL is difficulty 45 (JP index)",
))

_add(Game(
    name="DoDonPachi Dai-Fukkatsu",
    developer="Cave",
    year=2008,
    platform=Platform.ARCADE,
    rom_name="ddpdfk",
    orientation=Orientation.TATE,
    quality=5, difficulty_1cc=4, routing=Routing.LOW,
    difficulty_jp=12, goal_jp="1-ALL Strong",
    clear_time_1all=24,
    versions=[
        GameVersion("ddpdfk", "Ver 1.5", difficulty_jp=23, goal="2-ALL Omote Strong"),
        GameVersion("ddpdfk10", "Ver 1.0"),
        GameVersion("dfkbl", "Black Label", difficulty_jp=28, goal="via Hibachi Bomb"),
    ],
    aliases=["DoDonPachi Resurrection", "Daifukkatsu", "DFK"],
    notes="+2/+5/+6 for Bomb/Power style (JP index)",
))

_add(Game(
    name="DoDonPachi SaiDaiOuJou",
    developer="Cave",
    year=2012,
    platform=Platform.ARCADE,
    rom_name="ddpsdoj",
    orientation=Orientation.TATE,
    difficulty_jp=31, goal_jp="ALL via Hibachi",
    clear_time_1all=24,
    versions=[
        GameVersion("ddpsdoj", "Master Ver", difficulty_jp=31, goal="ALL via Hibachi"),
        GameVersion("sdojak", "Arrange"),
    ],
    aliases=["SDOJ"],
    notes="-11 without Hibachi (JP index)",
))

_add(Game(
    name="ESP Ra.De.",
    developer="Cave",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="esprade",
    orientation=Orientation.TATE,
    runahead_frames=2,
    difficulty_jp=20, goal_jp="ALL",
    clear_time_1all=15,
    versions=[
        GameVersion("esprade", "International"),
        GameVersion("espradej", "Japan Master"),
        GameVersion("espradejo", "Japan Older"),
    ],
    aliases=["Esprade"],
))

_add(Game(
    name="Guwange",
    developer="Cave",
    year=1999,
    platform=Platform.ARCADE,
    rom_name="guwange",
    orientation=Orientation.TATE,
    runahead_frames=2,
    difficulty_jp=20, goal_jp="ALL",
    clear_time_1all=18,
    versions=[
        GameVersion("guwange", "Master Ver"),
        GameVersion("guwangea", "Older Ver"),
    ],
))

_add(Game(
    name="Dangun Feveron",
    developer="Cave",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="dfeveron",
    orientation=Orientation.TATE,
    difficulty_jp=30, goal_jp="ALL via TLB",
    clear_time_1all=18,
    versions=[
        GameVersion("dfeveron", "Japan"),
        GameVersion("feversos", "Fever SOS (World)"),
    ],
    aliases=["Fever SOS"],
    notes="-2 if no TLB; +11 if playing as Uotaro (JP index)",
))

_add(Game(
    name="Espgaluda",
    developer="Cave",
    year=2003,
    platform=Platform.ARCADE,
    rom_name="espgal",
    orientation=Orientation.TATE,
    quality=8, difficulty_1cc=6, routing=Routing.MED,
    difficulty_jp=16, goal_jp="ALL",
    clear_time_1all=18,
    versions=[
        GameVersion("espgal", "Master Ver"),
        GameVersion("espgala", "Older Ver A"),
        GameVersion("espgalb", "Older Ver B"),
    ],
))

_add(Game(
    name="Espgaluda II",
    developer="Cave",
    year=2005,
    platform=Platform.ARCADE,
    rom_name="espgal2",
    orientation=Orientation.TATE,
    difficulty_jp=22, goal_jp="ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("espgal2", "Master Ver"),
        GameVersion("espgal2a", "Older A"),
        GameVersion("espgal2b", "Older B"),
    ],
    notes="+4 for Shin Seseri (JP index)",
))

_add(Game(
    name="Mushihimesama",
    developer="Cave",
    year=2004,
    platform=Platform.ARCADE,
    rom_name="mushisam",
    orientation=Orientation.TATE,
    quality=10, difficulty_1cc=5, routing=Routing.LOW,
    difficulty_jp=15, goal_jp="Original",
    clear_time_1all=18,
    versions=[
        GameVersion("mushisam", "Master Ver", difficulty_jp=15, goal="Original"),
        GameVersion("mushisama", "Older A"),
        GameVersion("mushisamb", "Older B"),
    ],
    notes="Maniac=18, Ultra=42 (JP index)",
))

_add(Game(
    name="Mushihimesama Futari",
    developer="Cave",
    year=2006,
    platform=Platform.ARCADE,
    rom_name="futari15",
    orientation=Orientation.TATE,
    quality=10, difficulty_1cc=8, routing=Routing.LOW,
    difficulty_jp=16, goal_jp="Original 1.5",
    clear_time_1all=20,
    versions=[
        GameVersion("futari10", "Ver 1.0"),
        GameVersion("futari15", "Ver 1.5", difficulty_jp=16, goal="Original"),
        GameVersion("futari15a", "Ver 1.5 Older"),
        GameVersion("futaribl", "Black Label", difficulty_jp=35, goal="God mode"),
        GameVersion("futariblj", "Black Label Japan"),
    ],
    notes="Maniac 1.5=23, Ultra 1.5=44 (JP index)",
))

_add(Game(
    name="Ibara",
    developer="Cave",
    year=2005,
    platform=Platform.ARCADE,
    rom_name="ibara",
    orientation=Orientation.TATE,
    difficulty_jp=24, goal_jp="ALL",
    clear_time_1all=26,
    versions=[
        GameVersion("ibara", "Master Ver"),
        GameVersion("ibarao", "Older"),
        GameVersion("ibarablk", "Kuro Black Label"),
        GameVersion("ibarablka", "Kuro Black Label A"),
    ],
    notes="1P side (JP index)",
))

_add(Game(
    name="Pink Sweets",
    developer="Cave",
    year=2006,
    platform=Platform.ARCADE,
    rom_name="pinkswts",
    orientation=Orientation.TATE,
    difficulty_jp=15, goal_jp="ALL",
    clear_time_1all=23,
    versions=[
        GameVersion("pinkswts", "Master Ver"),
        GameVersion("pinkswtsa", "Older A"),
        GameVersion("pinkswtsb", "Older B"),
        GameVersion("pinkswtsx", "X"),
        GameVersion("pinkswtssc", "Suicide Cab"),
    ],
    notes="with infinite lives trick (JP index)",
))

_add(Game(
    name="Muchi Muchi Pork!",
    developer="Cave",
    year=2007,
    platform=Platform.ARCADE,
    rom_name="mmpork",
    orientation=Orientation.TATE,
    difficulty_jp=24, goal_jp="1-ALL",
))

_add(Game(
    name="Deathsmiles",
    developer="Cave",
    year=2007,
    platform=Platform.ARCADE,
    rom_name="deathsml",
    orientation=Orientation.YOKO,
    quality=8, difficulty_1cc=5, routing=Routing.LOW,
    difficulty_jp=9, goal_jp="No Canyon",
    clear_time_1all=18,
    versions=[
        GameVersion("deathsml", "Master Ver", difficulty_jp=9, goal="No Canyon"),
    ],
    notes="ALL via Extra LV3=27, -9 without Extra (JP index)",
))

_add(Game(
    name="Deathsmiles MegaBlack Label",
    developer="Cave",
    year=2008,
    platform=Platform.ARCADE,
    rom_name="dsmbl",
    orientation=Orientation.YOKO,
    quality=8, difficulty_1cc=5, routing=Routing.LOW,
    difficulty_jp=37, goal_jp="LV999",
    clear_time_1all=20,
    notes="+2 for Canyon; +4 for TLB (JP index)",
))

_add(Game(
    name="Akai Katana",
    developer="Cave",
    year=2010,
    platform=Platform.ARCADE,
    rom_name="akatana",
    orientation=Orientation.YOKO,
    quality=9, difficulty_1cc=6, routing=Routing.LOW,
    clear_time_1all=20,
    difficulty_jp=13, goal_jp="ALL",
))

_add(Game(
    name="Ketsui",
    developer="Cave",
    year=2003,
    platform=Platform.ARCADE,
    rom_name="ket",
    orientation=Orientation.TATE,
    difficulty_jp=21, goal_jp="1-ALL Tiger",
    clear_time_1all=20,
    versions=[
        GameVersion("ket", "Master Ver", difficulty_jp=21, goal="1-ALL Tiger"),
        GameVersion("keta", "Older A"),
        GameVersion("ketb", "Older B"),
        GameVersion("ketarr", "Arrange"),
        GameVersion("ketarr151", "Arrange 1.51"),
    ],
    notes="2-ALL Omote=36, 2-ALL Ura=43, +1 for Tiger Schwert (JP index)",
))

_add(Game(
    name="Progear",
    developer="Cave",
    year=2001,
    platform=Platform.ARCADE,
    rom_name="progear",
    orientation=Orientation.YOKO,
    runahead_frames=3,
    difficulty_jp=18, goal_jp="1-ALL",
    clear_time_1all=25,
    versions=[
        GameVersion("progear", "USA"),
        GameVersion("progeara", "Asia"),
        GameVersion("progearj", "Japan"),
    ],
    notes="2-ALL=38 (JP index)",
))


# =============================================================================
# TOAPLAN GAMES
# =============================================================================

_add(Game(
    name="Batsugun",
    developer="Toaplan",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="batsugun",
    orientation=Orientation.TATE,
    quality=8, difficulty_1cc=7, routing=Routing.MED,
    difficulty_jp=12, goal_jp="ALL",
    clear_time_1all=18,
    versions=[
        GameVersion("batsugun", "World"),
        GameVersion("batsugunj", "Japan"),
        GameVersion("batsugunsp", "Special Version", difficulty_jp=3, goal="1-ALL"),
    ],
    notes="Special 4-ALL=24 (JP index)",
))

_add(Game(
    name="Truxton",
    developer="Toaplan",
    year=1988,
    platform=Platform.ARCADE,
    rom_name="truxton",
    orientation=Orientation.TATE,
    difficulty_jp=20, goal_jp="1-ALL",
    clear_time_1all=22,
    versions=[
        GameVersion("truxton", "World"),
        GameVersion("tatsujn", "Tatsujin Japan"),
    ],
    aliases=["Tatsujin"],
    notes="-7 with autofire (JP index)",
))

_add(Game(
    name="Truxton II",
    developer="Toaplan",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="truxton2",
    orientation=Orientation.TATE,
    aliases=["Tatsujin Oh"],
))

_add(Game(
    name="Fire Shark",
    developer="Toaplan",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="fireshrk",
    orientation=Orientation.TATE,
    quality=6, difficulty_1cc=1, routing=Routing.LOW,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("fireshrk", "Fire Shark"),
        GameVersion("samesame", "Same! Same! Same!"),
    ],
    aliases=["Same! Same! Same!"],
    notes="-10 with autofire; -10 for international (JP index)",
))

_add(Game(
    name="Vimana",
    developer="Toaplan",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="vimana",
    orientation=Orientation.TATE,
    difficulty_jp=3, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="+2 without autofire (JP index)",
))

_add(Game(
    name="Dogyuun",
    developer="Toaplan",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="dogyuun",
    orientation=Orientation.TATE,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="-2 with autofire (JP index)",
))

_add(Game(
    name="Zero Wing",
    developer="Toaplan",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="zerowing",
    orientation=Orientation.YOKO,
    difficulty_jp=15, goal_jp="1-ALL",
    clear_time_1all=28,
    notes="+4 no autofire; +7 for 2-ALL; +30 for 3-ALL+ (JP index)",
))

_add(Game(
    name="Out Zone",
    developer="Toaplan",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="outzone",
    orientation=Orientation.TATE,
    difficulty_jp=16, goal_jp="1-ALL",
))

_add(Game(
    name="Hellfire",
    developer="Toaplan",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="hellfire",
    orientation=Orientation.YOKO,
))

_add(Game(
    name="Flying Shark",
    developer="Toaplan",
    year=1987,
    platform=Platform.ARCADE,
    rom_name="fshark",
    orientation=Orientation.TATE,
    difficulty_jp=16, goal_jp="1-ALL",
    clear_time_1all=18,
    versions=[
        GameVersion("fshark", "Flying Shark World"),
        GameVersion("fsharkj", "Hishouzame Japan"),
    ],
    aliases=["Hishouzame", "Sky Shark"],
))

_add(Game(
    name="Twin Cobra",
    developer="Toaplan",
    year=1987,
    platform=Platform.ARCADE,
    rom_name="twincobr",
    orientation=Orientation.TATE,
    versions=[
        GameVersion("twincobr", "World"),
        GameVersion("twincobrj", "Kyukyoku Tiger Japan"),
    ],
    aliases=["Kyukyoku Tiger"],
))

_add(Game(
    name="Grind Stormer",
    developer="Toaplan",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="grindstm",
    orientation=Orientation.TATE,
    difficulty_jp=32, goal_jp="2-ALL",
    clear_time_1all=25,
    versions=[
        GameVersion("grindstm", "Grind Stormer World"),
        GameVersion("vfive", "V-Five Japan"),
    ],
    aliases=["V-Five", "V-V"],
))

_add(Game(
    name="FixEight",
    developer="Toaplan",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="fixeight",
    orientation=Orientation.TATE,
    difficulty_jp=18, goal_jp="1-ALL",
))


# =============================================================================
# RAIZING / EIGHTING GAMES
# =============================================================================

_add(Game(
    name="Battle Garegga",
    developer="Raizing",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="bgaregga",
    orientation=Orientation.TATE,
    runahead_frames=3,
    difficulty_jp=26, goal_jp="1-loop with Golden Bat",
    clear_time_1all=30,
    versions=[
        GameVersion("bgaregga", "Europe/USA/Japan/Asia", notes="Vanilla unpatched"),
        GameVersion("bgareggaz", "Zakk QoL patch (Sept 2019)", notes="Rank display (Stage Edit DIP), no rank carryover, guest ships unlocked, quick reset (Start+ABC), scoreboard fix"),
        GameVersion("bgareggat2", "Type 2"),
        GameVersion("bgareggahk", "Hong Kong"),
        GameVersion("bgaregganv", "New Version"),
        GameVersion("bgareggacn", "China"),
    ],
    notes="bgareggaz adds QoL features. Harder (extended)=35, +1 for extended two-loop (JP index)",
))

_add(Game(
    name="Armed Police Batrider",
    developer="Raizing",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="batrider",
    orientation=Orientation.TATE,
    runahead_frames=3,
    quality=8, difficulty_1cc=6, routing=Routing.LOW,
    difficulty_jp=25, goal_jp="Advanced course",
    clear_time_1all=28,
    versions=[
        GameVersion("batrider", "Europe"),
        GameVersion("batriderj", "Japan"),
        GameVersion("batriderk", "Korea"),
        GameVersion("batridert", "Taiwan"),
        GameVersion("batriderhk", "Hong Kong"),
    ],
))

_add(Game(
    name="Battle Bakraid",
    developer="Raizing",
    year=1999,
    platform=Platform.ARCADE,
    rom_name="bbakraid",
    orientation=Orientation.TATE,
    runahead_frames=3,
    quality=8, difficulty_1cc=6, routing=Routing.LOW,
    difficulty_jp=22, goal_jp="Advanced course",
    clear_time_1all=26,
    versions=[
        GameVersion("bbakraid", "Unlimited USA"),
        GameVersion("bbakraidj", "Unlimited Japan"),
        GameVersion("bbakraidja", "Japan Apr 7"),
        GameVersion("bbakraidc", "Unlimited China"),
    ],
    notes="with F-111B (JP index)",
))

_add(Game(
    name="Mahou Daisakusen",
    developer="Raizing",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="mahoudai",
    orientation=Orientation.TATE,
    difficulty_jp=18, goal_jp="1-ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("mahoudai", "Japan"),
        GameVersion("sstriker", "Sorcer Striker World"),
    ],
    aliases=["Sorcer Striker"],
    notes="2-ALL=36; -5 for international (JP index)",
))

_add(Game(
    name="Shippu Mahou Daisakusen",
    developer="Raizing",
    year=1994,
    platform=Platform.ARCADE,
    rom_name="shippumd",
    orientation=Orientation.TATE,
    difficulty_jp=14, goal_jp="1-ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("shippumd", "Japan"),
        GameVersion("kingdmgp", "Kingdom Grandprix"),
    ],
    aliases=["Kingdom Grandprix"],
    notes="2-ALL=27 (JP index)",
))

_add(Game(
    name="Great Mahou Daisakusen",
    developer="Raizing",
    year=2000,
    platform=Platform.ARCADE,
    rom_name="gmahou",
    orientation=Orientation.TATE,
    difficulty_jp=23, goal_jp="1-loop with Birthday",
    clear_time_1all=25,
    versions=[
        GameVersion("gmahou", "Japan"),
        GameVersion("dimahoo", "Dimahoo Europe"),
        GameVersion("dimahoou", "Dimahoo USA"),
    ],
    aliases=["Dimahoo"],
))

_add(Game(
    name="Soukyugurentai",
    developer="Raizing",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="sokyugrt",
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=25, goal_jp="ALL",
    clear_time_1all=22,
    aliases=["Terra Diver"],
    notes="with Toryu; ST-V hardware",
))

_add(Game(
    name="1944: The Loop Master",
    developer="Raizing",
    year=2000,
    platform=Platform.ARCADE,
    rom_name="1944",
    orientation=Orientation.YOKO,
    difficulty_jp=27, goal_jp="1-loop mode",
    clear_time_1all=22,
    versions=[
        GameVersion("1944", "Europe"),
        GameVersion("1944j", "Japan"),
        GameVersion("1944u", "USA"),
    ],
))


# =============================================================================
# PSIKYO GAMES
# =============================================================================

_add(Game(
    name="Gunbird",
    developer="Psikyo",
    year=1994,
    platform=Platform.ARCADE,
    rom_name="gunbird",
    orientation=Orientation.TATE,
    runahead_frames=4,
    difficulty_jp=17, goal_jp="1-ALL",
    clear_time_1all=11,
    versions=[
        GameVersion("gunbird", "World"),
        GameVersion("gunbirdj", "Japan"),
        GameVersion("gunbirdk", "Korea"),
    ],
    notes="2-ALL=38 (JP index)",
))

_add(Game(
    name="Gunbird 2",
    developer="Psikyo",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="gunbird2",
    orientation=Orientation.TATE,
    runahead_frames=4,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=13,
    notes="2-ALL=39 (JP index)",
))

_add(Game(
    name="Strikers 1945",
    developer="Psikyo",
    year=1995,
    platform=Platform.ARCADE,
    rom_name="s1945",
    orientation=Orientation.TATE,
    runahead_frames=4,
    difficulty_jp=20, goal_jp="1-ALL",
    clear_time_1all=10,
    versions=[
        GameVersion("s1945", "World"),
        GameVersion("s1945j", "Japan"),
        GameVersion("s1945k", "Korea"),
    ],
    notes="2-ALL with BF-109/P-51=40 (JP index)",
))

_add(Game(
    name="Strikers 1945 II",
    developer="Psikyo",
    year=1997,
    platform=Platform.ARCADE,
    rom_name="s1945ii",
    orientation=Orientation.TATE,
    difficulty_jp=21, goal_jp="1-ALL Hayate",
    clear_time_1all=10,
    notes="2-ALL with Flying Pancake=39 (JP index)",
))

_add(Game(
    name="Strikers 1945 III",
    developer="Psikyo",
    year=1999,
    platform=Platform.ARCADE,
    rom_name="s1945iii",
    orientation=Orientation.TATE,
    difficulty_jp=20, goal_jp="1-ALL",
    clear_time_1all=11,
    versions=[
        GameVersion("s1945iii", "World/Japan"),
        GameVersion("s1945p", "Strikers 1945 Plus"),
    ],
    aliases=["Strikers 1999"],
    notes="2-ALL with Pancake=35, +4 with other ships (JP index)",
))

_add(Game(
    name="Samurai Aces",
    developer="Psikyo",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="samuraia",
    orientation=Orientation.TATE,
    difficulty_jp=12, goal_jp="1-ALL Aine",
    clear_time_1all=9,
    versions=[
        GameVersion("samuraia", "World"),
        GameVersion("sngkace", "Sengoku Ace Japan"),
    ],
    aliases=["Sengoku Ace"],
    notes="2-ALL with Aine=24; +7 with Kenoumaru (JP index)",
))

_add(Game(
    name="Tengai",
    developer="Psikyo",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="tengai",
    orientation=Orientation.YOKO,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=12,
    versions=[
        GameVersion("tengai", "World"),
        GameVersion("tengaij", "Sengoku Blade Japan"),
    ],
    aliases=["Sengoku Blade"],
    notes="2-ALL with A autofire=42 (JP index)",
))

_add(Game(
    name="Sol Divide",
    developer="Psikyo",
    year=1997,
    platform=Platform.ARCADE,
    rom_name="soldivid",
    orientation=Orientation.YOKO,
    difficulty_jp=16, goal_jp="1-ALL",
))

_add(Game(
    name="Dragon Blaze",
    developer="Psikyo",
    year=2000,
    platform=Platform.ARCADE,
    rom_name="dragnblz",
    orientation=Orientation.TATE,
    difficulty_jp=21, goal_jp="1-ALL",
    clear_time_1all=11,
    notes="2-ALL=37 (JP index)",
))

_add(Game(
    name="Zero Gunner 2",
    developer="Psikyo",
    year=2001,
    platform=Platform.ARCADE,
    rom_name="zgundm2",
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=20, goal_jp="1-ALL",
    clear_time_1all=11,
    notes="2-ALL=37; Naomi hardware",
))

_add(Game(
    name="Gunbarich",
    developer="Psikyo",
    year=2001,
    platform=Platform.ARCADE,
    rom_name="gnbarich",
    orientation=Orientation.TATE,
))

_add(Game(
    name="Space Bomber",
    developer="Psikyo",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="sbomber",
    orientation=Orientation.TATE,
    difficulty_jp=13, goal_jp="ALL tetris block",
    clear_time_1all=15,
    notes="Ver. B; Ver. B normal=25 (JP index)",
))


# =============================================================================
# IREM GAMES
# =============================================================================

_add(Game(
    name="R-Type",
    developer="Irem",
    year=1987,
    platform=Platform.ARCADE,
    rom_name="rtype",
    orientation=Orientation.YOKO,
    runahead_frames=2,
    quality=10, difficulty_1cc=7, routing=Routing.HIGH,
    difficulty_jp=18, goal_jp="1-ALL",
    clear_time_1all=25,
    versions=[
        GameVersion("rtype", "World"),
        GameVersion("rtypej", "Japan"),
        GameVersion("rtypeu", "USA"),
    ],
    notes="2-ALL=29; -3 with autofire (JP index)",
))

_add(Game(
    name="R-Type II",
    developer="Irem",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="rtype2",
    orientation=Orientation.YOKO,
    runahead_frames=2,
    quality=8, difficulty_1cc=8, routing=Routing.HIGH,
    difficulty_jp=19, goal_jp="1-ALL",
    clear_time_1all=22,
    versions=[
        GameVersion("rtype2", "World"),
        GameVersion("rtype2j", "Japan"),
    ],
    notes="2-ALL=36; -2 autofire; -2 international (JP index)",
))

_add(Game(
    name="R-Type Leo",
    developer="Irem",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="rtypeleo",
    orientation=Orientation.YOKO,
    runahead_frames=3,
    quality=6, difficulty_1cc=6, routing=Routing.HIGH,
    difficulty_jp=15, goal_jp="ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("rtypeleo", "World"),
        GameVersion("rtypeleoj", "Japan"),
    ],
))

_add(Game(
    name="Image Fight",
    developer="Irem",
    year=1988,
    platform=Platform.ARCADE,
    rom_name="imgfight",
    orientation=Orientation.TATE,
    difficulty_jp=18, goal_jp="1-ALL",
    clear_time_1all=22,
    notes="no penalty area; 2-ALL no補習=36; +8 for loop 2 penalty areas (JP index)",
))

_add(Game(
    name="X-Multiply",
    developer="Irem",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="xmultipl",
    orientation=Orientation.YOKO,
    difficulty_jp=15, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="2-ALL=26 (JP index)",
))

_add(Game(
    name="Air Duel",
    developer="Irem",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="airduel",
    orientation=Orientation.TATE,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="without autofire (JP index)",
))

_add(Game(
    name="In The Hunt",
    developer="Irem",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="inthunt",
    orientation=Orientation.YOKO,
    difficulty_jp=23, goal_jp="ALL",
    clear_time_1all=22,
    versions=[
        GameVersion("inthunt", "World"),
        GameVersion("inthuntu", "USA"),
        GameVersion("kaiteids", "Kaitei Daisensou Japan"),
    ],
    aliases=["Kaitei Daisensou"],
))

_add(Game(
    name="Dragon Breed",
    developer="Irem",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="dbreed",
    orientation=Orientation.YOKO,
    difficulty_jp=5, goal_jp="1-ALL",
))

_add(Game(
    name="Mystic Riders",
    developer="Irem",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="mysticri",
    orientation=Orientation.YOKO,
    difficulty_jp=15, goal_jp="1-ALL",
    clear_time_1all=22,
    aliases=["Gun Hohki"],
    notes="2-ALL=39 (JP index)",
))


# =============================================================================
# SEIBU KAIHATSU GAMES
# =============================================================================

_add(Game(
    name="Raiden",
    developer="Seibu Kaihatsu",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="raiden",
    orientation=Orientation.TATE,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=28,
    notes="+2 without autofire (JP index)",
))

_add(Game(
    name="Raiden II",
    developer="Seibu Kaihatsu",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="raiden2",
    orientation=Orientation.TATE,
    difficulty_jp=30, goal_jp="1-ALL",
    clear_time_1all=30,
    versions=[
        GameVersion("raiden2", "World"),
        GameVersion("raiden2j", "Japan"),
        GameVersion("raiden2u", "USA"),
    ],
    notes="+5 without autofire; -1 international (JP index)",
))

_add(Game(
    name="Raiden DX",
    developer="Seibu Kaihatsu",
    year=1994,
    platform=Platform.ARCADE,
    rom_name="raidendx",
    orientation=Orientation.TATE,
    quality=7, difficulty_1cc=6, routing=Routing.LOW,
    difficulty_jp=5, goal_jp="Practice course radar",
    clear_time_1all=25,
    versions=[
        GameVersion("raidendx", "UK"),
        GameVersion("raidendxj", "Japan"),
        GameVersion("raidendxu", "USA"),
    ],
    notes="Novice=13, Practice 1-5=24, Practice 1-8=33, Expert no 9th=21 (JP index)",
))

_add(Game(
    name="Raiden Fighters",
    developer="Seibu Kaihatsu",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="rdft",
    orientation=Orientation.TATE,
    difficulty_jp=7, goal_jp="ALL as Slave",
    clear_time_1all=20,
    versions=[
        GameVersion("rdft", "Germany"),
        GameVersion("rdftj", "Japan"),
        GameVersion("rdftu", "USA"),
    ],
    notes="+10 to +16 with others (JP index)",
))

_add(Game(
    name="Raiden Fighters 2",
    developer="Seibu Kaihatsu",
    year=1997,
    platform=Platform.ARCADE,
    rom_name="rdft2",
    orientation=Orientation.TATE,
    quality=7, difficulty_1cc=6, routing=Routing.LOW,
    difficulty_jp=2, goal_jp="ALL with TLB Fairy",
    clear_time_1all=20,
    versions=[
        GameVersion("rdft2", "Germany"),
        GameVersion("rdft2j", "Japan"),
        GameVersion("rdft2u", "USA"),
    ],
    notes="+2 Slave; +18 to +22 others (JP index)",
))

_add(Game(
    name="Raiden Fighters Jet",
    developer="Seibu Kaihatsu",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="rfjet",
    orientation=Orientation.TATE,
    quality=6, difficulty_1cc=4, routing=Routing.LOW,
    difficulty_jp=9, goal_jp="ALL3 with TLB Fairy",
    clear_time_1all=22,
    versions=[
        GameVersion("rfjet", "Germany"),
        GameVersion("rfjetj", "Japan"),
        GameVersion("rfjetu", "USA"),
    ],
    notes="+5 Slave; +15 to +20 others (JP index)",
))

_add(Game(
    name="Viper Phase 1",
    developer="Seibu Kaihatsu",
    year=1995,
    platform=Platform.ARCADE,
    rom_name="viprp1",
    orientation=Orientation.TATE,
    difficulty_jp=27, goal_jp="ALL new ver",
    clear_time_1all=25,
    notes="old ver no autofire=36; -6/-3 with autofire (JP index)",
))


# =============================================================================
# KONAMI GAMES
# =============================================================================

_add(Game(
    name="Gradius",
    developer="Konami",
    year=1985,
    platform=Platform.ARCADE,
    rom_name="gradius",
    orientation=Orientation.YOKO,
    quality=4, difficulty_1cc=4, routing=Routing.HIGH,
    difficulty_jp=10, goal_jp="1-ALL",
    clear_time_1all=15,
    aliases=["Nemesis"],
))

_add(Game(
    name="Gradius II",
    developer="Konami",
    year=1988,
    platform=Platform.ARCADE,
    rom_name="gradius2",
    orientation=Orientation.YOKO,
    quality=5, difficulty_1cc=5, routing=Routing.HIGH,
    difficulty_jp=11, goal_jp="1-ALL type 4",
    clear_time_1all=28,
    aliases=["Gofer no Yabou"],
    notes="+1 for type 3; +2 for type 1/2 (JP index)",
))

_add(Game(
    name="Gradius III",
    developer="Konami",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="gradius3",
    orientation=Orientation.YOKO,
    quality=6, difficulty_1cc=4, routing=Routing.HIGH,
    difficulty_jp=30, goal_jp="1-ALL type B",
    clear_time_1all=35,
    notes="+2 A, +4 C, +1 D; +2 for 2-ALL; +13 for 3-ALL+ (JP index)",
))

_add(Game(
    name="Gradius IV",
    developer="Konami",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="gradius4",  # Hornet hardware
    orientation=Orientation.YOKO,
    requires_mame=True,
    difficulty_jp=23, goal_jp="1-ALL equip 5",
    clear_time_1all=28,
    notes="+1 equip 1; +2 equip 2/6; +4 equip 3 (JP index)",
))

_add(Game(
    name="Salamander",
    developer="Konami",
    year=1986,
    platform=Platform.ARCADE,
    rom_name="salamand",
    orientation=Orientation.YOKO,
    difficulty_jp=9, goal_jp="1-ALL",
    clear_time_1all=15,
    versions=[
        GameVersion("salamand", "World"),
        GameVersion("salamandj", "Japan"),
        GameVersion("lifefrce", "Life Force World"),
        GameVersion("lifefrceja", "Life Force Japan"),
    ],
    aliases=["Life Force"],
    notes="with autofire (JP index)",
))

_add(Game(
    name="Salamander 2",
    developer="Konami",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="salamand2",
    orientation=Orientation.YOKO,
    requires_mame=True,
    difficulty_jp=11, goal_jp="1-ALL",
    clear_time_1all=18,
    notes="2-ALL=24; System GX hardware",
))

_add(Game(
    name="Parodius Da!",
    developer="Konami",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="parodius",
    orientation=Orientation.YOKO,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=28,
    notes="2-ALL=44 (JP index)",
))

_add(Game(
    name="Gokujou Parodius",
    developer="Konami",
    year=1994,
    platform=Platform.ARCADE,
    rom_name="gokuparo",
    orientation=Orientation.YOKO,
    difficulty_jp=23, goal_jp="via Special stage",
    clear_time_1all=26,
    notes="-10 if no special stage (JP index)",
))

_add(Game(
    name="Sexy Parodius",
    developer="Konami",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="sexyparo",
    orientation=Orientation.YOKO,
    difficulty_jp=25, goal_jp="via Special stage",
    clear_time_1all=26,
    notes="-10 if no special stage (JP index)",
))

_add(Game(
    name="Xexex",
    developer="Konami",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="xexex",
    orientation=Orientation.YOKO,
    quality=9, difficulty_1cc=7, routing=Routing.HIGH,
    difficulty_jp=14, goal_jp="1-ALL",
    clear_time_1all=25,
    notes="2-ALL=40; +6 international (JP index)",
))

_add(Game(
    name="Thunder Cross",
    developer="Konami",
    year=1988,
    platform=Platform.ARCADE,
    rom_name="thunderx",
    orientation=Orientation.YOKO,
    difficulty_jp=7, goal_jp="1-ALL",
    clear_time_1all=15,
    versions=[
        GameVersion("thunderx", "Set 1"),
        GameVersion("thunderxj", "Japan"),
        GameVersion("thunderxa", "Set 2"),
        GameVersion("thunderxb", "Set 3"),
    ],
    notes="+11 for international (JP index)",
))

_add(Game(
    name="Thunder Cross II",
    developer="Konami",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="thndrx2",
    orientation=Orientation.YOKO,
    difficulty_jp=8, goal_jp="1-ALL",
))

_add(Game(
    name="Trigon",
    developer="Konami",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="trigon",
    orientation=Orientation.TATE,
    difficulty_jp=20, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="2-ALL=32 (JP index)",
))

_add(Game(
    name="A-Jax",
    developer="Konami",
    year=1987,
    platform=Platform.ARCADE,
    rom_name="ajax",
    orientation=Orientation.TATE,
    difficulty_jp=18, goal_jp="ALL",
))

_add(Game(
    name="TwinBee",
    developer="Konami",
    year=1985,
    platform=Platform.ARCADE,
    rom_name="twinbee",
    orientation=Orientation.TATE,
    difficulty_jp=13, goal_jp="1-ALL 5 stages",
    clear_time_1all=12,
    notes="ignoring power items (JP index)",
))

_add(Game(
    name="Detana!! TwinBee",
    developer="Konami",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="detatwin",
    orientation=Orientation.TATE,
    difficulty_jp=17, goal_jp="1-ALL",
    clear_time_1all=15,
    notes="2-ALL=44 (JP index)",
))

_add(Game(
    name="TwinBee Yahho!",
    developer="Konami",
    year=1995,
    platform=Platform.ARCADE,
    rom_name="tbyahhoo",
    orientation=Orientation.TATE,
    difficulty_jp=11, goal_jp="1-ALL",
))


# =============================================================================
# TAITO GAMES
# =============================================================================

_add(Game(
    name="Darius",
    developer="Taito",
    year=1986,
    platform=Platform.ARCADE,
    rom_name="darius",
    orientation=Orientation.YOKO,
    difficulty_jp=15, goal_jp="ALL",
    clear_time_1all=25,
    notes="+1 for EX (JP index)",
))

_add(Game(
    name="Darius II",
    developer="Taito",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="darius2",
    orientation=Orientation.YOKO,
    difficulty_jp=24, goal_jp="ALL",
    clear_time_1all=28,
    versions=[
        GameVersion("darius2", "World"),
        GameVersion("darius2d", "Dual Screen"),
        GameVersion("sagaia", "Sagaia"),
    ],
    aliases=["Sagaia"],
    notes="-10 with autofire (JP index)",
))

_add(Game(
    name="Darius Gaiden",
    developer="Taito",
    year=1994,
    platform=Platform.ARCADE,
    rom_name="dariusg",
    orientation=Orientation.YOKO,
    quality=5, difficulty_1cc=4, routing=Routing.MED,
    difficulty_jp=17, goal_jp="Survival route",
    clear_time_1all=25,
    versions=[
        GameVersion("dariusg", "World"),
        GameVersion("dariusgj", "Japan"),
        GameVersion("dariusgx", "Extra"),
    ],
    notes="-10 with autofire (JP index)",
))

_add(Game(
    name="G-Darius",
    developer="Taito",
    year=1997,
    platform=Platform.ARCADE,
    rom_name="gdarius",  # ZN-2 hardware
    orientation=Orientation.YOKO,
    requires_mame=True,
    quality=8, difficulty_1cc=5, routing=Routing.MED,
    difficulty_jp=14, goal_jp="zone U",
    clear_time_1all=24,
    notes="with autofire; Ver.2=19 (JP index)",
))

_add(Game(
    name="Darius Burst Another Chronicle",
    developer="Taito",
    year=2010,
    platform=Platform.ARCADE,
    rom_name="daborig",  # Taito Type X2 hardware
    orientation=Orientation.YOKO,
    requires_mame=True,
    quality=7, difficulty_1cc=2, routing=Routing.LOW,
    clear_time_1all=22,
    notes="Taito Type X2 hardware; EX version also available",
))

_add(Game(
    name="RayForce",
    developer="Taito",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="rayforce",
    orientation=Orientation.TATE,
    runahead_frames=2,
    difficulty_jp=23, goal_jp="ALL",
    clear_time_1all=22,
    versions=[
        GameVersion("rayforce", "World"),
        GameVersion("rayforcej", "Japan"),
        GameVersion("gunlock", "Gunlock Europe"),
    ],
    aliases=["Gunlock", "Layer Section"],
))

_add(Game(
    name="RayStorm",
    developer="Taito",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="raystorm",  # ZN-2 hardware
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=30, goal_jp="ALL",
))

_add(Game(
    name="RayCrisis",
    developer="Taito",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="raycrisis",  # ZN-2 hardware
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=16, goal_jp="ALL WR-03",
))

_add(Game(
    name="Metal Black",
    developer="Taito",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="metalb",
    orientation=Orientation.YOKO,
    runahead_frames=2,
    quality=7, difficulty_1cc=5, routing=Routing.HIGH,
    difficulty_jp=12, goal_jp="ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("metalb", "World"),
        GameVersion("metalbj", "Japan"),
    ],
    notes="-5 with autofire (JP index)",
))

_add(Game(
    name="Gun Frontier",
    developer="Taito",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="gunfront",
    orientation=Orientation.TATE,
    difficulty_jp=15, goal_jp="ALL",
    clear_time_1all=20,
    notes="with autofire (JP index)",
))

_add(Game(
    name="Gekirindan",
    developer="Taito",
    year=1995,
    platform=Platform.ARCADE,
    rom_name="gekiridn",
    orientation=Orientation.TATE,
    difficulty_jp=3, goal_jp="ALL 2P side",
    clear_time_1all=18,
    versions=[
        GameVersion("gekiridn", "World"),
        GameVersion("gekiridnj", "Japan"),
    ],
))


# =============================================================================
# CAPCOM GAMES
# =============================================================================

_add(Game(
    name="1941: Counter Attack",
    developer="Capcom",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="1941",
    orientation=Orientation.TATE,
    runahead_frames=3,
    difficulty_jp=10, goal_jp="ALL",
    clear_time_1all=18,
    versions=[
        GameVersion("1941", "World"),
        GameVersion("1941j", "Japan"),
        GameVersion("1941u", "USA"),
    ],
))

_add(Game(
    name="1942",
    developer="Capcom",
    year=1984,
    platform=Platform.ARCADE,
    rom_name="1942",
    orientation=Orientation.TATE,
))

_add(Game(
    name="1943",
    developer="Capcom",
    year=1987,
    platform=Platform.ARCADE,
    rom_name="1943",
    orientation=Orientation.TATE,
    difficulty_jp=27, goal_jp="vs Yamato",
    clear_time_1all=22,
    versions=[
        GameVersion("1943", "World"),
        GameVersion("1943j", "Japan"),
        GameVersion("1943u", "USA"),
        GameVersion("1943kai", "1943 Kai"),
    ],
    notes="-8 with autofire; Kai -5 for Shotgun (JP index)",
))

_add(Game(
    name="19XX: The War Against Destiny",
    developer="Capcom",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="19xx",
    orientation=Orientation.TATE,
    difficulty_jp=20, goal_jp="ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("19xx", "World"),
        GameVersion("19xxj", "Japan"),
        GameVersion("19xxu", "USA"),
    ],
))

_add(Game(
    name="Giga Wing",
    developer="Takumi",
    year=1999,
    platform=Platform.ARCADE,
    rom_name="gigawing",
    orientation=Orientation.YOKO,
    runahead_frames=3,
    quality=8, difficulty_1cc=9, routing=Routing.HIGH,
    difficulty_jp=18, goal_jp="true ending",
    clear_time_1all=15,
    versions=[
        GameVersion("gigawing", "USA"),
        GameVersion("gigawingj", "Japan"),
        GameVersion("gigawinga", "Asia"),
    ],
))

_add(Game(
    name="Giga Wing 2",
    developer="Takumi",
    year=2000,
    platform=Platform.ARCADE,
    rom_name="gigawing2",
    orientation=Orientation.YOKO,
    requires_mame=True,
    difficulty_jp=22, goal_jp="with TLB",
    clear_time_1all=18,
    notes="Naomi hardware",
))

_add(Game(
    name="Mars Matrix",
    developer="Takumi",
    year=2000,
    platform=Platform.ARCADE,
    rom_name="mmatrix",
    orientation=Orientation.TATE,
    runahead_frames=4,
    difficulty_jp=25, goal_jp="ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("mmatrix", "USA"),
        GameVersion("mmatrixj", "Japan"),
    ],
))

_add(Game(
    name="Area 88",
    developer="Capcom",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="unsquad",  # US parent; area88 is Japan clone
    orientation=Orientation.YOKO,
    difficulty_jp=12, goal_jp="ALL",
    clear_time_1all=15,
    versions=[
        GameVersion("unsquad", "U.N. Squadron World"),
        GameVersion("area88", "Japan"),
        GameVersion("area88r", "Japan Resale"),
    ],
    aliases=["U.N. Squadron"],
    notes="-5 with autofire (JP index)",
))

_add(Game(
    name="Carrier Air Wing",
    developer="Capcom",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="cawing",
    orientation=Orientation.YOKO,
    difficulty_jp=13, goal_jp="ALL",
    clear_time_1all=18,
    notes="-5 with autofire (JP index)",
))

_add(Game(
    name="Side Arms",
    developer="Capcom",
    year=1986,
    platform=Platform.ARCADE,
    rom_name="sidearms",
    orientation=Orientation.YOKO,
    difficulty_jp=12, goal_jp="ALL",
    clear_time_1all=18,
    notes="without autofire (JP index)",
))


# =============================================================================
# SNK / NEO GEO GAMES
# =============================================================================

_add(Game(
    name="Blazing Star",
    developer="Yumekobo",
    year=1998,
    platform=Platform.NEOGEO,
    rom_name="blazstar",
    orientation=Orientation.YOKO,
    runahead_frames=2,
    quality=8, difficulty_1cc=5, routing=Routing.MED,
    difficulty_jp=24, goal_jp="ALL",
    clear_time_1all=12,
    notes="-1 with autofire (JP index)",
))

_add(Game(
    name="Pulstar",
    developer="Aicom",
    year=1995,
    platform=Platform.NEOGEO,
    rom_name="pulstar",
    orientation=Orientation.YOKO,
))

_add(Game(
    name="Last Resort",
    developer="SNK",
    year=1992,
    platform=Platform.NEOGEO,
    rom_name="lresort",
    orientation=Orientation.YOKO,
    difficulty_jp=9, goal_jp="2-ALL",
    clear_time_1all=12,
    notes="with autofire (JP index)",
))

_add(Game(
    name="Prehistoric Isle 2",
    developer="Yumekobo",
    year=1999,
    platform=Platform.NEOGEO,
    rom_name="preisle2",
    orientation=Orientation.YOKO,
    difficulty_jp=4, goal_jp="ALL",
    clear_time_1all=10,
    notes="-1 with autofire (JP index)",
))

_add(Game(
    name="Twinkle Star Sprites",
    developer="ADK",
    year=1996,
    platform=Platform.NEOGEO,
    rom_name="twinspri",
    orientation=Orientation.TATE,
    difficulty_jp=5, goal_jp="ALL",
))


# =============================================================================
# NMK GAMES
# =============================================================================

_add(Game(
    name="Thunder Dragon",
    developer="NMK",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="tdragon",
    orientation=Orientation.TATE,
    difficulty_jp=31, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="-1 with autofire (JP index)",
))

_add(Game(
    name="Thunder Dragon 2",
    developer="NMK",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="tdragon2",
    orientation=Orientation.TATE,
    difficulty_jp=28, goal_jp="ALL 2P or 1P autofire",
    clear_time_1all=22,
    notes="+6 for 1P no autofire (JP index)",
))

_add(Game(
    name="P-47",
    developer="NMK",
    year=1988,
    platform=Platform.ARCADE,
    rom_name="p47",
    orientation=Orientation.YOKO,
    runahead_frames=2,
    difficulty_jp=32, goal_jp="1-ALL",
    clear_time_1all=22,
    notes="-5 with autofire (JP index)",
))

_add(Game(
    name="P-47 Aces",
    developer="NMK",
    year=1995,
    platform=Platform.ARCADE,
    rom_name="p47aces",
    orientation=Orientation.YOKO,
    difficulty_jp=39, goal_jp="ALL",
    clear_time_1all=25,
    notes="-2 with autofire (JP index)",
))

_add(Game(
    name="USAAF Mustang",
    developer="NMK",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="mustang",
    orientation=Orientation.TATE,
    difficulty_jp=33, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="-8 with autofire (JP index)",
))

_add(Game(
    name="Saint Dragon",
    developer="NMK",
    year=1989,
    platform=Platform.ARCADE,
    rom_name="stdragon",
    orientation=Orientation.YOKO,
    difficulty_jp=25, goal_jp="ALL",
))

_add(Game(
    name="Macross",
    developer="NMK",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="macross",
    orientation=Orientation.TATE,
    difficulty_jp=17, goal_jp="2-ALL",
    clear_time_1all=10,
    aliases=["Super Dimension Fortress Macross"],
    notes="1-ALL=8 (JP index)",
))


# =============================================================================
# VIDEO SYSTEM GAMES
# =============================================================================

_add(Game(
    name="Sonic Wings",
    developer="Video System",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="aerofgt",  # Parent; sonicwi is Japan clone
    orientation=Orientation.TATE,
    difficulty_jp=16, goal_jp="1-ALL",
    clear_time_1all=10,
    versions=[
        GameVersion("aerofgt", "World"),
        GameVersion("sonicwi", "Japan"),
        GameVersion("aerfboot", "Aero Fighters bootleg"),
    ],
    aliases=["Aero Fighters"],
    notes="2-ALL with AJ-37/IDS=27; +4 for F-18/FSX (JP index)",
))

_add(Game(
    name="Sonic Wings 2",
    developer="Video System",
    year=1994,
    platform=Platform.NEOGEO,
    rom_name="sonicwi2",
    orientation=Orientation.TATE,
    difficulty_jp=18, goal_jp="1-ALL",
))

_add(Game(
    name="Sonic Wings 3",
    developer="Video System",
    year=1995,
    platform=Platform.NEOGEO,
    rom_name="sonicwi3",
    orientation=Orientation.TATE,
    difficulty_jp=13, goal_jp="1-ALL P61",
    clear_time_1all=9,
    notes="2-ALL=21 (JP index)",
))

_add(Game(
    name="Air Gallet",
    developer="Gazelle",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="agallet",
    orientation=Orientation.TATE,
    difficulty_jp=19, goal_jp="ALL",
    clear_time_1all=12,
    versions=[
        GameVersion("agallet", "Europe"),
        GameVersion("agalletj", "Akuu Gallet Japan"),
        GameVersion("agalletu", "USA"),
    ],
    aliases=["Akuu Gallet"],
))


# =============================================================================
# VISCO GAMES
# =============================================================================

_add(Game(
    name="Vasara",
    developer="Visco",
    year=2000,
    platform=Platform.ARCADE,
    rom_name="vasara",
    orientation=Orientation.TATE,
    difficulty_jp=17, goal_jp="ALL",
))

_add(Game(
    name="Vasara 2",
    developer="Visco",
    year=2001,
    platform=Platform.ARCADE,
    rom_name="vasara2",
    orientation=Orientation.TATE,
    difficulty_jp=21, goal_jp="天の巻 1-ALL",
    clear_time_1all=14,
    notes="+3 with Takeda Nobukatsu; 天の巻 2-ALL=39 (JP index)",
))

_add(Game(
    name="Storm Blade",
    developer="Visco",
    year=1996,
    platform=Platform.ARCADE,
    rom_name="stmblade",
    orientation=Orientation.TATE,
    difficulty_jp=3, goal_jp="1-ALL",
    clear_time_1all=10,
    versions=[
        GameVersion("stmblade", "USA"),
        GameVersion("stmbladej", "Japan"),
    ],
))

_add(Game(
    name="Asuka & Asuka",
    developer="Visco",
    year=1988,
    platform=Platform.ARCADE,
    rom_name="asuka",
    orientation=Orientation.TATE,
    difficulty_jp=2, goal_jp="ALL",
))


# =============================================================================
# TECHNOSOFT GAMES
# =============================================================================

_add(Game(
    name="Thunder Force AC",
    developer="Technosoft",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="tfrceac",
    orientation=Orientation.YOKO,
    quality=6, difficulty_1cc=2, routing=Routing.LOW,
    clear_time_1all=22,
    versions=[
        GameVersion("tfrceac", "World"),
        GameVersion("tfrceacj", "Japan"),
    ],
    notes="Arcade version of Thunder Force III",
))


# =============================================================================
# OTHER DEVELOPERS
# =============================================================================

_add(Game(
    name="Radiant Silvergun",
    developer="Treasure",
    year=1998,
    platform=Platform.ARCADE,
    rom_name="rsgun",
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=22, goal_jp="Stage 2 route",
    clear_time_1all=35,
    notes="Stage 4 route=25; ST-V hardware",
))

_add(Game(
    name="Ikaruga",
    developer="Treasure",
    year=2001,
    platform=Platform.ARCADE,
    rom_name="ikaruga",
    orientation=Orientation.TATE,
    requires_mame=True,
    quality=7, difficulty_1cc=3, routing=Routing.LOW,
    difficulty_jp=13, goal_jp="Easy",
    clear_time_1all=22,
    notes="Normal=21, Hard=34; Naomi hardware",
))

_add(Game(
    name="Daioh",
    developer="Athena",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="daioh",
    orientation=Orientation.TATE,
    difficulty_jp=24, goal_jp="1-ALL",
    clear_time_1all=24,
    notes="2-ALL=36; -1 US version (JP index)",
))

_add(Game(
    name="Strike Gunner S.T.G",
    developer="Athena",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="stg",
    orientation=Orientation.TATE,
    difficulty_jp=27, goal_jp="ALL",
    clear_time_1all=25,
    notes="-5 with autofire (JP index)",
))

_add(Game(
    name="Zing Zing Zip",
    developer="Allumer",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="zingzip",
    orientation=Orientation.TATE,
    difficulty_jp=34, goal_jp="1-ALL",
    clear_time_1all=28,
    notes="as 1P; with autofire (JP index)",
))

_add(Game(
    name="Rezon",
    developer="Allumer",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="rezon",
    orientation=Orientation.YOKO,
    difficulty_jp=26, goal_jp="ALL",
))

_add(Game(
    name="War of Aero",
    developer="Allumer",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="wrofaero",
    orientation=Orientation.TATE,
    difficulty_jp=18, goal_jp="1-ALL",
    clear_time_1all=22,
    notes="2-ALL=24 (JP index)",
))

_add(Game(
    name="Nostradamus",
    developer="Face",
    year=1993,
    platform=Platform.ARCADE,
    rom_name="nost",
    orientation=Orientation.TATE,
    difficulty_jp=26, goal_jp="ALL",
    clear_time_1all=25,
    versions=[
        GameVersion("nost", "World"),
        GameVersion("nostj", "Japan"),
        GameVersion("nostk", "Korea"),
    ],
    notes="2P side; with autofire (JP index)",
))

_add(Game(
    name="Sand Scorpion",
    developer="Face",
    year=1992,
    platform=Platform.ARCADE,
    rom_name="sandscrp",
    orientation=Orientation.TATE,
    difficulty_jp=14, goal_jp="1-ALL",
    clear_time_1all=20,
    notes="with autofire (JP index)",
))

_add(Game(
    name="Night Raid",
    developer="Takumi",
    year=2001,
    platform=Platform.ARCADE,
    rom_name="nightrai",
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=1, goal_jp="upper left corner",
    clear_time_1all=15,
    notes="+22 without corner cheese; PS2 Arcade hardware",
))

_add(Game(
    name="Kyukyoku Tiger II",
    developer="Takumi",
    year=1995,
    platform=Platform.ARCADE,
    rom_name="ktiger2",
    orientation=Orientation.TATE,
    difficulty_jp=6, goal_jp="ALL 1P side",
    clear_time_1all=18,
    notes="+5 as 2P (JP index)",
))

_add(Game(
    name="Shienryu",
    developer="Warashi",
    year=1997,
    platform=Platform.ARCADE,
    rom_name="sngkstrk",
    orientation=Orientation.TATE,
    requires_mame=True,  # ST-V hardware, not in FBNeo
    difficulty_jp=25, goal_jp="1-ALL",
    clear_time_1all=24,
    versions=[
        GameVersion("sngkstrk", "Gekioh Japan"),
    ],
    aliases=["Gekioh"],
    notes="2-ALL=39 (JP index)",
))

_add(Game(
    name="Triggerheart Exelica",
    developer="Warashi",
    year=2006,
    platform=Platform.ARCADE,
    rom_name="trgheart",
    orientation=Orientation.TATE,
    requires_mame=True,
    quality=6, difficulty_1cc=6, routing=Routing.LOW,
    difficulty_jp=12, goal_jp="True Ending",
    clear_time_1all=22,
    notes="Naomi hardware",
))

_add(Game(
    name="Castle Shikigami",
    developer="Alfa System",
    year=2001,
    platform=Platform.ARCADE,
    rom_name="shikgam",
    orientation=Orientation.TATE,
    requires_mame=True,  # Taito Type X, not in FBNeo
    difficulty_jp=21, goal_jp="ALL",
    clear_time_1all=22,
    aliases=["Shikigami no Shiro"],
))

_add(Game(
    name="Castle Shikigami 2",
    developer="Alfa System",
    year=2003,
    platform=Platform.ARCADE,
    rom_name="shikgam2",
    orientation=Orientation.TATE,
    requires_mame=True,  # Taito Type X, not in FBNeo
    difficulty_jp=11, goal_jp="ALL Kim",
))

_add(Game(
    name="Castle Shikigami 3",
    developer="Alfa System",
    year=2006,
    platform=Platform.ARCADE,
    rom_name="shikgam3",
    orientation=Orientation.TATE,
    requires_mame=True,  # Not in FBNeo
    difficulty_jp=20, goal_jp="ALL Nagino",
))

_add(Game(
    name="Psyvariar",
    developer="Success",
    year=2000,
    platform=Platform.ARCADE,
    rom_name="psyvariar",
    orientation=Orientation.TATE,
    requires_mame=True,  # SH3 hardware, not in FBNeo
    difficulty_jp=19, goal_jp="X-A no TLB",
    clear_time_1all=10,
    aliases=["Psyvariar Revision"],
    notes="+12 with TLB (JP index)",
))

_add(Game(
    name="Psyvariar 2",
    developer="Success",
    year=2003,
    platform=Platform.ARCADE,
    rom_name="psyvar2",
    orientation=Orientation.TATE,
    requires_mame=True,  # SH3 hardware, not in FBNeo
    difficulty_jp=19, goal_jp="no TLB",
    clear_time_1all=12,
    notes="+13 with TLB (JP index)",
))

_add(Game(
    name="Under Defeat",
    developer="G.rev",
    year=2005,
    platform=Platform.ARCADE,
    rom_name="undefeat",
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=15, goal_jp="1-ALL",
    clear_time_1all=18,
    notes="2-ALL=23; Naomi hardware",
))

_add(Game(
    name="Border Down",
    developer="G.rev",
    year=2003,
    platform=Platform.ARCADE,
    rom_name="bdrdown",
    orientation=Orientation.YOKO,
    requires_mame=True,
    difficulty_jp=15, goal_jp="6A",
    clear_time_1all=20,
    notes="+3 for B/D; +2 for C; Naomi hardware",
))

_add(Game(
    name="Karous",
    developer="Milestone",
    year=2006,
    platform=Platform.ARCADE,
    rom_name="karous",
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=0, goal_jp="Easy",
    clear_time_1all=18,
    notes="Naomi hardware",
))

_add(Game(
    name="Radirgy",
    developer="Milestone",
    year=2005,
    platform=Platform.ARCADE,
    rom_name="radirgy",
    orientation=Orientation.TATE,
    requires_mame=True,
    difficulty_jp=20, goal_jp="Laser",
    clear_time_1all=20,
    notes="Naomi hardware",
))

_add(Game(
    name="E.D.F.",
    developer="Jaleco",
    year=1991,
    platform=Platform.ARCADE,
    rom_name="edf",
    orientation=Orientation.YOKO,
    difficulty_jp=23, goal_jp="ALL",
    clear_time_1all=24,
    aliases=["Earth Defense Force"],
))

_add(Game(
    name="Mazinger Z",
    developer="Banpresto",
    year=1994,
    platform=Platform.ARCADE,
    rom_name="mazinger",
    orientation=Orientation.TATE,
    difficulty_jp=9, goal_jp="1-ALL",
    clear_time_1all=20,
    versions=[
        GameVersion("mazinger", "World"),
        GameVersion("mazingerj", "Japan"),
    ],
    notes="2-ALL=24; -2 with autofire (JP index)",
))

_add(Game(
    name="Galaga '88",
    developer="Namco",
    year=1987,
    platform=Platform.ARCADE,
    rom_name="galaga88",
    orientation=Orientation.TATE,
    difficulty_jp=15, goal_jp="ALL",
))

_add(Game(
    name="Dragon Spirit",
    developer="Namco",
    year=1987,
    platform=Platform.ARCADE,
    rom_name="dspirit",
    orientation=Orientation.TATE,
    difficulty_jp=16, goal_jp="ALL",
    clear_time_1all=22,
    notes="-10 with autofire (JP index)",
))

_add(Game(
    name="Xevious",
    developer="Namco",
    year=1982,
    platform=Platform.ARCADE,
    rom_name="xevious",
    orientation=Orientation.TATE,
    difficulty_jp=12, goal_jp="1-ALL",
))

_add(Game(
    name="Dragon Saber",
    developer="Namco",
    year=1990,
    platform=Platform.ARCADE,
    rom_name="dsaber",
    orientation=Orientation.TATE,
    difficulty_jp=12, goal_jp="ALL",
))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_game(key: str) -> Game | None:
    """Get a game by ROM name or alias."""
    return GAMES.get(key.lower().replace(" ", "").replace("-", "").replace(":", ""))


def get_arcade_games() -> list[Game]:
    """Get all arcade games."""
    return [g for g in GAMES.values() if g.platform == Platform.ARCADE]


def get_games_by_developer(developer: str) -> list[Game]:
    """Get all games by a developer."""
    dev_lower = developer.lower()
    return [g for g in GAMES.values() if dev_lower in g.developer.lower()]


def get_vertical_games() -> list[Game]:
    """Get all vertical (TATE) games."""
    return [g for g in GAMES.values() if g.orientation == Orientation.TATE]


def get_games_sorted_by_difficulty(use_jp: bool = True) -> list[Game]:
    """Get games sorted by difficulty (hardest first)."""
    if use_jp:
        return sorted(
            [g for g in GAMES.values() if g.difficulty_jp is not None],
            key=lambda g: g.difficulty_jp or 0,
            reverse=True
        )
    else:
        return sorted(
            [g for g in GAMES.values() if g.difficulty_1cc is not None],
            key=lambda g: g.difficulty_1cc or 0,
            reverse=True
        )


# Deduplicate games dict (remove duplicate entries from aliases)
_seen = set()
_unique_games = {}
for key, game in GAMES.items():
    if id(game) not in _seen:
        _seen.add(id(game))
        _unique_games[game.rom_name if game.rom_name else key] = game
GAMES = _unique_games


if __name__ == "__main__":
    print(f"Total games in database: {len(GAMES)}")
    print(f"Arcade games: {len(get_arcade_games())}")
    print(f"Vertical (TATE) games: {len(get_vertical_games())}")
    print()

    # Show top 10 hardest (JP index)
    print("Top 10 Hardest (Japanese Index):")
    for i, g in enumerate(get_games_sorted_by_difficulty()[:10], 1):
        print(f"  {i:2}. {g.difficulty_jp:2} - {g.name} ({g.goal_jp})")
