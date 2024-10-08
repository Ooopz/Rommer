import os
import shutil
from functools import partial

import requests

from .file import extract_zip
from .constants import INVERT_RDB_CONSOLE_MAP


def download_bin_file(url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    for i in range(3):
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(save_path, "wb") as file:
                file.write(response.content)
                print(f"Downloaded {url} to {save_path}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            print(f"Retrying {i+1}...")


def clean_str(_str: str):
    trans = str.maketrans(r"/\|<>:?*& ", "_" * 10)
    return _str.translate(trans)


def clean_name(_str: str):
    trans = str.maketrans(r"/\|<>:?*&", "_" * 9)
    return _str.translate(trans)


def download_libretro_rdb(console_type, save_path):
    console = INVERT_RDB_CONSOLE_MAP[console_type]
    url = f"https://raw.githubusercontent.com/libretro/libretro-database/master/rdb/{console}.rdb"
    return download_bin_file(url, save_path)


def download_libretro_img(url_template, name, console_type, save_path):
    console = INVERT_RDB_CONSOLE_MAP[console_type]
    console_name = clean_str(console)
    url = url_template.format(console_name, clean_name(name))
    return download_bin_file(url, save_path)


download_libretro_boxart = partial(
    download_libretro_img, "https://raw.githubusercontent.com/libretro-thumbnails/{}/master/Named_Boxarts/{}.png"
)


download_libretro_snap = partial(
    download_libretro_img, "https://raw.githubusercontent.com/libretro-thumbnails/{}/master/Named_Snaps/{}.png"
)


download_libretro_title = partial(
    download_libretro_img, "https://raw.githubusercontent.com/libretro-thumbnails/{}/master/Named_Titles/{}.png"
)


def download_openvgdb(save_path, version="v29.0"):
    url = f"https://github.com/OpenVGDB/OpenVGDB/releases/download/{version}/openvgdb.zip"
    return download_bin_file(url, save_path)


def download_mame(save_path, version="0269"):
    iver = int(version)
    urls = [
        (f"https://github.com/mamedev/mame/releases/download/mame{version}/mame{version}lx.zip", "mamelx.zip"),
        (f"https://www.progettosnaps.net/series/packs/pS_Series_{iver}.zip", "series.zip"),
        (f"https://www.progettosnaps.net/languages/packs/pS_Languages_{iver}.zip", "languages.zip"),
        (f"https://www.progettosnaps.net/catver/packs/pS_CatVer_{iver}.zip", "catver.zip"),
        (f"https://www.progettosnaps.net/renameset/packs/pS_version_{iver}.zip", "version.zip"),
    ]

    for url, name in urls:
        save_fp = os.path.join(save_path, name)
        download_bin_file(url, save_fp)


def download_redump(save_path):
    urls = [
        ("http://redump.org/datfile/psp/", "psp.zip"),
        ("http://redump.org/datfile/psx/", "psx.zip"),
        ("http://redump.org/datfile/ps2/", "ps2.zip"),
        ("http://redump.org/datfile/ss/", "ss.zip"),
        ("http://redump.org/datfile/dc/", "dc.zip"),
        ("http://redump.org/datfile/wii/", "wii.zip"),
        ("http://redump.org/datfile/gc/", "gc.zip"),
        ("http://redump.org/datfile/ngcd/", "ngcd.zip"),
        ("http://redump.org/datfile/ajcd/", "ajcd.zip"),
        ("http://redump.org/datfile/pce/", "pcecd.zip"),
        ("http://redump.org/datfile/pc-fx/", "pcfx.zip"),
        ("http://redump.org/datfile/mcd/", "mdcd.zip"),
    ]

    for url, name in urls:
        save_fp = os.path.join(save_path, name)
        download_bin_file(url, save_fp)


def download_wikipedia():
    pass


def prepare_meta(save_path, openvgdb_version="v29.0", mame_version="0269", overwrite=False):
    for console, name in INVERT_RDB_CONSOLE_MAP.items():
        dat_fp = os.path.join(save_path, "rdb", f"{name}.rdb")
        if overwrite or not os.path.exists(dat_fp):
            download_libretro_rdb(console, dat_fp)

    openvgdb_fp = os.path.join(save_path, "openvgdb", "openvgdb.zip")
    if overwrite or not os.path.exists(openvgdb_fp):
        download_openvgdb(openvgdb_fp, openvgdb_version)
    extract_zip(openvgdb_fp, os.path.join(save_path, "openvgdb"), "sqlite")

    mame_fp = os.path.join(save_path, "mame")
    if overwrite or not os.path.exists(os.path.join(mame_fp, "mamelx.zip")):
        download_mame(mame_fp, mame_version)
    extract_zip(os.path.join(mame_fp, "mamelx.zip"), os.path.join(save_path, "mame"), "xml")
    extract_zip(os.path.join(mame_fp, "series.zip"), os.path.join(save_path, "mame"), "ini")
    extract_zip(os.path.join(mame_fp, "languages.zip"), os.path.join(save_path, "mame"), "ini")
    extract_zip(os.path.join(mame_fp, "catver.zip"), os.path.join(save_path, "mame"), "ini")
    extract_zip(os.path.join(mame_fp, "version.zip"), os.path.join(save_path, "mame"), "ini")

    for r, _, f in os.walk(mame_fp):
        for file in f:
            shutil.move(os.path.join(r, file), os.path.join(mame_fp, file))

    redump_fp = os.path.join(save_path, "redump")
    if overwrite or not os.path.exists(redump_fp):
        download_redump(redump_fp)
