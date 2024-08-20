import os
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor

from . import file_handler as fh
from .parse_meta import RDB, read_2col_csv_to_dict
from ..utils.spider import download_boxart
from ..utils.constants import ConsoleType


class RomSet:
    def __init__(self, console_type: ConsoleType):
        self.metas = {}
        self.roms = {}
        self.console_type = console_type
        self.enhanced = False

    def add_metas(self, rdb_path):
        if not self.enhanced:
            rdb = RDB(rdb_path)
            for g in rdb.parsed_data:
                g["console_type"] = self.console_type
                self.metas[g["name"]] = g
            # self.metas = {k: self.metas[k] for k in sorted(self.metas)}
            print(f"Added {len(self.rawmetas)} metadata.")
        else:
            print("Metadata already enhanced, can't add new metas.")

    def add_meta_alt_name(self, namemap_path):
        name = read_2col_csv_to_dict(namemap_path)
        for k, v in name.items():
            if self.metas.get(k, None) is not None:
                self.metas[k]["alt_name"] = v
            else:
                self.metas[k] = {"name": k, "alt_name": v}
        self.enhanced = True
        print(f"Enhanced {len(name)} metadata.")

    def add_rom(self, rom_path: str):
        SmartRom = getattr(sys.modules[__name__], self.console_type.name)
        r = SmartRom(rom_path)
        self.roms[r.name] = r

    def add_roms(self, folder_paths, valid_extensions):
        for r, _, f in os.walk(folder_paths):
            for file in f:
                if file.split(".")[-1] in valid_extensions:
                    self.add_rom(os.path.join(r, file))
        # self.roms = {k: self.roms[k] for k in sorted(self.roms)}
        print(f"Added {len(self.roms)} roms.")

    def match(self):
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

    def fill_alt_name(self):
        for rom in self.roms.values():
            if rom.meta is not None and rom.meta.get("alt_name", None) is not None:
                rom.alt_name = rom.meta["alt_name"]

    def filter_alt_name(self):
        self.roms = {k: v for k, v in self.roms.items() if v.alt_name is not None}

    def gen_new_rom_set(self, out_dir, use_alt_name=False):
        for rom in self.roms.values():
            if rom.meta is not None:
                os.makedirs(out_dir, exist_ok=True)
                name = rom.alt_name if use_alt_name and rom.alt_name is not None else rom.name
                shutil.copy(rom.rom_path, os.path.join(out_dir, name + "." + rom.extend))

    def dl_images(self, out_dir, use_alt_name=False):
        os.makedirs(out_dir, exist_ok=True)
        for rom in self.roms.values():
            if rom.meta is not None:
                name = rom.alt_name if use_alt_name and rom.alt_name is not None else rom.name
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
        self.calc_hash()
        self.init()

    def init(self):
        raise NotImplementedError

    def match_meta_basic(self, meta: dict):
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
        if fh.is_zip(self.rom_path):
            data = fh.load_zip(self.rom_path)
        elif fh.is_rar(self.rom_path):
            data = fh.load_rar(self.rom_path)
        elif fh.is_7z(self.rom_path):
            data = fh.load_7z(self.rom_path)
        else:
            data = fh.load_bin(self.rom_path)

        self.crc32 = fh.calc_crc32(data)
        self.md5 = fh.calc_md5(data)
        self.sha1 = fh.calc_sha1(data)

        print(f"Hash for {self.name} calculated.")


class PM(Rom):
    def match_meta(self, meta: dict):
        if self.match_meta_basic(meta):
            self.meta = meta
            return True

    def init(self):
        pass


class NES(Rom):
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
