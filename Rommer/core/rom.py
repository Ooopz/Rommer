import os
import sys
import shutil

import fuzzywuzzy

from ..utils import file as fh
from .parse_meta import DAT, RDB, SQLite, load_csv_pair
from ..utils.spider import download_libretro_boxart
from ..utils.constants import ConsoleType


class RomSet:
    def __init__(self, console_type: ConsoleType):
        self.metas = {}
        self.roms = {}
        self.console_type = console_type

    def add_metas(self, meta_path):
        if meta_path.endswith(".rdb"):
            meta = RDB(meta_path)
            for g in meta.parsed_data:
                g["console_type"] = self.console_type
                self.metas[g["name"]] = g
        elif meta_path.endswith(".dat"):
            meta = DAT(meta_path)
            for g in meta.parsed_data:
                g["console_type"] = self.console_type
                self.metas[g["name"]] = g
        elif meta_path.endswith(".sqlite"):
            meta = SQLite(meta_path)  # allredy have console_type
            for g in meta.parsed_data:
                if g["console_type"] == self.console_type:
                    self.metas[g["name"]] = g
        print(f"Added {len(self.metas)} metadata.")

    def add_rom(self, rom_path: str):
        SmartRom = getattr(sys.modules[__name__], self.console_type.name, BaseRom)
        r = SmartRom(rom_path, self.console_type)
        self.roms[r.name] = r

    def add_roms(self, folder_paths, valid_extensions):
        for r, _, f in os.walk(folder_paths):
            for file in f:
                if file.split(".")[-1] in valid_extensions:
                    self.add_rom(os.path.join(r, file))
        print(f"Added {len(self.roms)} roms.")

    def set_std_name_for_rom(self, namemap_path):
        name_map = load_csv_pair(namemap_path)
        count = 0
        for name, std_name in name_map.items():
            for rom_name, rom in self.roms.items():
                if name == rom.name or name == rom.std_name or name == rom.alt_name:
                    self.roms[rom_name].std_name = std_name
                    count += 1
                    break
        print(f"Set {count} std names.")

    def set_alt_name_for_rom(self, namemap_path):
        count = 0
        name_map = load_csv_pair(namemap_path)
        for name, alt_name in name_map.items():
            for rom_name, rom in self.roms.items():
                if name == rom.name or name == rom.std_name or name == rom.alt_name:
                    self.roms[rom_name].alt_name = alt_name
                    count += 1
                    break
        print(f"Set {count} alt names.")

    def exact_match(self, rom, meta):
        return any(
            [
                rom.sha1 == meta.get("sha1", " "),
                rom.md5 == meta.get("md5", " "),
                rom.crc32 == meta.get("crc32", " "),
                rom.serial == meta.get("serial", " "),
                rom.name == meta.get("name", " "),
                rom.std_name == meta.get("name", " "),
                rom.alt_name == meta.get("name", " "),
                rom.name == meta.get("rom_name", " "),
            ]
        )

    def fuzzy_match(self, rom, metas):
        matched, score = fuzzywuzzy.process.extractOne(rom.name, metas)
        if score > 95:
            return matched
        

    def match(self):
        if len(self.roms) == 0:
            print("No roms.")
            return
        if len(self.metas) == 0:
            print("No metadata.")
            return
        success = 0
        self.match_success_list = []
        self.match_failed_list = []
        meta_names = [meta["name"] for meta in self.metas.values()]
        for rom in self.roms:
            for meta in self.metas.values():
                if self.exact_match(self.roms[rom], meta):
                    self.roms[rom].set_meta(meta)
                    success += 1
                    self.match_success_list.append(rom)
                    break
            else:
                matched = self.fuzzy_match(self.roms[rom], meta_names)
                if matched:
                    self.roms[rom].set_meta(self.metas[matched])
                    success += 1
                    self.match_success_list.append(rom)
                else:
                    self.match_failed_list.append(rom)

        print(f"Matched {success} / {len(self.roms)} roms.")

    def filter_std_name(self):
        self.roms = {k: v for k, v in self.roms.items() if v.std_name is not None}

    def filter_alt_name(self):
        self.roms = {k: v for k, v in self.roms.items() if v.alt_name is not None}

    def gen_new_rom_set(self, out_dir, use_std_name=False, use_alt_name=False):
        os.makedirs(out_dir, exist_ok=True)
        for rom in self.roms.values():
            if rom.meta is not None:
                if use_std_name and rom.std_name is not None:
                    name = rom.std_name
                elif use_alt_name and rom.alt_name is not None:
                    name = rom.alt_name
                else:
                    name = rom.name
                save_fp = os.path.join(out_dir, name + "." + rom.extend)
                shutil.copy(rom.rom_path, save_fp)

    def dl_images(self, out_dir, use_std_name=False, use_alt_name=False):
        os.makedirs(out_dir, exist_ok=True)
        for rom in self.roms.values():
            if rom.meta is not None:
                if use_std_name and rom.std_name is not None:
                    name = rom.std_name
                elif use_alt_name and rom.alt_name is not None:
                    name = rom.alt_name
                else:
                    name = rom.name
                save_fp = os.path.join(out_dir, name + ".png")

                rom_name = ".".join(rom.meta["rom_name"].split(".")[:-1])
                if download_libretro_boxart(rom_name, self.console_type, save_fp):  # noqa: SIM114
                    pass
                elif download_libretro_boxart(rom.meta["name"], self.console_type, save_fp):  # noqa: SIM114
                    pass
                elif download_libretro_boxart(rom.name, self.console_type, save_fp):
                    pass


class BaseRom:
    def __init__(self, rom_path, ctype):
        self.rom_path = rom_path
        self.ctype = ctype
        self.name = ".".join(os.path.basename(rom_path).split(".")[:-1])
        self.extend = os.path.basename(rom_path).split(".")[-1]
        self.serial = None

        self.std_name = None
        self.alt_name = None
        self.meta = None
        self.filetype = None

        self.init()
        self.calc_hash()

    def init(self):
        pass

    def __str__(self) -> str:
        return f"{self.ctype.name} Rom: {self.name}"

    def set_meta(self, meta):
        self.meta = meta

    def get_data(self):
        if fh.is_zip(self.rom_path):
            data = fh.load_zip(self.rom_path)
        elif fh.is_rar(self.rom_path):
            data = fh.load_rar(self.rom_path)
        elif fh.is_7z(self.rom_path):
            data = fh.load_7z(self.rom_path)
        else:
            data = fh.load_bin(self.rom_path)
        return data

    def calc_hash(self):
        data = self.get_data()
        self.crc32 = fh.calc_crc32(data)
        self.md5 = fh.calc_md5(data)
        self.sha1 = fh.calc_sha1(data)

        print(f"Hash for {self.name} calculated.")

    def get_serial(self):
        pass

    def set_alt_name(self, alt_name):
        self.alt_name = alt_name


class GBC(BaseRom):
    def init(self):
        self.compatibility()

    def get_serial(self):
        data = self.get_data()
        return data[0x013F:0x0143].decode("utf-8")

    def compatibility(self):
        data = self.get_data()
        if data[0x0143] == 0xC0:
            self.is_gb = False
            self.is_gbc = True
        elif data[0x0143] == 0x80:
            self.is_gb = True
            self.is_gbc = True
        else:
            self.is_gb = True
            self.is_gbc = False
        self.is_sgb = data[0x0146] == 0x03


class PS(BaseRom):
    def get_serial(self):
        pass
