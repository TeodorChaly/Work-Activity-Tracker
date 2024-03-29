import os
import random
import time
from datetime import datetime
from time import strftime, gmtime

import tkinter as tk
from tkinter import font
import ctypes
import pyglet
from PIL import Image, ImageTk
from pynput import mouse, keyboard

from App_Files.GUI import popup_notification
from App_Files.activity_window import open_second_window
from App_Files.afk_detektor import AFKDetector
from App_Files.play_music import audio_check, audio_download, play_music_switcher
from DataBase.db_connection import create_db_connection
from DataBase.db_logs_operations import session_db_add, get_time_today
from DataBase.db_time_writing import db_time_write
from App_Files.images_controller import take_screenshot_all_monitors as take_screenshots
from Settings.app_settings import settings_windows
from Settings.save_settings import load_settings


class TimerApp:
    def __init__(self, root, user_name, user_surname, email):
        self.connection = create_db_connection()

        background_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        play_img_path = background_image_path + "\\App_image\\play.png"
        pause_img_path = background_image_path + "\\App_image\\stop.png"

        self.user_name = user_name
        self.user_surname = user_surname

        self.background_label = tk.Label(root)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.root = root
        self.email = email
        root.title("Timer")
        ico = Image.open('App_image/Logo_Small.ico')
        photo = ImageTk.PhotoImage(ico)
        root.wm_iconphoto(False, photo)

        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        root.geometry("500x500")
        root.resizable(False, False)
        root.configure(bg="white")

        background_color = "white"

        # Customize settings
        self.screenshot = load_settings(self, "screenshot")
        self.afk_mode = int(load_settings(self, "afk_mode"))
        self.week_goal = int(load_settings(self, "week_goal"))
        self.time_remainder = int(load_settings(self, "time_remainder")) * 60
        self.volume = int(load_settings(self, "volume")) * 60

        # Time settings
        self.now = datetime.now()
        self.current_hour = self.now.strftime("%H:%M:%S")
        self.session_time = 0
        self.current_time = self.now.date()

        self.elapsed_time = get_time_today(self.email, self.current_time, self.connection)

        change = self.week_goal * 60 // 7
        self.hours, self.remainder = divmod(change, 60)

        # GUI
        custom_font = font.Font(family="Open Sans", size=16, weight="normal")
        self.setting_button = tk.Button(self.root, text="Settings", relief="flat", command=self.setting_button_click,
                                        bg=background_color, activebackground=background_color, font=custom_font,
                                        fg="gray")
        self.setting_button.place(x=178, y=60)
        self.setting_button.bind("<Enter>", lambda event, label=self.setting_button: label.config(fg="black"))
        self.setting_button.bind("<Leave>", lambda event, label=self.setting_button: label.config(fg="gray"))

        custom_font = font.Font(family="Open Sans", size=14, weight="normal")
        self.link_button = tk.Button(self.root, text="Activity", relief="flat",
                                     command=self.open_second_window_wrapper, bg=background_color,
                                     activebackground=background_color, fg="gray", font=custom_font)
        self.link_button.place(x=75, y=125)
        self.link_button.bind("<Enter>", lambda event, label=self.link_button: label.config(fg="black"))
        self.link_button.bind("<Leave>", lambda event, label=self.link_button: label.config(fg="gray"))

        self.check_audio()

        custom_font = font.Font(family="Open Sans", size=14, weight="normal")
        self.goal_label = tk.Label(root,
                                   text=f"Goal(h)\n{round((self.elapsed_time // 60) / 60, 2)}/{self.hours:1}.{self.remainder // 6}",
                                   font=custom_font,
                                   bg=background_color,
                                   fg="gray")
        self.goal_label.place(x=315, y=115)

        custom_font = font.Font(family="Open Sans", size=54, weight="normal")
        self.time_label = tk.Label(root, text="00:00:00", font=custom_font, bg=background_color)
        self.time_label.place(x=36, y=188)

        play_image = Image.open(play_img_path).resize((82, 82))
        pause_image = Image.open(pause_img_path).resize((82, 82))
        self.play_img = ImageTk.PhotoImage(play_image)

        self.pause_img = ImageTk.PhotoImage(pause_image)
        self.start_button = tk.Button(root, image=self.play_img, command=self.start_timer, bg=background_color,
                                      activebackground=background_color, borderwidth=0, highlightthickness=0)
        self.start_button.place(x=150, y=330)

        self.pause_button = tk.Button(root, image=self.pause_img, command=self.pause_timer, state=tk.DISABLED,
                                      bg=background_color, activebackground=background_color, borderwidth=0,
                                      highlightthickness=0)
        self.pause_button.place(x=265, y=330)

        # General settings
        self.running = False
        self.next_notification_time = self.time_remainder
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.display_time()
        self.interval = 0
        self.remaining_interval = None

        # AFK mode checking
        self.aft_timer = 0
        self.afk_detector = AFKDetector(int(self.afk_mode))
        mouse_listener = mouse.Listener(on_move=self.afk_detector.update_last_action_time,
                                        on_click=self.afk_detector.update_last_action_time)
        keyboard_listener = keyboard.Listener(on_press=self.afk_detector.update_last_action_time)
        mouse_listener.start()
        keyboard_listener.start()

        self.music_player = None
        self.position = 0

        self.image_progress_changer()

    def check_playback(self):
        if self.music_player is not None:
            if self.music_player.time >= self.music_player.source.duration:
                print("End of song, playing again")
                self.position = 0
                self.music_player.play()
                self.music_player.seek(self.position)
        self.root.after(100, self.check_playback)

    def check_audio(self):
        background_color = "white"
        if audio_check(self):
            custom_font = font.Font(family="Open Sans", size=14, weight="normal")
            self.music = tk.Label(self.root, text="Music", fg="gray", cursor="hand2", bg=background_color,
                                  font=custom_font)
            self.music.bind("<Enter>", lambda event, label=self.music: label.config(fg="black"))
            self.music.bind("<Leave>", lambda event, label=self.music: label.config(fg="gray"))
            self.music.bind("<Button-1>", lambda event: play_music_switcher(self))
            self.music.place(x=205, y=135)
        else:
            custom_font = font.Font(family="Open Sans", size=14, weight="normal")
            self.music = tk.Label(self.root, text="Set music", fg="gray", cursor="hand2", bg=background_color,
                                  font=custom_font)
            self.music.bind("<Enter>", lambda event, label=self.music: label.config(fg="black"))
            self.music.bind("<Leave>", lambda event, label=self.music: label.config(fg="gray"))
            self.music.bind("<Button-1>", lambda event: audio_download(self))
            self.music.place(x=185, y=135)

    def open_second_window_wrapper(self):
        open_second_window(self)

    def random_picture(self):  # Screenshots
        if self.remaining_interval is not None:
            self.interval = self.remaining_interval
            self.remaining_interval = None
            # print("Continue (in seconds)", self.interval // 1000)
        else:
            min_val = 1000 * 10 * 60
            max_val = 1000 * 20 * 60
            self.interval = random.randint(min_val, max_val)
            # print("New time for screenshot: ", self.interval // 1000)

        self.root.after(self.interval, self.screenshot_picture)

    def screenshot_picture(self):  # Fix (memory leak)
        if self.running:
            screenshot_path = take_screenshots()

            session_db_add(self, self.current_time, self.email, self.current_time, self.current_hour, self.session_time,
                           screenshot_path)

            file_path = "App_Files/time_cash.txt"

            if os.path.exists(file_path):
                os.remove(file_path)

            self.session_time = 0

            self.now = datetime.now()
            self.current_time = self.now.date()

            self.current_hour = self.now.strftime("%H:%M:%S")
            if self.screenshot:
                self.random_picture()
            popup_notification("Screenshot taken", 2)

    def save_time(self):
        hours, remainder = divmod(self.elapsed_time, 3600)
        print(hours, remainder)
        minutes, seconds = divmod(remainder, 60)
        db_time_write(self, hours, minutes, seconds, self.email)

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_timer()
            self.start_button['state'] = tk.DISABLED
            self.pause_button['state'] = tk.NORMAL

            self.now = datetime.now()

            self.current_time = self.now.date()

            self.current_hour = self.now.strftime("%H:%M:%S")

            if self.screenshot:
                self.random_picture()

            self.timer_start_time = time.time()

    def pause_timer(self):
        self.save_time()
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED

        session_db_add(self, self.current_time, self.email, self.current_time, self.current_hour, self.session_time,
                       "None")

        file_path = "App_Files/time_cash.txt"

        if os.path.exists(file_path):
            os.remove(file_path)

        self.session_time = 0

        if self.interval > 0:
            self.remaining_interval = self.interval - int((time.time() - self.timer_start_time) * 1000)
            self.interval = 0


    def temporary_pause_timer(self):
        self.save_time()
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED
        self.wait_for_activity_to_resume_timer()

        if self.interval > 0:
            self.remaining_interval = self.interval - int((time.time() - self.timer_start_time) * 1000)
            self.interval = 0

    def on_close(self):
        self.save_time()
        self.root.destroy()

    def wait_for_activity_to_resume_timer(self):
        if not self.afk_detector.is_afk():
            popup_notification(f"        Welcome back!\n You have been offline for {self.aft_timer//60} min", 2)
            self.aft_timer = 0
            self.start_timer()
            self.now = datetime.now()
            self.current_hour = self.now.strftime("%H:%M:%S")
        else:
            self.root.after(1000, self.wait_for_activity_to_resume_timer)
            self.aft_timer += 1

    def display_time(self):
        hours, remainder = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.time_label.config(text=time_string)

    def get_next_notification_time(self):
        return random.randint(10 * 60, 25 * 60)  # Random check from 600 to 900 sec

    def update_timer(self):
        if self.running:
            self.image_progress_changer()

            self.elapsed_time += 1
            self.display_time()
            time_string = strftime('%H:%M:%S', gmtime(self.elapsed_time))
            self.time_label.config(text=time_string)

            if self.afk_detector.is_afk():
                # PopupNotification(self.root, "You are AFK.", 2).show()
                popup_notification("You are AFK.", 10)
                self.temporary_pause_timer()

            self.next_notification_time -= 1
            print(self.next_notification_time)
            if self.next_notification_time <= 0:
                notification_play = pyglet.media.Player()
                notification_play.queue(pyglet.resource.media("notification_sound.mp3"))
                notification_play.volume = int(load_settings(self, "week_goal")) / 10
                notification_play.play()
                popup_notification(f"It's been {self.time_remainder // 60} minute.\n   Take a break!",
                                   5)

                self.next_notification_time = self.time_remainder

            if self.elapsed_time % 1 == 0:  # Check every 10 seconds and save time and DB
                self.current_time = datetime.now().date()
                with open("App_Files/time_cash.txt", "w") as file:
                    file.write(
                        str(self.current_time) + "|" + str(self.email) + "|" + str(self.current_time) + "|" + str(
                            self.current_hour) + "|" + str(self.session_time) + "|" + "None")

            self.session_time += 1

            print("Total today's time:", self.elapsed_time, "Next, notification:", self.next_notification_time)

            self.goal_label.config(
                text=f"Goal(h)\n{round((self.elapsed_time // 60) / 60, 2)}/{self.hours:1}.{self.remainder // 6}")

            self.root.after(1000, self.update_timer)

    def image_progress_changer(self):
        # week_goal round to int
        time_now = self.elapsed_time // 60
        day_goal = self.hours * 60 + self.remainder

        if time_now >= day_goal:
            self.change_bg("\\App_image\\Circle\\circle_10.png")
            popup_notification("Your reached day's goal!", 2)
        if time_now // (day_goal / 23) == 0:
            self.change_bg("\\App_image\\Circle\\circle_0.png")
        if time_now // (day_goal / 23) == 1:
            self.change_bg("\\App_image\\Circle\\circle_1.png")
        if time_now // (day_goal / 23) == 2:
            self.change_bg("\\App_image\\Circle\\circle_1_2.png")
        if time_now // (day_goal / 23) == 3:
            self.change_bg("\\App_image\\Circle\\circle_1_3.png")
        if time_now // (day_goal / 23) == 4:
            self.change_bg("\\App_image\\Circle\\circle_1_4.png")
        if time_now // (day_goal / 23) == 5:
            self.change_bg("\\App_image\\Circle\\circle_1_5.png")
        if time_now // (day_goal / 23) == 6:
            self.change_bg("\\App_image\\Circle\\circle_1_6.png")
        if time_now // (day_goal / 23) == 7:
            self.change_bg("\\App_image\\Circle\\circle_1_7.png")
        if time_now // (day_goal / 23) == 8:
            self.change_bg("\\App_image\\Circle\\circle_1_8.png")
        if time_now // (day_goal / 23) == 9:
            self.change_bg("\\App_image\\Circle\\circle_1_9.png")
        if time_now // (day_goal / 23) == 10:
            self.change_bg("\\App_image\\Circle\\circle_1_10.png")
        if time_now // (day_goal / 23) == 11:
            self.change_bg("\\App_image\\Circle\\circle_1_11.png")
        if time_now // (day_goal / 23) == 12:
            self.change_bg("\\App_image\\Circle\\circle_1_12.png")
        if time_now // (day_goal / 23) == 13:
            self.change_bg("\\App_image\\Circle\\circle_1_13.png")
        if time_now // (day_goal / 23) == 14:
            self.change_bg("\\App_image\\Circle\\circle_2.png")
        if time_now // (day_goal / 23) == 15:
            self.change_bg("\\App_image\\Circle\\circle_3.png")
        if time_now // (day_goal / 23) == 16:
            self.change_bg("\\App_image\\Circle\\circle_4.png")
        if time_now // (day_goal / 23) == 17:
            self.change_bg("\\App_image\\Circle\\circle_5.png")
        if time_now // (day_goal / 23) == 18:
            self.change_bg("\\App_image\\Circle\\circle_6.png")
        if time_now // (day_goal / 23) == 19:
            self.change_bg("\\App_image\\Circle\\circle_7.png")
        if time_now // (day_goal / 23) == 20:
            self.change_bg("\\App_image\\Circle\\circle_8.png")
        if time_now // (day_goal / 23) == 21:
            self.change_bg("\\App_image\\Circle\\circle_9.png")
        if time_now // (day_goal / 23) == 22:
            self.change_bg("\\App_image\\Circle\\circle_10.png")

    def change_bg(self, path):
        background_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        big_image_path = background_image_path + path

        bg_image = Image.open(big_image_path)
        bg_resized_image = bg_image.resize(
            (500, 500))
        self.bg_image = ImageTk.PhotoImage(bg_resized_image)

        self.background_label.config(image=self.bg_image)

    def setting_button_click(self):
        settings_windows(self, load_settings(self, "screenshot"), int(load_settings(self, "afk_mode")),
                         int(load_settings(self, "time_remainder")), int(load_settings(self, "week_goal")),
                         int(load_settings(self, "volume")))
