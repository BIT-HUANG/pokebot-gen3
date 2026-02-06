from dataclasses import dataclass

from modules.context import context
from modules.memory import unpack_uint16, get_save_block


@dataclass
class ClockTime:
    days: int
    hours: int
    minutes: int
    seconds: int

    def __str__(self):
        return f"{self.days} day{'s' if self.days != 1 else ''}, {self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"

    def total_minutes(self) -> int:
        return self.days * 24 * 60 + self.hours * 60 + self.minutes




@dataclass
class PlayTime:
    hours: int
    minutes: int
    seconds: int
    frames: int

    def __str__(self):
        return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d} +{self.frames} frames"


def get_play_time() -> PlayTime:
    """
    Returns the play time counter. This gets advanced every frame and so is tied to
    the emulation speed as well.

    It's the time the game will display on the trainer card, while saving, etc.

    :return: Time played as reported by the game. This has a maximum value of 999 days,
             59 minutes, 59 seconds, and 59 frames. Once that value is reached, this
             time will not advance anymore.
    """
    save_block_time = get_save_block(2, offset=0x0E, size=0x5)
    return PlayTime(unpack_uint16(save_block_time[0:2]), save_block_time[2], save_block_time[3], save_block_time[4])
