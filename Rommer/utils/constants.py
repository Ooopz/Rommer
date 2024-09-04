from enum import Enum


class RomDataType(Enum):
    BIN = 1
    ZIP = 2
    RAR = 3
    _7Z = 4
    ISO = 5
    CSO = 6
    CUE = 7
    CHD = 8


class ConsoleType(Enum):
    GW = 0
    PM = 1
    GB = 2
    GBC = 3
    GBA = 4
    NDS = 5
    _3DS = 6
    NS = 7
    NES = 8
    SNES = 9
    N64 = 10
    GC = 11
    WII = 12
    WIIU = 13

    PS = 14
    PS2 = 15
    PSP = 16
    PSV = 17

    MD = 18
    SS = 19
    DC = 20
    GG = 21

    ARCADE = 22

    OTHER = 99


CONSOLE_NAME_MAP = {
    # Nintendo
    ConsoleType.GW: "Handheld Electronic Game",
    ConsoleType.PM: "Nintendo - Pokemon Mini",
    ConsoleType.GB: "Nintendo - Game Boy",
    ConsoleType.GBC: "Nintendo - Game Boy Color",
    ConsoleType.GBA: "Nintendo - Game Boy Advance",
    ConsoleType.NDS: "Nintendo - Nintendo DS",
    ConsoleType._3DS: "Nintendo - Nintendo 3DS",
    ConsoleType.NS: "Nintendo - Nintendo Switch",
    ConsoleType.NES: "Nintendo - Nintendo Entertainment System",  # gen 3
    ConsoleType.SNES: "Nintendo - Super Nintendo Entertainment System",  # gen 4
    ConsoleType.N64: "Nintendo - Nintendo 64",  # gen 5
    ConsoleType.GC: "Nintendo - Nintendo GameCube",  # gen 6
    ConsoleType.WII: "Nintendo - Nintendo Wii",  # gen 7
    ConsoleType.WIIU: "Nintendo - Nintendo Wii U",  # gen 8
    # Sony
    ConsoleType.PS: "Sony - Sony PlayStation",  # gen 5
    ConsoleType.PS2: "Sony - Sony PlayStation 2",  # gen 6
    ConsoleType.PSP: "Sony - Sony PlayStation Portable",
    ConsoleType.PSV: "Sony - Sony PlayStation Vita",
    # Sega
    ConsoleType.MD: "Sega - Mega Drive - Genesis",  # gen 4
    ConsoleType.SS: "Sega - Saturn",  # gen 5
    ConsoleType.DC: "Sega - Dreamcast",  # gen 6
    ConsoleType.GG: "Sega - Game Gear",
    # Arcade
}

RDB_TYPE_MAP = {
    "name": str,
    "description": str,
    "genre": str,
    "achievements": int,
    "category": str,
    "language": str,
    "region": str,
    "console_exclusive": int,
    "platform_exclusive": int,
    "score": str,
    "media": str,
    "controls": str,
    "artstyle": str,
    "gameplay": str,
    "narrative": str,
    "pacing": str,
    "perspective": str,
    "setting": str,
    "visual": str,
    "vehicular": str,
    "rom_name": str,
    "size": int,
    "users": int,
    "releasemonth": int,
    "releaseyear": int,
    "rumble": int,
    "analog": int,
    "famitsu_rating": int,
    "edge_rating": int,
    "edge_issue": int,
    "edge_review": str,
    "enhancement_hw": str,
    "barcode": str,
    "esrb_rating": str,
    "elspa_rating": str,
    "pegi_rating": str,
    "cero_rating": str,
    "franchise": str,
    "developer": str,
    "publisher": str,
    "origin": str,
    "coop": int,
    "tgdb_rating": int,
    "crc": bytes,
    "md5": bytes,
    "sha1": bytes,
    "serial": bytes,
}
