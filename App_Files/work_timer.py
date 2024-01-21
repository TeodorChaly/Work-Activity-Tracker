import os
import random
from datetime import datetime
from time import strftime, gmtime

import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
from pynput import mouse, keyboard

from App_Files.GUI import popup_notification
from App_Files.activity_window import open_second_window
from App_Files.afk_detektor import AFKDetector
from App_Files.play_music import audio_check, audio_download, play_music_switcher
from DataBase.db_logs_operations import session_db_add, get_time_today
from DataBase.db_time_writing import db_time_write
from App_Files.images_controller import take_screenshot
from Settings.app_settings import settings_windows
from Settings.save_settings import load_settings


class TimerApp:
    def __init__(self, root, user_name, user_surname, email):
        background_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        big_image_path = background_image_path + "\\App_image\\circle.png"
        play_img_path = background_image_path + "\\App_image\\play.png"
        pause_img_path = background_image_path + "\\App_image\\stop.png"

        bg_image = Image.open(big_image_path)
        bg_resized_image = bg_image.resize(
            (500, 500))
        self.bg_image = ImageTk.PhotoImage(bg_resized_image)

        self.background_label = tk.Label(root, image=self.bg_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.root = root
        self.email = email
        root.title("Timer")

        root.geometry("500x500")
        root.resizable(False, False)
        root.configure(bg="white")

        background_color = "white"

        # Customize settings
        self.screenshot = load_settings(self, "screenshot")
        self.afk_mode = int(load_settings(self, "afk_mode"))
        self.week_goal = int(load_settings(self, "week_goal"))
        self.time_remainder = int(load_settings(self, "time_remainder")) * 60

        # Time settings
        self.now = datetime.now()
        self.current_hour = self.now.strftime("%H:%M:%S")
        self.session_time = 0
        self.current_time = self.now.date()
        self.elapsed_time = get_time_today(self.email, self.current_time)
        change = self.week_goal * 60 // 7
        self.hours, self.remainder = divmod(change, 60)

        # top_frame = tk.Frame(root)
        # top_frame.pack(side=tk.TOP, fill=tk.X)
        #
        # self.user_info_label = tk.Label(top_frame, text=f"{user_name} {user_surname}", font=("Arial", 10))
        # self.user_info_label.pack(side=tk.LEFT, padx=10, pady=10)
        #
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

        # self.start_button = tk.Button(root, text="GO", command=self.start_timer, bg=background_color,
        #                               activebackground=background_color)
        # self.start_button.place(x=170, y=100)
        #
        # self.pause_button = tk.Button(root, text="PAUSE", command=self.pause_timer, state=tk.DISABLED,
        #                               bg=background_color, activebackground=background_color)
        # self.pause_button.place(x=200, y=100)

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

    def random_picture(self):
        min_val = 1000 * 10 * 60
        max_val = 1000 * 25 * 60
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
            popup_notification("Screenshot taken", 2)

    def save_time(self):
        hours, remainder = divmod(self.elapsed_time, 3600)
        print(hours, remainder)
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
            popup_notification(f"Welcome back!\n You have been offline for {self.aft_timer}", 2)

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
                popup_notification("You are AFK.", 2)
                self.temporary_pause_timer()

            self.next_notification_time -= 1
            if self.next_notification_time <= 0:
                popup_notification("Time for a break!", 2)
                # PopupNotification(self.root, "Time for a break!", 2).show()
                # print(self.time_remainder)
                self.next_notification_time = self.time_remainder

            if self.elapsed_time % 1 == 0:  # Check every 10 seconds and save time and DB
                self.current_time = datetime.now().date()
                with open("App_Files/time_cash.txt", "w") as file:
                    file.write(
                        str(self.current_time) + "|" + str(self.email) + "|" + str(self.current_time) + "|" + str(
                            self.current_hour) + "|" + str(self.session_time) + "|" + "None")
                    # print(self.session_time)

            self.session_time += 1

            self.goal_label.config(
                text=f"Goal(h)\n{round((self.elapsed_time // 60) / 60, 2)}/{self.hours:1}.{self.remainder // 6}")

            # print(self.session_time, self.session_time)
            self.root.after(1000, self.update_timer)

    def image_progress_changer(self):
        # week_goal round to int
        time_now = self.elapsed_time // 60
        day_goal = self.hours * 60 + self.remainder

        print(day_goal, time_now, day_goal / 10 )

        if time_now >= day_goal:
            self.change_bg("\\App_image\\Circle\\circle_10.png")
            popup_notification("Your reached day's goal!", 2)
        if time_now // (day_goal / 10) == 0:
            self.change_bg("\\App_image\\Circle\\circle_0.png")
        # If 1/10 of week_goal
        if time_now // (day_goal / 10) == 1:
            self.change_bg("\\App_image\\Circle\\circle_1.png")
        # If 2/10 of week_goal
        if time_now // (day_goal / 10) == 2:
            self.change_bg("\\App_image\\Circle\\circle_2.png")
        # If 3/10 of week_goal
        if time_now // (day_goal / 10) == 3:
            self.change_bg("\\App_image\\Circle\\circle_3.png")
        # If 4/10 of week_goal
        if time_now // (day_goal / 10) == 4:
            self.change_bg("\\App_image\\Circle\\circle_4.png")
        # If 5/10 of week_goal
        if time_now // (day_goal / 10) == 5:
            self.change_bg("\\App_image\\Circle\\circle_5.png")
        # If 6/10 of week_goal
        if time_now // (day_goal / 10) == 6:
            self.change_bg("\\App_image\\Circle\\circle_6.png")
        # If 7/10 of week_goal
        if time_now // (day_goal / 10) == 7:
            self.change_bg("\\App_image\\Circle\\circle_7.png")
        # If 8/10 of week_goal
        if time_now // (day_goal / 10) == 8:
            self.change_bg("\\App_image\\Circle\\circle_8.png")
        # If 9/10 of week_goal
        if time_now // (day_goal / 10) == 9:
            self.change_bg("\\App_image\\Circle\\circle_9.png")
        # If 10/10 of week_goal
        if time_now // (day_goal / 10) == 10:
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
                         int(load_settings(self,
                                           "time_remainder")), int(load_settings(self,
                                                                                 "week_goal")))  # , int(self, "today_goal"), int(self, "week_goal")
