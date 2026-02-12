import tkinter.font
from tkinter import Menu, Tk, ttk
from typing import Union

from showinfm import show_in_file_manager
from modules.context import context


class EmulatorControls:
    def __init__(self, window: Tk):
        self.window = window

        self.frame: Union[ttk.Frame, None] = None
        self.menu_bar: Union[Menu, None] = None
        self.speed_1x_button: ttk.Button
        self.speed_menu_button: ttk.Button | None
        self.unthrottled_button: ttk.Button
        self.toggle_video_button: ttk.Button
        self.toggle_audio_button: ttk.Button
        self.bot_message: ttk.Label
        self.stats_label: ttk.Label

        self.emulator_menu: Menu | None = None
        self.profile_menu: Menu | None = None
        self.help_menu: Menu | None = None
        self.debug_menu: Menu | None = None

    def get_additional_width(self) -> int:
        return 0

    def get_additional_height(self) -> int:
        return 200

    def add_to_window(self) -> None:
        from modules.gui import LoadStateWindow

        self.menu_bar = Menu(self.window)

        self.emulator_menu = Menu(self.window, tearoff=0)
        self.emulator_menu.add_command(label="Load Save State", command=lambda: LoadStateWindow(self.window))
        self.emulator_menu.add_command(
            label="New Save State", command=lambda: context.emulator.create_save_state("Manual")
        )
        self.emulator_menu.add_command(
            label="Take Screenshot", command=lambda: context.emulator.take_screenshot("manual")
        )
        self.emulator_menu.add_separator()
        self.emulator_menu.add_command(label="Reset", command=context.emulator.reset)

        self.profile_menu = Menu(self.window, tearoff=0)
        self.profile_menu.add_command(
            label="Open Profile Folder", command=lambda: show_in_file_manager(str(context.profile.path))
        )

        # self.help_menu = Menu(self.window, tearoff=0)
        # self.help_menu.add_command(
        #     label=f"BD4SLW mGBA Wiki",
        #     command=lambda: webbrowser.open_new_tab("https://github.com/40Cakes/pokebot-gen3/tree/main/wiki"),
        # )
        # self.help_menu.add_command(
        #     label="Discord #pokebot-gen3-support",
        #     command=lambda: webbrowser.open_new_tab(
        #         "https://discord.com/channels/1057088810950860850/1139190426834833528"
        #     ),
        # )

        self.menu_bar.add_cascade(label="Emulator", menu=self.emulator_menu)
        self.menu_bar.add_cascade(label="Profile", menu=self.profile_menu)
        # self.menu_bar.add_cascade(label="Help", menu=self.help_menu)


        self.window.config(menu=self.menu_bar)

        self.frame = ttk.Frame(self.window, padding=5)
        self.frame.grid(row=1, sticky="NSWE")
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self._add_speed_controls(row=0, column=1, sticky="N")
        self._add_settings_controls(row=0, column=2)

        self._add_message_area(row=1, column=0, columnspan=3)
        self._add_stats_and_version_notice(row=2, column=0, columnspan=3)

        self.update()

    def remove_from_window(self) -> None:
        if self.frame:
            self.frame.destroy()

        self.frame = None

    def update(self) -> None:
        if self.frame is None:
            return

        if context.emulation_speed > 1:
            speed_text = f"{context.emulation_speed}× ▾"
        else:
            speed_text = "… ▾"
        self.speed_menu_button.config(text=speed_text)

        self._set_button_colour(self.speed_1x_button, active_condition=context.emulation_speed == 1)
        self._set_button_colour(self.speed_menu_button, active_condition=context.emulation_speed > 1)
        self._set_button_colour(self.unthrottled_button, active_condition=context.emulation_speed == 0)

        self._set_button_colour(self.toggle_video_button, active_condition=context.video)
        self._set_button_colour(
            self.toggle_audio_button, active_condition=context.audio, disabled_condition=context.emulation_speed == 0
        )

        self.bot_message.config(text=context.message)


    def on_video_output_click(self, click_location: tuple[int, int], scale: int):
        pass


    def _add_speed_controls(self, row: int, column: int, sticky: str = "W"):
        def set_emulation_speed(speed: int) -> None:
            context.emulation_speed = speed
            self.update()

        def open_speed_menu():
            bold_font = tkinter.font.Font(self.window, weight="bold", size=10)
            self.speed_menu = tkinter.Menu(self.window, tearoff=0)

            speeds = [
                (f"1× (key: {context.config.keys.emulator.set_speed_1x})", 1),
                (f"2× (key: {context.config.keys.emulator.set_speed_2x})", 2),
                (f"3× (key: {context.config.keys.emulator.set_speed_3x})", 3),
                (f"4× (key: {context.config.keys.emulator.set_speed_4x})", 4),
                (f"8× (key: {context.config.keys.emulator.set_speed_8x})", 8),
                (f"16× (key: {context.config.keys.emulator.set_speed_16x})", 16),
                (f"32× (key: {context.config.keys.emulator.set_speed_32x})", 32),
                (f"Unthrottled (key: {context.config.keys.emulator.set_speed_unthrottled})", 0),
            ]
            for label, speed in speeds:
                if context.emulation_speed == speed:
                    self.speed_menu.add_command(
                        label=label, font=bold_font, command=lambda s=speed: set_emulation_speed(s)
                    )
                else:
                    self.speed_menu.add_command(label=label, command=lambda s=speed: set_emulation_speed(s))

            self.speed_menu.tk_popup(
                self.speed_menu_button.winfo_rootx(),
                self.speed_menu_button.winfo_rooty() + self.speed_menu_button.winfo_height(),
            )

        group = ttk.Frame(self.frame)
        group.grid(row=row, column=column, sticky=sticky)
        group.columnconfigure(3, weight=1)

        ttk.Label(group, text="Emulation Speed:", justify="left").grid(row=0, column=0, columnspan=4, sticky="W")

        button_settings = {"width": 4, "padding": (0, 3), "cursor": "hand2"}
        menu_button_settings = {**button_settings, "width": 6}
        self.speed_1x_button = ttk.Button(group, text="1×", **button_settings, command=lambda: set_emulation_speed(1))
        self.speed_menu_button = ttk.Button(group, text="…", **menu_button_settings, command=open_speed_menu)
        self.unthrottled_button = ttk.Button(group, text="∞", **button_settings, command=lambda: set_emulation_speed(0))

        self.speed_1x_button.grid(row=1, column=0)
        self.speed_menu_button.grid(row=1, column=1)
        self.unthrottled_button.grid(row=1, column=2)

    def _add_settings_controls(self, row: int, column: int):
        group = ttk.Frame(self.frame)
        style = ttk.Style()
        style.map(
            "Accent.TButton",
            foreground=[("!active", "white"), ("active", "white"), ("pressed", "white")],
            background=[("!active", "purple1"), ("active", "purple3"), ("pressed", "purple1")],
        )
        group.grid(row=row, column=column, sticky="W")

        ttk.Label(group, text="Other Settings:").grid(row=0, columnspan=2, sticky="W")

        button_settings = {"width": 6, "padding": (0, 3), "cursor": "hand2"}
        self.toggle_video_button = ttk.Button(group, text="Video", **button_settings, command=context.toggle_video)
        self.toggle_audio_button = ttk.Button(group, text="Audio", **button_settings, command=context.toggle_audio)

        self.toggle_video_button.grid(row=1, column=0, padx=2)
        self.toggle_audio_button.grid(row=1, column=1, padx=2)

    def _add_message_area(self, row: int, column: int, columnspan: int = 1):
        group = ttk.LabelFrame(self.frame, text="Message:", padding=(10, 5))
        group.grid(row=row, column=column, columnspan=columnspan, sticky="NSWE", pady=10)

        self.bot_message = ttk.Label(group, wraplength=440, justify="left")
        self.bot_message.grid(row=0, sticky="NW")

    def _add_stats_and_version_notice(self, row: int, column: int, columnspan: int = 1):
        group = ttk.Frame(self.frame)
        group.columnconfigure(0, weight=1)
        group.grid(row=row, column=column, columnspan=columnspan, sticky="SWE")

        self.stats_label = ttk.Label(group, text="", foreground="grey", font=tkinter.font.Font(size=9))
        self.stats_label.grid(row=0, column=0, sticky="W")

        version_label = ttk.Label(
            group,
            text=f"{context.rom.short_game_name} - BD4SLW mGBA",
            foreground="grey" if not context.rom.game_name.startswith("Unsupported") else "red",
            font=tkinter.font.Font(size=9),
        )

        # In debug mode, we are displaying more performance stats in the footer (left side.)
        # So for game with particularly long names (e.g. 'LeafGreen (E) (Rev 1)', the stats
        # and the game/version info on the right combined become wider than the emulator screen,
        # leading to the window growing and shrinking.
        #
        # This puts the game/version info in a separate line in debug mode.
        if context.debug:
            version_label.grid(row=1, column=0, sticky="W")
        else:
            version_label.grid(row=0, column=1, sticky="E")

    def _set_button_colour(self, button: ttk.Button, active_condition: bool, disabled_condition: bool = False) -> None:
        if disabled_condition:
            button.config(style="TButton", state="disabled")
        elif active_condition:
            button.config(style="Accent.TButton", state="normal")
        else:
            button.config(style="TButton", state="normal")

