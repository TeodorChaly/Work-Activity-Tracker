from PIL import ImageGrab
from datetime import datetime
import os


def take_screenshot():
    now = datetime.now()
    filename = now.strftime("%M_%H_%d_%m_%Y") + ".png"

    screenshot = ImageGrab.grab()
    screenshot.save(filename)

    print(f"Screenshot saved as {filename}")


if not os.path.exists('Images'):
    os.makedirs('Images')

os.chdir('Images')

take_screenshot()
