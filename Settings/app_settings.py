import tkinter as tk

from Settings.save_settings import save_settings


def settings_windows(self, default_screenshot, default_afk_mode, default_time_remainder, default_weak_goal):
    print(self.screenshot, self.time_remainder, self.afk_mode, self.week_goal, 1)
    print(default_screenshot, default_time_remainder, default_afk_mode, default_weak_goal, 2)
    setting_window = tk.Toplevel(self.root)
    setting_window.title("Settings")

    # Middle position
    window_width = 300
    window_height = 380
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
    tk.Label(setting_window, text="Time remainder (minute)").pack()
    self.time_remainder_var = tk.StringVar(value=default_time_remainder)
    time_remainder_entry = tk.Entry(setting_window, textvariable=self.time_remainder_var)
    time_remainder_entry.pack()

    # AFK Mode - Int
    tk.Label(setting_window, text="AFK Mode (minute)").pack()
    self.afk_mode_var = tk.StringVar(value=default_afk_mode)
    afk_mode_entry = tk.Entry(setting_window, textvariable=self.afk_mode_var)
    afk_mode_entry.pack()

    # Weak goal - Int
    tk.Label(setting_window, text="Weak goal (hours)").pack()
    self.week_goal_var = tk.StringVar(value=default_weak_goal)
    week_goal_entry = tk.Entry(setting_window, textvariable=self.week_goal_var)
    week_goal_entry.pack()

    enter_button = tk.Button(setting_window, text="Enter",
                             command=lambda: apply(setting_window, self))
    enter_button.pack(pady=(5, 5))

    self.error_label = tk.Label(setting_window, fg="red")
    self.error_label.pack()

    setting_window.grab_set()


def on_email_click(event):
    print("Email label was clicked")


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def apply(setting_window, self):
    error_message = ""

    if not is_number(self.time_remainder_var.get()):
        error_message += "not correct  time remainder, "

    if not is_number(self.afk_mode_var.get()):
        error_message += "not correct AFK mode, "

    if not is_number(self.week_goal_var.get()):
        error_message += "not correct week goal, "

    if error_message:
        error_message = "Error: " + error_message.rstrip(", ")
        self.error_label.config(text=error_message)
    else:
        self.error_label.config(text="")
        save_settings(self)
        setting_window.destroy()
