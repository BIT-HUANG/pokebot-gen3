"""Contains modes of operation for the bot."""

from typing import TYPE_CHECKING, Type

from ._interface import BattleAction, BotListener, BotMode, BotModeError, FrameInfo


if TYPE_CHECKING:
    from modules.roms import ROM

# 清空模式缓存（原本存储自动化模式）
_bot_modes: list[Type[BotMode]] = []


def get_bot_mode_names() -> list[str]:
    # 仅保留 Manual 手动模式，移除所有自动化模式名称
    return ["Manual"]


def get_bot_mode_by_name(name: str) -> Type[BotMode] | None:
    # 任何自动化模式名称都返回 None（仅 Manual 无对应模式类）
    return None

