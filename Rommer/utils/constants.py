from enum import Enum


def invert_dict(d):
    inverted_dict = {}
    for k, v in d.items():
        if v in inverted_dict:
            if isinstance(inverted_dict[v], list):
                inverted_dict[v].append(k)
            else:
                inverted_dict[v] = [inverted_dict[v], k]
        else:
            inverted_dict[v] = k
    return inverted_dict


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
    # Arcade
    ARCADE = "ARCADE"

    # Nintendo
    GW = "GW"
    PM = "PM"
    GB = "GB"
    GBC = "GBC"
    GBA = "GBA"
    NDS = "NDS"
    _3DS = "3DS"
    FDS = "FDS"
    NES = "NES"
    SNES = "SNES"
    N64 = "N64"
    GC = "GC"
    WII = "WII"
    WIIU = "WIIU"

    # Sony
    PS = "PS"
    PS2 = "PS2"
    PSP = "PSP"
    PSV = "PSV"

    # Sega
    SG1K = "SG1K"
    MS = "MS"
    MD = "MD"
    _32X = "32X"
    MDCD = "MDCD"
    SS = "SS"
    DC = "DC"
    GG = "GG"

    # SNK
    NGCD = "NGCD"
    NGP = "NGP"
    NGPC = "NGPC"

    # Microsoft
    MSX = "MSX"
    MSX2 = "MSX2"
    XBOX = "XBOX"

    # Atari
    A26 = "A26"
    A52 = "A52"
    A78 = "A78"
    JAG = "JAG"
    JAGCD = "JAGCD"
    LYNX = "LYNX"

    # Bandai
    WS = "WS"
    WSC = "WSC"

    # NEC
    PCE = "PCE"
    PCECD = "PCECD"
    PCFX = "PCFX"
    SGFX = "SGFX"

    # 3DO
    _3DO = "3DO"

    OTHER = "OTHER"


class Region(Enum):
    C = "C"
    J = "J"
    K = "K"
    U = "U"
    E = "E"
    W = "W"
    O = "O"


class Language(Enum):
    CHS = "CHS"
    CHT = "CHT"
    EN = "EN"
    JP = "JP"
    OTH = "OTH"


RDB_CONSOLE_MAP = {
    # Arcade
    "FBNeo - Arcade Games": ConsoleType.ARCADE,
    # Nintendo
    "Handheld Electronic Game": ConsoleType.GW,
    "Nintendo - Pokemon Mini": ConsoleType.PM,
    "Nintendo - Game Boy": ConsoleType.GB,
    "Nintendo - Game Boy Color": ConsoleType.GBC,
    "Nintendo - Game Boy Advance": ConsoleType.GBA,
    "Nintendo - Nintendo DS": ConsoleType.NDS,
    "Nintendo - Nintendo 3DS": ConsoleType._3DS,
    "Nintendo - Family Computer Disk System": ConsoleType.FDS,  # gen 3
    "Nintendo - Nintendo Entertainment System": ConsoleType.NES,  # gen 3
    "Nintendo - Super Nintendo Entertainment System": ConsoleType.SNES,  # gen 4
    "Nintendo - Nintendo 64": ConsoleType.N64,  # gen 5
    "Nintendo - GameCube": ConsoleType.GC,  # gen 6
    "Nintendo - Wii": ConsoleType.WII,  # gen 7
    "Nintendo - Nintendo Wii U": ConsoleType.WIIU,  # gen 8
    # Sony
    "Sony - PlayStation": ConsoleType.PS,  # gen 5
    "Sony - PlayStation 2": ConsoleType.PS2,  # gen 6
    "Sony - PlayStation Portable": ConsoleType.PSP,
    "Sony - PlayStation Vita": ConsoleType.PSV,
    # Sega
    "Sega - SG-1000": ConsoleType.SG1K,
    "Sega - Master System - Mark III": ConsoleType.MS,
    "Sega - Mega Drive - Genesis": ConsoleType.MD,  # gen 4
    "Sega - Mega-CD - Sega CD": ConsoleType.MDCD,
    "Sega - 32X": ConsoleType._32X,
    "Sega - Saturn": ConsoleType.SS,  # gen 5
    "Sega - Dreamcast": ConsoleType.DC,  # gen 6
    "Sega - Game Gear": ConsoleType.GG,
    # Bandai
    "Bandai - WonderSwan": ConsoleType.WS,
    "Bandai - WonderSwan Color": ConsoleType.WSC,
    # Microsoft
    "Microsoft - MSX": ConsoleType.MSX,
    "Microsoft - MSX2": ConsoleType.MSX2,
    "Microsoft - Xbox": ConsoleType.XBOX,  # gen 6
    # Atari
    "Atari - 2600": ConsoleType.A26,
    "Atari - 5200": ConsoleType.A52,
    "Atari - 7800": ConsoleType.A78,
    "Atari - Lynx": ConsoleType.LYNX,
    "Atari - Jaguar": ConsoleType.JAG,
    # NEC
    "NEC - PC Engine - TurboGrafx 16": ConsoleType.PCE,
    "NEC - PC Engine CD - TurboGrafx-CD": ConsoleType.PCECD,
    "NEC - PC-FX": ConsoleType.PCFX,
    "NEC - PC Engine SuperGrafx": ConsoleType.SGFX,
    # SNK
    "SNK - Neo Geo CD": ConsoleType.NGCD,
    "SNK - Neo Geo Pocket": ConsoleType.NGP,
    "SNK - Neo Geo Pocket Color": ConsoleType.NGPC,
}

