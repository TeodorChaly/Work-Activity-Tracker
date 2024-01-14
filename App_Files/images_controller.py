import pyautogui
from datetime import datetime
import os


def take_screenshot(): # Only one monitor
    folder = 'Images'

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{folder}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M')}.png"

    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

    return filename
