from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import BinaryIO

from modules.runtime import get_base_path

ROMS_DIRECTORY = get_base_path() / "roms"



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
    handle.seek(0xA0)
    game_title = handle.read(12).decode("ascii").strip()
    game_code = handle.read(4).decode("ascii")
    handle.seek(0xBC)
    revision = int.from_bytes(handle.read(1), byteorder="little")
    game_name = game_title
    game_name += f" ({game_code[3]})"
    if revision > 0:
        game_name += f" (Rev {revision})"
    try:
        language = ROMLanguage(game_code[3])
    except ValueError:
        language = ROMLanguage.English

    return ROM(file, game_name, game_title, game_code[:3], language, revision)


def _load_gb_rom(file: Path, handle: BinaryIO) -> ROM:
    handle.seek(0x134)
    game_title = handle.read(11).rstrip(b"\x00").decode("ascii").strip()
    maker_code = handle.read(4).decode("ascii")
    game_name = game_title
    revision = 0
    language = ROMLanguage.English
    return ROM(file, game_name, game_title, "GBCR", language, revision)


def load_rom_data(file: Path) -> ROM:
    global rom_cache
    if str(file) in rom_cache:
        return rom_cache[str(file)]
    with open(file, "rb") as handle:
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