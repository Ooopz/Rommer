import os
import re
import sys
import shutil

from fuzzywuzzy import process

from .n64 import N64ByteSwapper
from ..utils import file as fh
from .parse_meta import DAT, RDB, SQLite
from ..utils.spider import download_libretro_boxart
from ..utils.constants import ConsoleType

import pandas as pd


class RomSet:
    def __init__(self, console_type: ConsoleType):
        self.metas = {}
        self.roms = {}
        self.console_type = console_type

    def add_metas(self, meta_path):
        if meta_path.endswith(".rdb"):
            self.metas = RDB(meta_path).parsed_data
        elif meta_path.endswith(".dat"):
            self.metas = DAT(meta_path).parsed_data
        elif meta_path.endswith(".sqlite"):
            meta = SQLite(meta_path)  # allredy have console_type
            for g in meta.parsed_data:
                if g["console_type"] == self.console_type:
                    self.metas[g["name"]] = g
        print(f"Added {len(self.metas)} metadata.")

    def add_rom(self, rom_path):
        SmartRom = getattr(sys.modules[__name__], self.console_type.name, BaseRom)
        r = SmartRom(rom_path, self.console_type)
        self.roms[r.name] = r

    def add_roms(self, folder_paths, valid_extensions):
        for r, _, f in os.walk(folder_paths):
            for file in f:
                if file.split(".")[-1] in valid_extensions:
                    self.add_rom(os.path.join(r, file))
        print(f"Added {len(self.roms)} roms.")

    def set_meta_for_roms(self, meta_path):
        count = 0
        meta_dict = pd.read_csv(meta_path).set_index("rom_name").to_dict("index")

        for name, meta in meta_dict.items():
            rom = self.roms.get(name)
            if rom:
                rom.meta.update(meta)
                if "alt_name" in meta:
                    rom.alt_name = meta["alt_name"]
                count += 1

        print(f"Set meta for {count} roms.")

    def hash_match(self, rom, meta):
        return any(
            [
                rom.sha1 == meta.get("sha1", " "),
                rom.md5 == meta.get("md5", " "),
                rom.crc32 == meta.get("crc32", " "),
            ]
        )

    def serial_match(self, rom, meta):
        return rom.serial == meta.get("serial", " ")

    def name_match(self, rom, meta):
        return any(
            [
                rom.name == meta.get("name", " "),
                rom.std_name == meta.get("name", " "),
                rom.alt_name == meta.get("name", " "),
                rom.name == meta.get("rom_name", " "),
            ]
        )

    def fuzzy_match(self, rom, dsts):
        for name in [rom.name, rom.std_name, rom.alt_name]:
            if name is not None:
                name, score = process.extractOne(name, dsts)
                if score > 95:
                    return "fuzzy", name
        return False, " "

    def match_by_type(self, rom, meta):
        if self.hash_match(rom, meta):
            return "hash"
        elif self.serial_match(rom, meta):
            return "serial"
        elif self.name_match(rom, meta):
            return "name"
        return False

    def match(self, use_hash=False, use_serial=False):
        if not self.roms or not self.metas:
            print("No roms or metadata added.")
            return

        success = 0
        meta_names = [meta["name"] for meta in self.metas.values()]

        for i, rom in enumerate(self.roms):
            if use_hash:
                self.roms[rom].get_hash()
            if use_serial:
                self.roms[rom].get_serial()

            for meta in self.metas.values():
                match_type = self.match_by_type(self.roms[rom], meta)
                if match_type:
                    _temp_meta = meta
                    break
            else:
                match_type, name = self.fuzzy_match(self.roms[rom], meta_names)
                if match_type:
                    _temp_meta = self.metas[name]

            if match_type:
                self.roms[rom].meta = _temp_meta
                self.roms[rom].std_name = _temp_meta["name"]
                success += 1

                print(f"#{i+1} [Success] {rom} matche meta by {match_type} with {_temp_meta['name']}.")
            else:
                print(f"#{i+1} [Failed ] {rom} matche failed.")

        print(f"Matched {success} / {len(self.roms)} roms.")

    def gen_rom_info(self, save_path):
        infos = []
        for rom in self.roms.values():
            info = {}
            info["name"] = rom.name
            info["std_name"] = rom.std_name
            info["alt_name"] = rom.alt_name
            meta = rom.meta
            if meta is not None:
                for k, v in meta.items():
                    info[f"meta.{k}"] = v
            infos.append(info)
        pd.DataFrame(infos).to_csv(save_path, index=False)

    def filter_remove_meta(self, key, value):
        self.roms = {k: v for k, v in self.roms.items() if v.meta[key] != value}

    def filter_keep_meta(self, key, value):
        self.roms = {k: v for k, v in self.roms.items() if v.meta[key] == value}

    def filter_gt_meta(self, key, value):
        self.roms = {k: v for k, v in self.roms.items() if v.meta[key] > value}

    def filter_lt_meta(self, key, value):
        self.roms = {k: v for k, v in self.roms.items() if v.meta[key] < value}

    def filter_std_name(self):
        self.roms = {k: v for k, v in self.roms.items() if v.std_name is not None}

    def filter_alt_name(self):
        self.roms = {k: v for k, v in self.roms.items() if v.alt_name is not None}

    def gen_new_rom_set(self, out_path, use_std_name=False, use_alt_name=False):
        os.makedirs(out_path, exist_ok=True)
        for rom in self.roms.values():
            if use_std_name and rom.std_name is not None:
                name = rom.std_name
            elif use_alt_name and rom.alt_name is not None:
                name = rom.alt_name
            else:
                name = rom.name
            save_fp = os.path.join(out_path, name + "." + rom.extend)
            shutil.copy(rom.rom_path, save_fp)

    def dl_images(self, out_path, use_std_name=False, use_alt_name=False):
        os.makedirs(out_path, exist_ok=True)
        for rom in self.roms.values():
            if rom.meta is not None:
                if use_std_name and rom.std_name is not None:
                    name = rom.std_name
                elif use_alt_name and rom.alt_name is not None:
                    name = rom.alt_name
                else:
                    name = rom.name
                save_fp = os.path.join(out_path, name + ".png")

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

        self.rom_name = self.name
        self.std_name = None
        self.alt_name = None
        self.meta = None
        self.filetype = None
        self.sha1 = None
        self.md5 = None
        self.crc32 = None
        self.serial = None
        self.data = None

        self.init()

    def init(self):
        pass

    def __str__(self) -> str:
        return f"{self.ctype.name} Rom: {self.name}"

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

    def get_hash(self):
        if self.crc32 is None and self.md5 is None and self.sha1 is None:
            self.gen_hash()

    def gen_hash(self):
        if self.data is None:
            self.data = self.get_data()
        self.crc32 = fh.calc_crc32(self.data)
        self.md5 = fh.calc_md5(self.data)
        self.sha1 = fh.calc_sha1(self.data)

    def get_serial(self):
        if self.serial is None:
            self.gen_serial()

    def gen_serial(self):
        pass

    def clean_data(self):
        self.data = None


