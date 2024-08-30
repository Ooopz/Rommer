import re
import csv

from ..utils.constants import RDB_TYPE_MAP, ConsoleType


class RDB:
    def __init__(self, rdb_fp):
        self.data = None
        self.maxlen = 0
        self.parsed_data = None
        self.expect_num = 0

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
        def to_int(data):
            return int.from_bytes(data, byteorder="big")

        def get_rom(p):
            rom_indicator = to_int(self.data[p : p + 1])
            if rom_indicator == 0xDE:
                content_len = to_int(self.data[p : p + 3]) - 0xDE0000
                p += 3
            else:
                content_len = rom_indicator - 0x80
                p += 1
            return p, content_len

        def get_str(p):
            str_indicator = to_int(self.data[p : p + 1])
            if str_indicator == 0xD9:  # two bytes length indicator
                next_len = to_int(self.data[p : p + 2]) - 0xD900
                p += 2
            elif str_indicator == 0xDA:  # three bytes length indicator
                next_len = to_int(self.data[p : p + 3]) - 0xDA0000
                p += 3
            else:  # one byte length indicator
                next_len = str_indicator - 0xA0
                p += 1
            content = self.data[p : p + next_len].decode("utf-8")
            p += next_len
            return p, content

        def get_int(p):
            int_indicator = to_int(self.data[p : p + 1])
            next_len = 2 ** (int_indicator - 0xCC)  # one byte length indicator
            p += 1
            content = to_int(self.data[p : p + next_len])
            p += next_len
            return p, content

        def get_bytes(p):
            bytes_indicator = to_int(self.data[p : p + 1])
            if bytes_indicator == 0xC4:  # two bytes length indicator
                next_len = to_int(self.data[p : p + 2]) - 0xC400
                p += 2
            content = self.data[p : p + next_len]
            p += next_len
            if key == "serial":
                try:
                    content = content.decode("utf-8")
                except UnicodeDecodeError:
                    content = content.hex().upper()
            else:
                content = content.hex().upper()
            return p, content

        p = 16
        res = []

        while p < self.maxlen - 16:
            rom = {}
            p, content_len = get_rom(p)
            for _ in range(content_len):
                p, key = get_str(p)
                # get value
                if RDB_TYPE_MAP[key] is str:
                    p, content = get_str(p)
                elif RDB_TYPE_MAP[key] is int:
                    p, content = get_int(p)
                elif RDB_TYPE_MAP[key] is bytes:
                    p, content = get_bytes(p)
                rom[key] = content
            res.append(rom)

        # get count num
        count_index = self.data.find(b"count", p, self.maxlen)
        if self.maxlen - count_index > 5:
            p = count_index + 5
            _, self.expect_num = get_int(p)

        # filter useless data
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
