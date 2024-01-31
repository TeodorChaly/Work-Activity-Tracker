import os
import tkinter as tk

from PIL import Image, ImageTk

from App_Files.play_music import audio_download, download_audio
from Settings.save_settings import save_settings


def settings_windows(self, default_screenshot, default_afk_mode, default_time_remainder, default_weak_goal,
                     default_volume):
    window_width = 300
    window_height = 550
    background_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    big_image_path = background_image_path + "\\App_image\\setting.jpg"
    bg_image = Image.open(big_image_path)
    bg_resized_image = bg_image.resize(
        (window_width, window_height))
    self.bg_image_set = ImageTk.PhotoImage(bg_resized_image)

    print(self.screenshot, self.time_remainder, self.afk_mode, self.week_goal, 1)
    print(default_screenshot, default_time_remainder, default_afk_mode, default_weak_goal, 2)
    setting_window = tk.Toplevel(self.root)
    setting_window.title("Settings")
    background_color = "white"

    background_label = tk.Label(setting_window, image=self.bg_image_set, bg=background_color,
                                activebackground=background_color)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    position_right = int(self.root.winfo_x() + (self.root.winfo_width() / 2 - window_width / 2))
    position_down = int(self.root.winfo_y() + (self.root.winfo_height() / 2 - window_height / 2))

    setting_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    setting_window.resizable(False, False)

    ico = Image.open('App_image/Logo_Small.ico')
    photo = ImageTk.PhotoImage(ico)
    setting_window.wm_iconphoto(False, photo)

    y_height = 15

    # Elements
    label_setting = tk.Label(setting_window, text=f"Settings", font=("Arial", 16), bg=background_color,
                             activebackground=background_color)
    label_setting.place(x=window_width // 2 - 60, y=20)

    label_email = tk.Label(setting_window, text=f"{self.email}", bg=background_color,
                           activebackground=background_color, font=("Arial", 11))
    setting_window.update()
    label_email.place(x=window_width // 2 - 30, y=60)

    label_music = tk.Label(setting_window, text=f"Change music", bg=background_color,
                           activebackground=background_color)
    label_music.place(x=window_width // 2 - 60, y=y_height + 350)


    def on_mouse_enter(event, text, x, y):
        event.widget.config(text=text, fg='blue')
        event.widget.place(x=x, y=y)

    def on_mouse_leave(event, text, x, y):
        event.widget.config(fg='black', text=text)
        event.widget.place(x=x, y=y)

    label_email.bind("<Enter>",
                     lambda event: on_mouse_enter(event, "Click to change email", window_width // 2 - 100, 60))
    label_email.bind("<Leave>", lambda event: on_mouse_leave(event, f"{self.email}", window_width // 2 - 30, 60))
    label_email.bind("<Button-1>", lambda event: on_email_click(event, self))

    label_music.bind("<Enter>",
                     lambda event: on_mouse_enter(event, "Click to change music", window_width // 2 - 90,
                                                  y_height + 350))
    label_music.bind("<Leave>",
                     lambda event: on_mouse_leave(event, "Change music", window_width // 2 - 60, y_height + 350))
    label_music.bind("<Button-1>", lambda event: change_music(event, self))

    self.screenshot_var = tk.BooleanVar(value=default_screenshot)
    screenshot_checkbutton = tk.Checkbutton(setting_window, text="Screenshot", variable=self.screenshot_var,
                                            bg=background_color,
                                            activebackground=background_color)
    screenshot_checkbutton.place(x=window_width // 2 - 60, y=y_height + 100)

    # Time remainder - Int
    self.time_label_remainder = tk.Label(setting_window, text="Time remainder (minute)", bg=background_color,
                                         activebackground=background_color)
    self.time_label_remainder.place(x=window_width // 2 - 100, y=y_height + 140)
    self.time_remainder_var = tk.StringVar(value=default_time_remainder)
    time_remainder_entry = tk.Entry(setting_window, textvariable=self.time_remainder_var, bg=background_color)
    time_remainder_entry.place(x=window_width // 2 - 100, y=y_height + 170)

    # AFK Mode - Int
    self.afk_label = tk.Label(setting_window, text="AFK Mode (minute)", bg=background_color,
                              activebackground=background_color)
    self.afk_label.place(x=window_width // 2 - 75, y=y_height + 210)
    self.afk_mode_var = tk.StringVar(value=default_afk_mode)
    afk_mode_entry = tk.Entry(setting_window, textvariable=self.afk_mode_var, bg=background_color)
    afk_mode_entry.place(x=window_width // 2 - 100, y=y_height + 240)

    # Weak goal - Int
    self.weak_label = tk.Label(setting_window, text="Weak goal (hours)", bg=background_color,
                               activebackground=background_color)
    self.weak_label.place(x=window_width // 2 - 75, y=y_height + 280)
    self.week_goal_var = tk.StringVar(value=default_weak_goal)
    week_goal_entry = tk.Entry(setting_window, textvariable=self.week_goal_var)
    week_goal_entry.place(x=window_width // 2 - 100, y=y_height + 310)

    # Volume - Int

    tk.Label(setting_window, text="Volume (music)", bg=background_color,
             activebackground=background_color).place(x=window_width // 2 - 65, y=y_height + 390)

    self.volume_var = tk.IntVar(value=default_volume)
    volume_scale = tk.Scale(setting_window, from_=0, to=10, orient='horizontal', variable=self.volume_var,
                            bg=background_color, activebackground=background_color, highlightthickness=0, borderwidth=0)
    volume_scale.place(x=window_width // 2 - 55, y=y_height + 420)

    # Save button
    self.enter_button = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\App_image\\enter_button.png"
    self.enter_button_1 = Image.open(self.enter_button).resize(
        (100, 40))
    self.enter_button_2 = ImageTk.PhotoImage(self.enter_button_1)
    print(self.enter_button_2)
    enter_button = tk.Button(setting_window, text="Enter",
                             command=lambda: apply(setting_window, self), image=self.enter_button_2, borderwidth=0,
                             highlightthickness=0)
    enter_button.place(x=window_width // 2 - 57, y=y_height + 480)

    setting_window.grab_set()


def on_email_click(event, self):
    print("Email label was clicked")

    file_path = 'cash_user.bin'

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File {file_path} was deleted.")
        self.root.destroy()
        re_log_reg()

    else:
        print(f"File {file_path} wasn't found.")


def re_log_reg():
    from run_app import App

    root = tk.Tk()
    app = App(root)

    root.mainloop()


def change_music(event, self):
    second_window = tk.Toplevel(self.root)
    second_window.title("Choose audio")
    second_window.grab_set()  # Делает окно модальным

    url_label = tk.Label(second_window, text="Enter link of audio from YouTube:")
    url_label.pack()

    url_entry = tk.Entry(second_window, width=40)
    url_entry.pack()

    status_label = tk.Label(second_window, text="")
    status_label.pack()

    def start_download():
        url = url_entry.get()
        download_audio(url, self, second_window)
        on_close_second_window(second_window)
        self.music_player = None

    download_button = tk.Button(second_window, text="Save audio", command=start_download)
    download_button.pack()

    second_window.protocol("WM_DELETE_WINDOW", lambda: on_close_second_window(second_window))


def on_close_second_window(window):
    window.grab_release()  # Освобождает блокировку при закрытии окна
    window.destroy()


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def apply(setting_window, self):
    error_message = ""

    if not is_number(self.time_remainder_var.get()):
        self.time_label_remainder.config(fg="red")

    if not is_number(self.afk_mode_var.get()):
        self.afk_label.config(fg="red")

    if not is_number(self.week_goal_var.get()):
        self.weak_label.config(fg="red")

    if error_message:
        print("Error")
    else:
        save_settings(self)
        setting_window.destroy()
