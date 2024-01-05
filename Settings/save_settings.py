import json
import os

from DataBase.db_logs_operations import session_db_add

user_path = "Settings/user_settings.json"


def save_settings(self):
    screenshot = self.screenshot_var.get()
    afk = self.afk_mode_var.get()
    notification = self.time_remainder_var.get()

    settings_data = {
        "screenshot": screenshot,
        "time_remainder": notification,
        "afk_mode": afk,
    }

    with open(user_path, "w") as file:
        json.dump(settings_data, file)

    self.screenshot = screenshot
    self.time_remainder = int(notification)
    self.afk_mode = int(afk)
    self.next_notification_time = self.time_remainder * 60


def load_settings(self, element_to_find):
    try:
        with open(user_path, "r") as file:
            settings_data = json.load(file)
            result = settings_data[element_to_find]
            return result
    except FileNotFoundError:
        print("File not found")


def pre_start_configuration():
    default_settings = {
        "screenshot": True,
        "time_remainder": "5",
        "afk_mode": "10"
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

            session_db_add(current_time, email, current_time, current_hour, session_time, screen_shot_path)

        os.remove("App_Files/time_cash.txt")