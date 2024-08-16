from Rommer.core.rom import RomSet
from Rommer.utils.constants import ConsoleType

romset = RomSet(ConsoleType.PM)
romset.add_meta(r"D:\Code\PlayLand\python\Rommer\data\rdb\Nintendo - Pokemon Mini.rdb")
romset.add_roms(r"D:\Code\PlayLand\python\Rommer\data\TestRomSet", ["zip","min"])
romset.enhance_meta(r"D:\Code\PlayLand\python\Rommer\data\name\Nintendo - Pokemon Mini.csv")
romset.match_meta()
romset.fill_cn_name()
romset.filter_cn_name()
romset.gen_new_rom_set(r"D:\Code\PlayLand\python\Rommer\data\TestRomSetCopy", use_cn_name=True)
romset.dl_images(r"D:\Code\PlayLand\python\Rommer\data\TestRomSetCopy\Imgs", use_cn_name=True)
