import os
import tkinter as tk

from PIL import Image, ImageTk

from Settings.save_settings import save_settings


def settings_windows(self, default_screenshot, default_afk_mode, default_time_remainder, default_weak_goal):
    background_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    big_image_path = background_image_path + "\\App_image\\setting.jpg"
    bg_image = Image.open(big_image_path)
    bg_resized_image = bg_image.resize(
        (300, 450))
    self.bg_image_set = ImageTk.PhotoImage(bg_resized_image)

    print(self.screenshot, self.time_remainder, self.afk_mode, self.week_goal, 1)
    print(default_screenshot, default_time_remainder, default_afk_mode, default_weak_goal, 2)
    setting_window = tk.Toplevel(self.root)
    setting_window.title("Settings")
    background_color = "white"

    background_label = tk.Label(setting_window, image=self.bg_image_set, bg=background_color,
                                activebackground=background_color)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Middle position
    window_width = 300
    window_height = 450
    position_right = int(self.root.winfo_x() + (self.root.winfo_width() / 2 - window_width / 2))
    position_down = int(self.root.winfo_y() + (self.root.winfo_height() / 2 - window_height / 2))

    setting_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    setting_window.resizable(False, False)

    # Elements
    label_setting = tk.Label(setting_window, text=f"Settings", font=("Arial", 15), bg=background_color,
                             activebackground=background_color)
    label_setting.place(x=window_width // 2 - 60, y=10)

    label_email = tk.Label(setting_window, text=f"{self.email}", bg=background_color,
                           activebackground=background_color)
    label_email.place(x=window_width // 2 - 60, y=50)

    def on_mouse_enter(event):
        event.widget.config(text="Click to change email", fg='blue')
        event.widget.place(x=window_width // 2 - 85, y=50)

    def on_mouse_leave(event):
        event.widget.config(fg='black', text=f"{self.email}")
        event.widget.place(x=window_width // 2 - 60, y=50)

    label_email.bind("<Enter>", on_mouse_enter)
    label_email.bind("<Leave>", on_mouse_leave)
    label_email.bind("<Button-1>", on_email_click)

    self.screenshot_var = tk.BooleanVar(value=default_screenshot)
    screenshot_checkbutton = tk.Checkbutton(setting_window, text="Screenshot", variable=self.screenshot_var,
                                            bg=background_color,
                                            activebackground=background_color)
    screenshot_checkbutton.place(x=window_width // 2 - 60, y=100)

    # Time remainder - Int
    tk.Label(setting_window, text="Time remainder (minute)", bg=background_color,
             activebackground=background_color).place(x=window_width // 2 - 100, y=140)
    self.time_remainder_var = tk.StringVar(value=default_time_remainder)
    time_remainder_entry = tk.Entry(setting_window, textvariable=self.time_remainder_var, bg=background_color)
    time_remainder_entry.place(x=window_width // 2 - 100, y=170)

    # AFK Mode - Int
    tk.Label(setting_window, text="AFK Mode (minute)", bg=background_color,
             activebackground=background_color).place(x=window_width // 2 - 75, y=210)
    self.afk_mode_var = tk.StringVar(value=default_afk_mode)
    afk_mode_entry = tk.Entry(setting_window, textvariable=self.afk_mode_var, bg=background_color)
    afk_mode_entry.place(x=window_width // 2 - 100, y=240)

    # Weak goal - Int
    tk.Label(setting_window, text="Weak goal (hours)", bg=background_color,
             activebackground=background_color).place(x=window_width // 2 - 75, y=280)
    self.week_goal_var = tk.StringVar(value=default_weak_goal)
    week_goal_entry = tk.Entry(setting_window, textvariable=self.week_goal_var)
    week_goal_entry.place(x=window_width // 2 - 100, y=310)

    enter_button = tk.Button(setting_window, text="Enter",
                             command=lambda: apply(setting_window, self))
    enter_button.place(x=window_width // 2 - 30, y=360)

    self.error_label = tk.Label(setting_window, fg="red", bg=background_color,
                                activebackground=background_color)
    self.error_label.place(x=window_width // 2 - 100, y=410)

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
        error_message += "Not correct time remainder\n"

    if not is_number(self.afk_mode_var.get()):
        error_message += "Not correct AFK mode\n"

    if not is_number(self.week_goal_var.get()):
        error_message += "Not correct week goal\n"

    if error_message:
        error_message = "" + error_message.rstrip(", ")
        self.error_label.config(text=error_message)
    else:
        self.error_label.config(text="")
        save_settings(self)
        setting_window.destroy()
