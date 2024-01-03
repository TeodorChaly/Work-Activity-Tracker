import json
import os

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


def setting_check():
    default_settings = {
        "screenshot": True,
        "time_remainder": "5",
        "afk_mode": "10"
    }

    if not os.path.exists(user_path):
        with open("Settings/user_settings.json", "w") as file:
            json.dump(default_settings, file)
