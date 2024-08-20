import re
import csv

from ..utils.constants import RDB_TYPE_MAP, ConsoleType


class RDB:
    def __init__(self, rdb_fp):
        self.data = None
        self.maxlen = 0
        self.parsed_data = None

        self.rdb_fp = rdb_fp
        self.load_rdb()
        self.parse_rdb()

    def load_rdb(self):
        with open(self.rdb_fp, "rb") as f:
            data = f.read()
        header = data[:7].decode("utf-8")
        assert header == "RARCHDB"
        self.data = data
        self.maxlen = len(self.data)

    def parse_rdb(self):
        p = 16
        res = []
        rom = {}
        while p < self.maxlen - 16:
            rom_indicator = int.from_bytes(self.data[p : p + 1], byteorder="big")
            if rom_indicator > 130 and rom_indicator < 160:  # normal rom sep indicator
                p += 1
                if rom:
                    res.append(rom)
                rom = {}
            if rom_indicator == 222:  # special 3 bytes length rom sep indicator
                p += 3
                if rom:
                    res.append(rom)
                rom = {}
            if rom_indicator == 130:  # useless byte between key and value
                p += 1

            key_len = int.from_bytes(self.data[p : p + 1], byteorder="big") - 160
            p += 1

            key = self.data[p : p + key_len].decode("utf-8")
            p += key_len

            if RDB_TYPE_MAP[key] is str:
                str_indicator = int.from_bytes(self.data[p : p + 1], byteorder="big")

                if str_indicator == 217:  # two bytes length indicator
                    next_len = int.from_bytes(self.data[p : p + 2], byteorder="big") - 55552
                    p += 2
                elif str_indicator == 218:  # three bytes length indicator
                    next_len = int.from_bytes(self.data[p : p + 3], byteorder="big") - 14286848
                    p += 3
                else:  # one byte length indicator
                    next_len = str_indicator - 160
                    p += 1

                content = self.data[p : p + next_len].decode("utf-8")
                p += next_len

            elif RDB_TYPE_MAP[key] is int:  # int 类型的 key 后是一位类型指示符加四位定长，然后是 int
                int_indicator = int.from_bytes(self.data[p : p + 1], byteorder="big")
                p += 1

                next_len = 2 ** (int_indicator - 204)
                content = int.from_bytes(self.data[p : p + next_len], byteorder="big")
                p += next_len

            elif RDB_TYPE_MAP[key] is bytes:  # bytes 类型的 key 后是一位类型指示符加一位长度指示符，然后是 bytes
                bytes_indicator = int.from_bytes(self.data[p : p + 1], byteorder="big")
                p += 1

                bytes_len_indicator = int.from_bytes(self.data[p : p + 1], byteorder="big")
                p += 1

                next_len = bytes_len_indicator
                content = self.data[p : p + next_len]
                p += next_len

                if key == "serial":
                    try:
                        content = content.decode("utf-8")
                    except UnicodeDecodeError:
                        content = content.hex().upper()
                else:
                    content = content.hex().upper()

            rom[key] = content

        self.parsed_data = [r for r in res if "name" in r]


class ParseDat:
    def __init__(self, dat_fp, console_type):
        self.dat_fp = dat_fp
        self.console_type = console_type
        self.get_regexp()
        self.load_dat()

        self.parsed_content = []

    def load_dat(self):
        with open(self.dat_fp, encoding="utf-8") as file:
            self.content = file.read()

    def get_regexp(self):
        if self.console_type == ConsoleType.GBA:
            self.get_regexp_gba()
        else:
            raise NotImplementedError

    def parse(self):
        matches = self.pattern.findall(self.content)
        for matche in matches:
            game = {}
            for key, value in zip(self.match_key, matche):
                game[key] = value
            self.parsed_content.append(game)

    def get_regexp_gba(self):
        self.pattern = re.compile(
            r"""game \s* \(
                     \s* name \s* "(?P<name>[^"]+)"
                     \s* description \s* "(?P<description>[^"]+)"
                     \s* serial \s* "(?P<serial>[^"]+)"
                     \s* rom \s* \(
                        \s* name \s* "(?P<rom_name>[^"]+)"
                        \s* size \s* (?P<size>\d+)
                        \s* crc \s* (?P<crc>[A-F0-9]+)
                        \s* md5 \s* (?P<md5>[A-F0-9]+)
                        \s* sha1 \s* (?P<sha1>[A-F0-9]+)
                        \s* serial \s* "(?P<rom_serial>[^"]+)"
                    \s* \)
                \s *\)""",
            re.VERBOSE,
        )
        self.match_key = ["name", "description", "serial", "rom_name", "size", "crc", "md5", "sha1", "rom_serial"]


def read_2col_csv_to_dict(file_path):
    result_dict = {}
    with open(file_path, encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        for i, row in enumerate(csv_reader):
            if i == 0:
                continue
            if len(row) >= 2:  # 确保每行至少有两列
                key = row[0]
                value = row[1]
                result_dict[key] = value
    return result_dict
