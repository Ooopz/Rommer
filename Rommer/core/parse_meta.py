import csv
import configparser
import xml.etree.ElementTree as ET

from ..utils.constants import RDB_TYPE_MAP, OPENVGDB_CONSOLE_MAP


class RDB:
    """For Libretro RDB file
    https://github.com/libretro/libretro-database
    """

    def __init__(self, rdb_fp):
        self.data = None
        self.maxlen = 0
        self.parsed_data = {}
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
        self.parsed_data = {r["name"]: r for r in res if "name" in r}


class DAT:
    """For No-Intro and Redump DAT file
    https://no-intro.org
    http://redump.org
    """

    def __init__(self, dat_fp):
        self.parsed_data = {}
        self.header = {}

        self.dat_fp = dat_fp
        self.parse_dat()

    def parse_dat(self):
        tree = ET.parse(self.dat_fp)
        root = tree.getroot()

        # parse header
        _header = root.find("header")
        if _header is not None:
            for child in _header:
                self.header[child.tag] = child.text

        # parse games
        for game in root.findall("game"):
            meta = {}
            meta.update(game.attrib)
            for child in game:
                if child.tag == "rom":
                    child.attrib["rom_name"] = child.attrib.pop("name")
                    meta.update(child.attrib)
                else:
                    meta[child.tag] = child.text

            if "name" in meta:
                self.parsed_data[meta["name"]] = meta


class SQLite:
    """For OpenVGDB SQLite database
    https://github.com/OpenVGDB/OpenVGDB
    """

    def __init__(self, db_fp):
        self.db_fp = db_fp
        self.conn = None
        self.cursor = None
        self.parsed_data = {}

        self.connect()
        self.parse()

    def connect(self):
        import sqlite3

        self.conn = sqlite3.connect(self.db_fp)
        self.cursor = self.conn.cursor()

    def parse(self):
        sql = """
            SELECT 
                romExtensionlessFileName name,
                romFileName rom_name,
                romLanguage language,
                TEMPromRegion region,
                releaseDeveloper developer,
                releasePublisher publisher,
                releaseDescription description,
                releaseGenre genre,
                releaseDate year,
                romSize size,
                romSerial serial,
                romHashCRC crc,
                romHashMD5 md5,
                romHashSHA1 sha1,
                romDumpSource source,
                releaseCoverFront cover_url,
                TEMPsystemName console_type
            FROM ROMs a
            INNER JOIN (
                SELECT 
                    romID,
                    releaseCoverFront,
                    releaseDescription,
                    releaseDeveloper,
                    releasePublisher,
                    releaseGenre,
                    TEMPsystemName,
                    SUBSTR(releaseDate, -4) releaseDate,
                    releaseReferenceURL,
                    releaseReferenceImageURL
                FROM
                    RELEASES 
                GROUP BY romID
            ) b
            ON a.romID = b.romID
            """
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        columns = [name[0] for name in self.cursor.description]
        parsed_data = [dict(zip(columns, row)) for row in rows]
        for meta in parsed_data:
            meta["console_type"] = OPENVGDB_CONSOLE_MAP.get(meta["console_type"], None)
            if "name" in meta:
                self.parsed_data[meta["name"]] = meta


class MAME:
    """For MAME XML file
    https://github.com/mamedev/mame
    """

    def __init__(self, dat_fp):
        self.parsed_data = {}

        self.dat_fp = dat_fp
        self.parse_dat()

    def parse_dat(self):
        context = ET.iterparse(self.dat_fp, events=("start",))
        next(context)  # skip root
        meta = {}
        tags = ["description", "year", "manufacturer"]
        for _, elem in context:
            if elem.tag == "machine":
                self.parsed_data[meta["name"]] = meta
                meta = {}
                meta.update(elem.attrib)
            elif elem.tag in tags:
                meta[elem.tag] = elem.text

    def parse_ini_file(self, ini_fp, key):
        config = configparser.ConfigParser(allow_no_value=True, strict=False)
        config.read(ini_fp, encoding="utf-8")
        for section in config.sections():
            for name, _ in config.items(section):
                if name in self.parsed_data:
                    self.parsed_data[name][key] = section


def load_csv_pair(file_path):
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
