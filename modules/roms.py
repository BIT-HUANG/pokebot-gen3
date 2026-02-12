import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import BinaryIO

from modules.runtime import get_base_path

ROMS_DIRECTORY = get_base_path() / "roms"

# 移除 GBA_GAME_NAME_MAP（不再需要映射）
# 移除 GBA_ROMS 白名单（不再校验哈希）
# 移除 GB_ROMS 白名单（不再校验GB ROM）
CUSTOM_GBA_ROM_HASHES: set[str] | None = None  # 保留但不再使用


class ROMLanguage(Enum):
    English = "E"
    French = "F"
    German = "D"
    Italian = "I"
    Japanese = "J"
    Spanish = "S"

    def __str__(self):
        return self.value


@dataclass
class ROM:
    file: Path
    game_name: str
    game_title: str
    game_code: str
    language: ROMLanguage
    revision: int

    @property
    def short_game_name(self) -> str:
        return self.game_name

    @property
    def id(self) -> str:
        return f"{self.game_code}{self.language.value}{self.revision}"


class InvalidROMError(Exception):
    pass


rom_cache: dict[str, ROM] = {}


def list_available_roms(force_recheck: bool = False) -> list[ROM]:
    """
    扫描roms目录下所有文件，加载所有有效的GBA/GB ROM（移除所有校验），仅保留Gen3 ROM的筛选
    """
    global rom_cache

    if force_recheck:
        rom_cache.clear()

    if not ROMS_DIRECTORY.is_dir():
        raise RuntimeError(f"Directory {str(ROMS_DIRECTORY)} does not exist!")

    result = []
    for file in ROMS_DIRECTORY.iterdir():
        if file.is_file():
            try:
                rom = load_rom_data(file)
                result.append(rom)
            except InvalidROMError:
                pass
    return result


def _load_gba_rom(file: Path, handle: BinaryIO) -> ROM:
    # 完全移除哈希校验、自定义白名单校验逻辑
    # 直接读取ROM头部元数据
    handle.seek(0xA0)
    game_title = handle.read(12).decode("ascii").strip()  # 去除首尾空白符
    game_code = handle.read(4).decode("ascii")
    maker_code = handle.read(2).decode("ascii")

    handle.seek(0xBC)
    revision = int.from_bytes(handle.read(1), byteorder="little")

    # 直接使用游戏标题作为game_name，舍弃映射
    game_name = game_title
    # 保留原有版本号、语言码拼接逻辑（可选，也可删除）
    game_name += f" ({game_code[3]})"
    if revision > 0:
        game_name += f" (Rev {revision})"

    # 兼容语言码：若game_code[3]不在ROMLanguage中，默认设为English
    try:
        language = ROMLanguage(game_code[3])
    except ValueError:
        language = ROMLanguage.English

    return ROM(file, game_name, game_title, game_code[:3], language, revision)


def _load_gb_rom(file: Path, handle: BinaryIO) -> ROM:
    # 移除GB ROM哈希校验，直接读取元数据
    handle.seek(0x134)
    game_title = handle.read(11).rstrip(b"\x00").decode("ascii").strip()
    maker_code = handle.read(4).decode("ascii")

    # 固定设置GB ROM的默认值（无校验）
    game_name = game_title
    revision = 0
    language = ROMLanguage.English  # GB ROM默认设为英文（可按需调整）

    return ROM(file, game_name, game_title, "GBCR", language, revision)


def load_rom_data(file: Path) -> ROM:
    # 优先使用缓存
    global rom_cache
    if str(file) in rom_cache:
        return rom_cache[str(file)]

    with open(file, "rb") as handle:
        # 简化GBA/GB魔术数判断（可选：完全移除则所有文件都尝试加载）
        handle.seek(0xB2)
        gba_magic_number = handle.read(1)
        if gba_magic_number == b"\x96":
            rom_cache[str(file)] = _load_gba_rom(file, handle)
            return rom_cache[str(file)]

        handle.seek(0x104)
        gb_magic_string = handle.read(4)
        if gb_magic_string == b"\xce\xed\x66\x66":
            rom_cache[str(file)] = _load_gb_rom(file, handle)
            return rom_cache[str(file)]

    raise InvalidROMError(f"File `{file.name}` does not seem to be a valid ROM (magic number missing.)")