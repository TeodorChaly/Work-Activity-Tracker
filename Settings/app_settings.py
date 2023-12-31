import tkinter as tk


def settings_windows(self):
    setting_window = tk.Toplevel(self.root)
    setting_window.title("Settings")

    # Middle position
    window_width = 300
    window_height = 200
    position_right = int(self.root.winfo_x() + (self.root.winfo_width() / 2 - window_width / 2))
    position_down = int(self.root.winfo_y() + (self.root.winfo_height() / 2 - window_height / 2))

    setting_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # Elements
    label = tk.Label(setting_window, text="Настройки")
    label.pack(pady=20)

    self.screenshoot_var = tk.BooleanVar(value=True)  # Пример начального значения
    screenshoot_checkbutton = tk.Checkbutton(setting_window, text="Screenshoot", variable=self.screenshoot_var)
    screenshoot_checkbutton.pack()

    # Time remainder - Int
    tk.Label(setting_window, text="Time remainder").pack()
    self.time_remainder_var = tk.StringVar(value="5")  # Пример начального значения
    time_remainder_entry = tk.Entry(setting_window, textvariable=self.time_remainder_var)
    time_remainder_entry.pack()

    # AFK Mode - Int
    tk.Label(setting_window, text="AFK Mode").pack()
    self.afk_mode_var = tk.StringVar(value="10")  # Пример начального значения
    afk_mode_entry = tk.Entry(setting_window, textvariable=self.afk_mode_var)
    afk_mode_entry.pack()

    enter_button = tk.Button(setting_window, text="Enter", command=apply)
    enter_button.pack()

    setting_window.grab_set()

    # Screenshoot - True/False
    # Time remainder - Int
    # AFK Mode - Int


def apply():
    print("True")
