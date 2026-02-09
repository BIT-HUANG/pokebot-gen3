"""
Contains definitions for the `BotMode` base class as well as the `BotModeError` type, so we
can import that anywhere without having to worry about circular import issues.
"""


class BotMode:
    @staticmethod
    def name() -> str:
        """
        :return: The name of this mode that will be displayed in the bot mode selection drop-down.
        """
        raise NotImplementedError




