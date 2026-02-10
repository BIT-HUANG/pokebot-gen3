"""Contains default schemas for configuration files."""

from __future__ import annotations

from typing import Literal

from confz import BaseConfig
from pydantic import ConfigDict, Field
from pydantic.types import Annotated, ClassVar, NonNegativeInt, PositiveInt



class Cheats(BaseConfig):
    """Schema for the cheat configuration."""

    filename: ClassVar = "cheats.yml"
    random_soft_reset_rng: bool = False
    faster_pickup: bool = False



class Keys(BaseConfig):
    """Schema for GBA key configuration."""

    filename: ClassVar = "keys.yml"
    gba: KeysGBA = Field(default_factory=lambda: KeysGBA())
    emulator: KeysEmulator = Field(default_factory=lambda: KeysEmulator())


class KeysEmulator(BaseConfig):
    """Schema for the emulator keys section in the Keys config."""

    zoom_in: str = "plus"
    zoom_out: str = "minus"
    toggle_manual: str = "Tab"
    toggle_video: str = "v"
    toggle_audio: str = "b"
    set_speed_1x: str = "1"
    set_speed_2x: str = "2"
    set_speed_3x: str = "3"
    set_speed_4x: str = "4"
    set_speed_8x: str = "5"
    set_speed_16x: str = "6"
    set_speed_32x: str = "7"
    set_speed_unthrottled: str = "0"
    reset: str = "Ctrl+R"
    reload_config: str = "Ctrl+C"
    exit: str = "Ctrl+Q"
    save_state: str = "Ctrl+S"
    load_state: str = "Ctrl+L"
    toggle_stepping_mode: str = "Ctrl+P"
    screenshot: str = "F12"


class KeysGBA(BaseConfig):
    """Schema for the GBA keys section in the Keys config."""

    Up: str = "Up"
    Down: str = "Down"
    Left: str = "Left"
    Right: str = "Right"
    A: str = "x"
    B: str = "z"
    L: str = "a"
    R: str = "s"
    Start: str = "Return"
    Select: str = "BackSpace"


class Logging(BaseConfig):
    """Schema for the logging configuration."""

    filename: ClassVar = "logging.yml"
    create_save_state_for_shiny: bool = True
    log_encounters: bool = False
    log_encounters_to_console: bool = True
    shiny_gifs: bool = True
    tcg_cards: bool = True



class ProfileMetadata(BaseConfig):
    """Schema for the metadata configuration file part of profiles."""

    filename: ClassVar = "metadata.yml"
    version: PositiveInt = 1
    rom: ProfileMetadataROM = Field(default_factory=lambda: ProfileMetadataROM())


class ProfileMetadataROM(BaseConfig):
    """Schema for the rom section of the metadata config."""

    file_name: str = ""
    game_code: str = ""
    revision: NonNegativeInt = 0
    language: Literal["E", "F", "D", "I", "J", "S"] = ""
