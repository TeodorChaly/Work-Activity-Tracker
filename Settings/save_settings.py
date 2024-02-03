import json
import os
import shutil

from datetime import datetime, timedelta
from pynput import mouse, keyboard

from App_Files.afk_detektor import AFKDetector
from DataBase.db_logs_operations import session_db_add

user_path = "Settings/user_settings.json"


def save_settings(self):
    screenshot = self.screenshot_var.get()
    afk = self.afk_mode_var.get()
    notification = self.time_remainder_var.get()
    week_goal = self.week_goal_var.get()
    volume = self.volume_var.get()

    settings_data = {
        "screenshot": screenshot,
        "time_remainder": notification,
        "afk_mode": afk,
        "week_goal": week_goal,
        "volume": volume,
    }

    with open(user_path, "w") as file:
        json.dump(settings_data, file)

    self.screenshot = screenshot
    self.time_remainder = int(notification) * 60
    self.afk_mode = int(afk)
    # self.week_goal_var = int(week_goal)
    self.week_goal = int(week_goal)

    self.afk_detector = AFKDetector(int(self.afk_mode))
    mouse_listener = mouse.Listener(on_move=self.afk_detector.update_last_action_time,
                                    on_click=self.afk_detector.update_last_action_time)
    keyboard_listener = keyboard.Listener(on_press=self.afk_detector.update_last_action_time)
    mouse_listener.start()
    keyboard_listener.start()
    self.next_notification_time = self.time_remainder
    print("Change", self.time_remainder* 60, self.next_notification_time)
    change = self.week_goal * 60 // 7
    self.hours, self.remainder = divmod(change, 60)
    self.goal_label.config(
        text=f"Goal(h)\n{round((self.elapsed_time // 60) / 60, 2)}/{self.hours:}.{self.remainder // 6}")
    try:
        self.music_player.volume = volume / 10
    except AttributeError:
        print("Music not playing")
        pass


def load_settings(self, element_to_find):
    try:
        with open(user_path, "r") as file:
            settings_data = json.load(file)
            # print(settings_data)
            result = settings_data[element_to_find]
            return result
    except FileNotFoundError:
        print("File not found")


def pre_start_configuration():
    clearing_screenshots()

    default_settings = {
        "screenshot": True,
        "time_remainder": "5",
        "afk_mode": "10",
        "week_goal": "14",
    }

    if not os.path.exists(user_path):
        with open("Settings/user_settings.json", "w") as file:
            json.dump(default_settings, file)
    if not os.path.exists("App_Files/time_cash.txt"):
        pass
    else:
        with open("App_Files/time_cash.txt", "r") as file:
            data_string = file.read()
            data = data_string.split("|")
            current_time = data[0]
            email = data[1]
            current_hour = data[3]
            session_time = data[4]
            screen_shot_path = data[5]

            session_db_add(None, current_time, email, current_time, current_hour, session_time, screen_shot_path)

        os.remove("App_Files/time_cash.txt")


def clearing_screenshots():
    screenshots_folder = 'Images'
    cleared_folder = os.path.join(screenshots_folder, 'clear')
    os.makedirs(cleared_folder, exist_ok=True)  # Создаем папку, если она еще не существует

    one_week_ago = datetime.now() - timedelta(days=8)

    for filename in os.listdir(screenshots_folder):
        if filename.startswith("screenshot_") and filename.endswith(".png"):
            timestamp_str = filename.split("_")[1] + "_" + filename.split("_")[2].split(".")[0]
            screenshot_datetime = datetime.strptime(timestamp_str, '%Y%m%d_%H%M')

            if screenshot_datetime < one_week_ago:
                source_path = os.path.join(screenshots_folder, filename)
                destination_path = os.path.join(cleared_folder, filename)

                shutil.move(source_path, destination_path)
