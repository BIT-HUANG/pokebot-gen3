import queue
import sys
from collections import deque
from typing import Generator

from modules.console import console
from modules.context import context

from modules.modes import BotMode


# Contains a queue of tasks that should be run the next time a frame completes.
# This is currently used by the HTTP server component (which runs in a separate thread) to trigger things
# such as extracting the current party, which need to be done from the main thread.
# Each entry here will be executed exactly once and then removed from the queue.
work_queue: queue.Queue[callable] = queue.Queue()


# Keeps a list of inputs that have been pressed for each frame so that the HTTP server
# can fetch and accumulate them for its `Inputs` stream event.
inputs_each_frame: deque[int] = deque(maxlen=128)


class ManualBotMode(BotMode):
    @staticmethod
    def name() -> str:
        return "Manual"

    def run(self) -> Generator:
        yield


def main_loop() -> None:
    """
    This function is run after the user has selected a profile and the emulator has been started.
    """
    try:
        if context.rom.game_name.startswith("Unsupported "):
            console.print("\n[red bold]You are running an unsupported game![/]")
            console.print(
                "\n[red]This ROM does not appear to be an exact copy of an original Gen3 game.\nIt's possible that is has been modified, or that it got corrupted while dumping the cartridge.\nWhile this might still work, chances are that some or all bot functions will not.[/]"
            )
            console.print("\n[red bold]Please do not ask for support if there are any problem with this game.[/]\n")

        # Built-in plugins are only loaded if some bot configuration actually requires them.
        # Since profile configuration can override global configuration, they can only be
        # loaded at this point where the profile has been loaded and so the full config is
        # available.
        #
        # Regular (user-provided) plugins need to be loaded in `pokebot.py` as early as possible
        # because they might add bot modes.




        while True:
            # Process work queue, which can be used to get the main thread to access the emulator
            # at a 'safe' time (i.e. not in the middle of emulating a frame.)
            while not work_queue.empty():
                callback = work_queue.get_nowait()
                callback()
                work_queue.task_done()

            context.frame += 1






            if context.bot_mode == "Manual":
                if not isinstance(context.bot_mode_instance, ManualBotMode):
                    context.emulator.reset_held_buttons()
                context.bot_mode_instance = ManualBotMode()


            try:
                if context.bot_mode == "Manual":
                    context.controller_stack = []
                if len(context.controller_stack) > 0:
                    next(context.controller_stack[-1])
            except (StopIteration, GeneratorExit):
                context.controller_stack.pop()
            except TimeoutError:
                console.print_exception()
                sys.exit(1)
            except Exception as e:
                console.print_exception()
                context.emulator.reset_held_buttons()
                context.message = f"Internal Bot Error: {str(e)}"
                context.set_manual_mode()

            inputs_each_frame.append(context.emulator.get_inputs())
            context.emulator.run_single_frame()


    except SystemExit:
        raise
    except Exception:
        console.print_exception(show_locals=True)
        sys.exit(1)
