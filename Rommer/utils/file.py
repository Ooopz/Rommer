import zlib
import hashlib
import zipfile

import py7zr
import rarfile


def is_zip(fp):
    return zipfile.is_zipfile(fp)


def is_rar(fp):
    return rarfile.is_rarfile(fp)


def is_7z(fp):
    try:
        with py7zr.SevenZipFile(fp, "r") as _:
            return True
    except py7zr.Bad7zFile:
        return False


def is_iso(fp):
    with open(fp, "rb") as f:
        data = f.read(0x8010)
        return data[-15:-10] == b"CD001"


def is_cso(fp):
    with open(fp, "rb") as f:
        return f.read(4) == b"CISO"


def is_chd(fp):
    with open(fp, "rb") as f:
        return f.read(8) == b"MComprHD"


def is_cue(fp):
    pass


def load_zip(fp):
    with zipfile.ZipFile(fp, "r") as z:
        file_list = z.namelist()
        if not file_list:
            return None
        file = file_list[0]
        with z.open(file) as f:
            content = f.read()
        return content


def load_rar(fp):
    with rarfile.RarFile(fp, "r") as r:
        file_list = r.namelist()
        if not file_list:
            return None
        file = file_list[0]
        with r.open(file) as f:
            content = f.read()
        return content


def load_7z(fp):
    with py7zr.SevenZipFile(fp, "r") as z:
        file_list = z.getnames()
        if not file_list:
            return None
        file = file_list[0]
        content = z.read()[file].read()
        return content


def load_bin(fp):
    with open(fp, "rb") as f:
        return f.read()


def calc_md5(data):
    return str(hashlib.md5(data).hexdigest()).upper()


def calc_sha1(data):
    return str(hashlib.sha1(data).hexdigest()).upper()


def calc_crc32(data):
    return f"{zlib.crc32(data)  & 0xFFFFFFFF:08X}"


def filter_mac_files(files):
    return [file for file in files if "__MACOSX" not in file]


def extract_zip(fp, dst, extend=None, assign=None):
    extend = [extend] if isinstance(extend, str) else extend
    assign = [assign] if isinstance(assign, str) else assign
    with zipfile.ZipFile(fp, "r") as z:
        if extend:
            names = z.namelist()
            filtered = filter_mac_files(names)
            filtered = [name for name in filtered for ext in extend if name.endswith(ext)]
            for file in filtered:
                z.extract(file, dst)
        elif assign:
            for file in assign:
                z.extract(file, dst)

        else:
            z.extractall(dst)


def extract_7z(fp, dst, extend=None):
    extend = [extend] if isinstance(extend, str) else extend
    with py7zr.SevenZipFile(fp, "r") as z:
        if extend:
            names = z.getnames()
            filtered = filter_mac_files(names)
            filtered = [name for name in filtered for ext in extend if name.endswith(ext)]
            for file in filtered:
                z.extract(file, dst)
        else:
            z.extractall(dst)
