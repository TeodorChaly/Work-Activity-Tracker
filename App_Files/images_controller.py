import os

import pyautogui

from datetime import datetime

from PIL import ImageGrab
from functools import partial


def take_screenshot():  # Only one monitor
    folder = 'Images'

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{folder}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M')}.png"

    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

    return filename


def take_screenshot_all_monitors():
    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

    folder = 'Images'

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{folder}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M')}.png"

    screenshot = ImageGrab.grab()
    screenshot.save(filename)

    return filename
