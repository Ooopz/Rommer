class N64ByteSwapper:
    """z64 is proper format should to use for N64 roms."""

    def __init__(self, rom_path):
        self.rom_path = rom_path

        self.rom_formats_map = {
            b"\x40\x12\x37\x80": "n64",  # Little Endian
            b"\x80\x37\x12\x40": "z64",  # Big Endian
            b"\x37\x80\x40\x12": "v64",  # Byteswapped
        }

        self.valid_type = ["n64", "z64", "v64"]

    def check_header(self):
        with open(self.rom_path, "rb") as rom:
            rom_header = rom.read(4)
            self.rom_format = self.rom_formats_map.get(rom_header)
        if not self.rom_format:
            raise ValueError("Not an N64 rom.")

    @classmethod
    def swap_bytes(self, b):
        b = bytearray(b)
        b[0::2], b[1::2] = b[1::2], b[0::2]
        return b

    @classmethod
    def reverse_bytes(self, b):  # Endian swap
        return b"".join(b[i : i + 4][::-1] for i in range(0, len(b), 4))

    def convert(self, convert_type: str):
        # checking
        assert convert_type.lower() in self.valid_type, f"Invalid type: {convert_type}"

        self.check_header()

        if self.rom_format == convert_type:
            print(f"Rom already in {convert_type} format.")
            return

        # convert
        with open(self.rom_path, "rb") as rom_file:
            if self.rom_format == "n64" and convert_type == "z64":
                for chunk in iter(lambda: rom_file.read(1024), b""):
                    yield self.reverse_bytes(chunk)
            elif self.rom_format == "n64" and convert_type == "v64":
                for chunk in iter(lambda: rom_file.read(1024), b""):
                    yield self.swap_bytes(self.reverse_bytes(chunk))

            elif self.rom_format == "z64" and convert_type == "n64":
                for chunk in iter(lambda: rom_file.read(1024), b""):
                    yield self.reverse_bytes(chunk)
            elif self.rom_format == "z64" and convert_type == "v64":
                for chunk in iter(lambda: rom_file.read(1024), b""):
                    yield self.swap_bytes(chunk)

            elif self.rom_format == "v64" and convert_type == "n64":
                for chunk in iter(lambda: rom_file.read(1024), b""):
                    yield self.reverse_bytes(self.swap_bytes(chunk))
            elif self.rom_format == "v64" and convert_type == "z64":
                for chunk in iter(lambda: rom_file.read(1024), b""):
                    yield self.swap_bytes(chunk)

    def save(self, convert_type: str, output_path: str):
        with open(output_path, "wb") as output_file:
            for chunk in self.convert(convert_type):
                output_file.write(chunk)
        print(f"Rom saved to {output_path}")
