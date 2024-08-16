import os
import sys
import shutil
from copy import deepcopy

from .parse_meta import RDB, read_2col_csv_to_dict
from .file_handler import is_7z, is_rar, is_zip, load_7z, calc_md5, load_bin, load_rar, load_zip, calc_sha1, calc_crc32
from ..utils.spider import download_boxart
from ..utils.constants import ConsoleType


class RomSet:
    def __init__(self, console_type: ConsoleType):
        self.rawmetas = {}
        self.metas = {}
        self.roms = {}
        self.console_type = console_type
        self.enhanced = False

    def add_meta(self, rdb_path):
        rdb = RDB(rdb_path)
        for g in rdb.parsed_data:
            g["console_type"] = self.console_type
            self.rawmetas[g["name"]] = g
        self.metas = deepcopy(self.rawmetas)
        self.enhanced = False

    def enhance_meta(self, namemap_path):
        self.metas = deepcopy(self.rawmetas)
        name = read_2col_csv_to_dict(namemap_path)
        for k, v in name.items():
            if self.metas.get(k, None) is not None:
                self.metas[k]["cn_name"] = v
            else:
                self.metas[k] = {"name": k, "cn_name": v}
        self.enhanced = True

    def add_rom(self, rom_path: str):
        SmartRom = getattr(sys.modules[__name__], self.console_type.name)
        r = SmartRom(rom_path)
        self.roms[r.name] = r

    def add_roms(self, folder_paths, valid_extensions):
        for r, _, f in os.walk(folder_paths):
            for file in f:
                if file.split(".")[-1] in valid_extensions:
                    self.add_rom(os.path.join(r, file))

    def match_meta(self):
        if len(self.roms) == 0:
            print("No roms.")
            return
        if len(self.metas) == 0:
            print("No metadata.")
            return
        success = 0
        for rom in self.roms:
            for meta in self.metas.values():
                if self.roms[rom].match_meta(meta):
                    success += 1
                    break
        print(f"Matched {success} / {len(self.roms)} roms.")

    def filter_cn_name(self):
        self.roms = {k: v for k, v in self.roms.items() if v.cn_name is not None}

    def fill_cn_name(self):
        for rom in self.roms.values():
            if rom.meta is not None and rom.meta.get("cn_name", None) is not None:
                rom.cn_name = rom.meta["cn_name"]

    def gen_new_rom_set(self, out_dir, use_cn_name=False):
        for rom in self.roms.values():
            if rom.meta is not None:
                os.makedirs(out_dir, exist_ok=True)
                new_name = rom.cn_name if use_cn_name and rom.cn_name is not None else rom.name
                shutil.copy(rom.rom_path, os.path.join(out_dir, new_name + "." + rom.extend))

    def fill_en_name(self):
        for rom in self.roms.values():
            if rom.meta is not None and rom.meta.get("name", None) is not None:
                rom.en_name = rom.meta["name"]

    def dl_images(self, out_dir, use_cn_name=False):
        for rom in self.roms.values():
            if rom.meta is not None and rom.meta.get("name", None) is not None:
                os.makedirs(out_dir, exist_ok=True)
                name = rom.cn_name if use_cn_name and rom.cn_name is not None else rom.name
                saved_fp = os.path.join(out_dir, name + ".png")
                download_boxart(rom.meta["name"], self.console_type, saved_fp)


class Rom:
    def __init__(self, rom_path):
        self.rom_path = rom_path
        self.name = ".".join(os.path.basename(rom_path).split(".")[:-1])
        self.extend = os.path.basename(rom_path).split(".")[-1]
        self.alt_name = None
        self.std_name = None
        self.meta = None
        self.filetype = None
        self.init()

    def init(self):
        raise NotImplementedError

    def match_meta_basic(self, meta: dict):
        self.calc_hash()
        if self.sha1 == meta.get("sha1"):
            return True
        if self.md5 == meta.get("md5"):
            return True
        if self.crc32 == meta.get("crc32"):
            return True
        if self.name == meta.get("name"):
            return True

    def match_meta(self, meta: dict):
        raise NotImplementedError

    def set_alt_name(self, alt_name):
        self.alt_name = alt_name

    def calc_hash(self):
        if is_zip(self.rom_path):
            data = load_zip(self.rom_path)
        elif is_rar(self.rom_path):
            data = load_rar(self.rom_path)
        elif is_7z(self.rom_path):
            data = load_7z(self.rom_path)
        else:
            data = load_bin(self.rom_path)

        self.crc32 = calc_crc32(data)
        self.md5 = calc_md5(data)
        self.sha1 = calc_sha1(data)

        del data


class PM(Rom):
    def match_meta(self, meta: dict):
        if self.match_meta_basic(meta):
            self.meta = meta
            return True

    def init(self):
        pass


class Arcade(Rom):
    def init(self):
        pass

    def match_meta(self, meta: dict):
        if self.name == meta["rom_name"].split(".")[0]:
            self.meta = meta
            return True


class GBA(Rom):
    def init(self):
        self.type = ConsoleType.GBA

    def get_serial(self):
        return self.load_rom()[:12]
