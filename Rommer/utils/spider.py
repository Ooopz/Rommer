import requests

from .constants import CONSOLE_NAME_MAP


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


def download_libretro_boxart(name, console_type, save_path):
    name = clean_str(name)
    console_name = clean_str(CONSOLE_NAME_MAP[console_type].replace(" ", "_"))
    url = f"https://raw.githubusercontent.com/libretro-thumbnails/{console_name}/master/Named_Boxarts/{name}.png"
    return download_bin_file(url, save_path)


def download_libretro_snap(name, console_type, save_path):
    name = clean_str(name)
    console_name = clean_str(CONSOLE_NAME_MAP[console_type].replace(" ", "_"))
    url = f"https://raw.githubusercontent.com/libretro-thumbnails/{console_name}/master/Named_Snaps/{name}.png"
    return download_bin_file(url, save_path)


def download_libretro_title(name, console_type, save_path):
    name = clean_str(name)
    console_name = clean_str(CONSOLE_NAME_MAP[console_type].replace(" ", "_"))
    url = f"https://raw.githubusercontent.com/libretro-thumbnails/{console_name}/master/Named_Titles/{name}.png"
    return download_bin_file(url, save_path)
