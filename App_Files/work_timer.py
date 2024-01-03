import random
from datetime import datetime
from time import strftime, gmtime

import tkinter as tk
from pynput import mouse, keyboard

from App_Files.afk_detektor import AFKDetector
from App_Files.notification import PopupNotification
from App_Files.time_checker import check_last_visit
from DataBase.db_time_writing import db_time_write, get_time_from_db
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

        self.email_label = tk.Label(root, text=email, font=("Arial", 10))
        self.email_label.pack()

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
        print(self.screenshot, self.afk_mode, self.time_remainder)

        self.running = False
        self.elapsed_time = get_time_from_db(email)
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

        self.last_visit_date = datetime.now().date()  # Change last time
        check_last_visit(self)

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

    def pause_timer(self):
        self.save_time()
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED

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
            print(f"You have been offline {self.aft_timer}")
            self.aft_timer = 0
            self.start_timer()
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
            TIME_REMAINDER = 1 * 60  # Change time remainder (random)
            time_string = strftime('%H:%M:%S', gmtime(self.elapsed_time))
            self.time_label.config(text=time_string)

            # print(self.elapsed_time - self.time_last_break, TIME_REMAINDER)
            # if self.elapsed_time - self.time_last_break >= TIME_REMAINDER:
            #     PopupNotification(self.root, "It is time for little break!").show()
            #     self.time_last_break = self.elapsed_time

            if self.afk_detector.is_afk():
                self.temporary_pause_timer()

            self.next_notification_time -= 1
            if self.next_notification_time <= 0:
                PopupNotification(self.root, "Time for a break!").show()
                self.next_notification_time = self.time_remainder

            print(f"AFK: {self.afk_mode}, Notification: {self.next_notification_time}, Screenshot: {self.screenshot}")
            self.root.after(1000, self.update_timer)

    def setting_button_click(self):
        settings_windows(self, load_settings(self, "screenshot"), int(load_settings(self, "afk_mode")),
                         int(load_settings(self, "time_remainder")))

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TimerApp(root)
#     root.mainloop()