class GBC(BaseRom):
    def init(self):
        self.compatibility()

    def gen_serial(self):
        if self.data is None:
            self.data = self.get_data()
        self.serial = self.data[0x013F:0x0143].decode("utf-8")
        print(f"Serial for {self.name} is {self.serial}.")

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


class N64(BaseRom):
    def to_z64(self, rom_path: str, rom_type: str):
        base, file = os.path.split(rom_path)
        file, _ = os.path.splitext(file)
        output_path = os.path.join(base, f"{file}.{rom_type}")
        n64bs = N64ByteSwapper(rom_path)
        n64bs.save("z64", output_path)


class PS(BaseRom):
    def gen_serial(self):
        if self.data is None:
            self.data = self.get_data()

        regexp = b"[A-Z]{4}[_-][0-9]{3}[.][0-9]{2}|LSP[0-9]{5}[.][0-9]{3}"
        serial = re.search(regexp, self.data)
        if serial:
            serial = serial.group(0).decode("utf-8")
            serial = serial.replace("_", "").replace(".", "").replace("-", "")
            serial = serial[:4] + "-" + serial[4:]
            self.serial = serial
            print(f"Serial for {self.name} is {self.serial}.")
        else:
            print(f"Serial for {self.name} not found.")


class ARCADE(BaseRom):
    pass
