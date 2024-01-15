import asyncio
import os
import random
from datetime import datetime
from time import strftime, gmtime

import tkinter as tk

import pyglet
from pynput import mouse, keyboard

from App_Files.activity_window import open_second_window
from App_Files.afk_detektor import AFKDetector
from App_Files.notification import PopupNotification
from App_Files.play_music import audio_check, audio_download, play_music_switcher
from DataBase.db_logs_operations import session_db_add, get_time_today
from DataBase.db_time_writing import db_time_write
from App_Files.images_controller import take_screenshot
from Settings.app_settings import settings_windows
from Settings.save_settings import load_settings


class TimerApp:
    def __init__(self, root, user_name, user_surname, email):
        self.root = root
        self.email = email
        root.title("Timer")

        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.user_info_label = tk.Label(top_frame, text=f"{user_name} {user_surname}", font=("Arial", 10))
        self.user_info_label.pack(side=tk.LEFT, padx=10, pady=10)

        self.setting_button = tk.Button(top_frame, text="Settings", command=self.setting_button_click)
        self.setting_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.link_button = tk.Button(self.root, text="Activity this week", relief="flat",
                                     command=self.open_second_window_wrapper)
        self.link_button.pack()

        self.link_button.bind("<Enter>", self.on_enter)
        self.link_button.bind("<Leave>", self.on_leave)

        self.check_audio()

        self.time_label = tk.Label(root, text="00:00:00", font=("Arial", 30))
        self.time_label.pack()

        self.start_button = tk.Button(root, text="GO", command=self.start_timer)
        self.start_button.pack()

        self.pause_button = tk.Button(root, text="PAUSE", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.pack()

        # Customize settings
        self.screenshot = load_settings(self, "screenshot")
        self.afk_mode = int(load_settings(self, "afk_mode"))
        self.time_remainder = int(load_settings(self, "time_remainder")) * 60

        # Time settings
        self.now = datetime.now()
        self.current_hour = self.now.strftime("%H:%M:%S")

        self.current_time = self.now.date()

        self.session_time = 0

        # General settings
        self.running = False
        self.elapsed_time = get_time_today(self.email, self.current_time)
        self.time_last_break = 0
        self.next_notification_time = self.time_remainder
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.display_time()

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

    def check_playback(self):
        if self.music_player is not None:
            if self.music_player.time >= self.music_player.source.duration:
                print("End of song, playing again")
                self.position = 0
                self.music_player.seek(self.position)
                self.music_player.play()
        self.root.after(100, self.check_playback)

    def check_audio(self):
        if audio_check(self):
            self.music = tk.Label(self.root, text="Play", fg="black", cursor="hand2")
            self.music.bind("<Button-1>", lambda event: play_music_switcher(self))
            self.music.bind("<Enter>", lambda event, label=self.music: label.config(fg="blue"))
            self.music.bind("<Leave>", lambda event, label=self.music: label.config(fg="black"))
            self.music.pack()
        else:
            self.music = tk.Label(self.root, text="music", fg="black", cursor="hand2")
            self.music.bind("<Enter>", lambda event, label=self.music: label.config(fg="blue"))
            self.music.bind("<Leave>", lambda event, label=self.music: label.config(fg="black"))
            self.music.bind("<Button-1>", lambda event: audio_download(self))
            self.music.pack()

    def on_enter(self, event):
        self.link_button.config(fg="red")

    def on_leave(self, event):
        self.link_button.config(fg="black")

    def open_second_window_wrapper(self):
        open_second_window(self)

    def random_picture(self):
        min_val = 1000 * 60 * 15
        max_val = 1000 * 60 * 25
        interval = random.randint(min_val, max_val)
        self.root.after(interval, self.screenshot_picture)

    def screenshot_picture(self):  # Fix (memory leak)
        if self.running:
            screenshot_path = take_screenshot()

            session_db_add(self.current_time, self.email, self.current_time, self.current_hour, self.session_time,
                           screenshot_path)

            file_path = "App_Files/time_cash.txt"

            if os.path.exists(file_path):
                os.remove(file_path)

            self.session_time = 0

            self.now = datetime.now()
            self.current_time = self.now.date()

            self.current_hour = self.now.strftime("%H:%M:%S")
            self.random_picture()

    def save_time(self):
        hours, remainder = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        db_time_write(hours, minutes, seconds, self.email)

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_timer()
            self.start_button['state'] = tk.DISABLED
            self.pause_button['state'] = tk.NORMAL

            self.now = datetime.now()

            self.current_time = self.now.date()

            self.current_hour = self.now.strftime("%H:%M:%S")

            self.random_picture()

    def pause_timer(self):
        self.save_time()
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED

        session_db_add(self.current_time, self.email, self.current_time, self.current_hour, self.session_time,
                       "None")

        file_path = "App_Files/time_cash.txt"

        if os.path.exists(file_path):
            os.remove(file_path)

        self.session_time = 0

    def temporary_pause_timer(self):
        self.save_time()
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED
        self.wait_for_activity_to_resume_timer()

    def on_close(self):
        self.save_time()
        self.root.destroy()

    def wait_for_activity_to_resume_timer(self):
        if not self.afk_detector.is_afk():
            PopupNotification(self.root, f"Welcome back!\n You have been offline for {self.aft_timer}", 2).show()
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
            self.elapsed_time += 1
            self.display_time()
            time_string = strftime('%H:%M:%S', gmtime(self.elapsed_time))
            self.time_label.config(text=time_string)

            if self.afk_detector.is_afk():
                PopupNotification(self.root, "You are AFK.", 2).show()
                self.temporary_pause_timer()

            self.next_notification_time -= 1
            if self.next_notification_time <= 0:
                PopupNotification(self.root, "Time for a break!", 2).show()
                print(self.time_remainder)
                self.next_notification_time = self.time_remainder

            if self.elapsed_time % 1 == 0:  # Check every 10 seconds and save time and DB
                self.current_time = datetime.now().date()
                with open("App_Files/time_cash.txt", "w") as file:
                    file.write(
                        str(self.current_time) + "|" + str(self.email) + "|" + str(self.current_time) + "|" + str(
                            self.current_hour) + "|" + str(self.session_time) + "|" + "None")
                    print(self.session_time)

            self.session_time += 1

            print(self.session_time, self.session_time)
            self.root.after(1000, self.update_timer)

    def setting_button_click(self):
        settings_windows(self, load_settings(self, "screenshot"), int(load_settings(self, "afk_mode")),
                         int(load_settings(self, "time_remainder")))

