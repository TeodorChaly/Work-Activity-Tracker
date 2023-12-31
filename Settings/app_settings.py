import tkinter as tk

from Settings.save_settings import save_settings


def settings_windows(self, default_screenshot, default_afk_mode, default_time_remainder):
    print(self.screenshot, self.time_remainder, self.afk_mode, 1)
    print(default_screenshot, default_time_remainder, default_afk_mode, 2)
    setting_window = tk.Toplevel(self.root)
    setting_window.title("Settings")

    # Middle position
    window_width = 300
    window_height = 300
    position_right = int(self.root.winfo_x() + (self.root.winfo_width() / 2 - window_width / 2))
    position_down = int(self.root.winfo_y() + (self.root.winfo_height() / 2 - window_height / 2))

    setting_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # Elements
    label = tk.Label(setting_window, text=f"Settings", font=("Arial", 14))
    label.pack()

    label_email = tk.Label(setting_window, text=f"{self.email}")
    label_email.pack(pady=(0, 10))

    def on_mouse_enter(event):
        event.widget.config(text="Click to change email", fg='blue')

    def on_mouse_leave(event):
        event.widget.config(fg='black', text=f"{self.email}")

    label_email.bind("<Enter>", on_mouse_enter)
    label_email.bind("<Leave>", on_mouse_leave)
    label_email.bind("<Button-1>", on_email_click)

    self.screenshot_var = tk.BooleanVar(value=default_screenshot)
    screenshot_checkbutton = tk.Checkbutton(setting_window, text="Screenshot", variable=self.screenshot_var)
    screenshot_checkbutton.pack()

    # Time remainder - Int
    tk.Label(setting_window, text="Time remainder").pack()
    self.time_remainder_var = tk.StringVar(value=default_time_remainder)
    time_remainder_entry = tk.Entry(setting_window, textvariable=self.time_remainder_var)
    time_remainder_entry.pack()

    # AFK Mode - Int
    tk.Label(setting_window, text="AFK Mode").pack()
    self.afk_mode_var = tk.StringVar(value=default_afk_mode)
    afk_mode_entry = tk.Entry(setting_window, textvariable=self.afk_mode_var)
    afk_mode_entry.pack()

    enter_button = tk.Button(setting_window, text="Enter",
                             command=lambda: apply(setting_window, self))
    enter_button.pack(pady=(5, 5))

    setting_window.grab_set()


def on_email_click(event):
    print("Email label was clicked")


def apply(setting_window, self):
    save_settings(self)
    setting_window.destroy()