INVERT_RDB_CONSOLE_MAP = invert_dict(RDB_CONSOLE_MAP)

OPENVGDB_CONSOLE_MAP = {
    # Arcade
    "Arcade": ConsoleType.ARCADE,
    # Nintendo
    "Nintendo Game Boy": ConsoleType.GB,
    "Nintendo Game Boy Color": ConsoleType.GBC,
    "Nintendo Game Boy Advance": ConsoleType.GBA,
    "Nintendo DS": ConsoleType.NDS,
    "Nintendo Entertainment System": ConsoleType.NES,
    "Nintendo Famicom Disk System": ConsoleType.FDS,
    "Nintendo Super Nintendo Entertainment System": ConsoleType.SNES,
    "Nintendo 64": ConsoleType.N64,
    "Nintendo GameCube": ConsoleType.GC,
    "Nintendo Wii": ConsoleType.WII,
    "Nintendo Virtual Boy": ConsoleType.OTHER,
    # Sony
    "Sony PlayStation": ConsoleType.PS,
    "Sony PlayStation Portable": ConsoleType.PSP,
    # Sega
    "Sega SG-1000": ConsoleType.SG1K,
    "Sega Master System": ConsoleType.MS,
    "Sega Genesis/Mega Drive": ConsoleType.MD,
    "Sega 32X": ConsoleType._32X,
    "Sega CD/Mega-CD": ConsoleType.MDCD,
    "Sega Saturn": ConsoleType.SS,
    "Sega Game Gear": ConsoleType.GG,
    # Bandai
    "Bandai WonderSwan": ConsoleType.WS,
    "Bandai WonderSwan Color": ConsoleType.WSC,
    # Microsoft
    "Microsoft MSX": ConsoleType.MSX,
    "Microsoft MSX2": ConsoleType.MSX2,
    # Atari
    "Atari 2600": ConsoleType.A26,
    "Atari 5200": ConsoleType.A52,
    "Atari 7800": ConsoleType.A78,
    "Atari Lynx": ConsoleType.LYNX,
    "Atari Jaguar": ConsoleType.JAG,
    "Atari Jaguar CD": ConsoleType.JAGCD,
    # NEC
    "NEC PC Engine/TurboGrafx-16": ConsoleType.PCE,
    "NEC PC Engine CD/TurboGrafx-CD": ConsoleType.PCECD,
    "NEC PC-FX": ConsoleType.PCFX,
    "NEC SuperGrafx": ConsoleType.SGFX,
    # SNK
    "SNK Neo Geo Pocket": ConsoleType.NGP,
    "SNK Neo Geo Pocket Color": ConsoleType.NGPC,
    # Other
    "3DO Interactive Multiplayer": ConsoleType._3DO,
    "Coleco ColecoVision": ConsoleType.OTHER,
    "GCE Vectrex": ConsoleType.OTHER,
    "Intellivision": ConsoleType.OTHER,
    "Magnavox Odyssey2": ConsoleType.OTHER,
    "Commodore 64": ConsoleType.OTHER,
}

INVERT_OPENVGDB_CONSOLE_MAP = invert_dict(OPENVGDB_CONSOLE_MAP)

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
