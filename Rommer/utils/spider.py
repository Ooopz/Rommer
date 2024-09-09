from functools import partial

import requests

from .constants import INVERT_RDB_CONSOLE_MAP


def download_bin_file(url, save_path):
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
    trans = str.maketrans("/\|<>:?*&", "_" * 9)
    return _str.translate(trans)


def download_libretro(url_template, name, console_type, save_path):
    console = INVERT_RDB_CONSOLE_MAP[console_type]
    if isinstance(console, list):
        for c in console:
            console_name = clean_str(c)
            url = url_template.format(console_name, name)
            if not download_bin_file(url, save_path):
                return False
    else:
        console_name = clean_str(console)
        url = url_template.format(console_name)
        return download_bin_file(url, save_path)


download_libretro_rdb = partial(
    download_libretro, "https://raw.githubusercontent.com/libretro/libretro-database/master/rdb/{}.rdb{}", ""
)


download_libretro_boxart = partial(
    download_libretro, "https://raw.githubusercontent.com/libretro-thumbnails/{}/master/Named_Boxarts/{}.png"
)


download_libretro_snap = partial(
    download_libretro, "https://raw.githubusercontent.com/libretro-thumbnails/{}/master/Named_Snaps/{}.png"
)


download_libretro_title = partial(
    download_libretro, "https://raw.githubusercontent.com/libretro-thumbnails/{}/master/Named_Titles/{}.png"
)


def download_openvgdb(save_path):
    url = "https://github.com/OpenVGDB/OpenVGDB/releases/download/v29.0/openvgdb.zip"
    return download_bin_file(url, save_path)
