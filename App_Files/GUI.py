import os
import tkinter as tk
from PIL import Image, ImageTk


def popup_notification(message, time_to_fade):
    fade_duration = 1
    background_image_path = "\\App_image\\notification_section_bg.png"
    abs_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + background_image_path

    popup_window = tk.Toplevel()
    popup_window.overrideredirect(True)
    popup_window.attributes("-topmost", True)

    screen_width = popup_window.winfo_screenwidth()
    screen_height = popup_window.winfo_screenheight()

    window_width = 330
    window_height = 150

    x = screen_width - window_width
    y = screen_height - window_height

    popup_window.geometry(f'{window_width}x{window_height}+{x - 10}+{y - 10}')

    image = Image.open(abs_image_path)
    resized_image = image.resize((window_width, window_height))
    tk_image = ImageTk.PhotoImage(resized_image)

    canvas = tk.Canvas(popup_window, width=window_width, height=window_height)
    canvas.pack(fill="both", expand=True)

    canvas.background_image = tk_image
    canvas.create_image(window_width / 2, window_height / 2, image=canvas.background_image)

    font = ("Arial", 10)
    canvas.create_text(window_width / 2, window_height * 0.50, text=message, fill="black", font=font)

    def fade_away():
        alpha = popup_window.attributes("-alpha")
        if alpha > 0:
            alpha -= (1 / (fade_duration * 1000 / time_to_fade))
            popup_window.attributes("-alpha", alpha)
            popup_window.after(time_to_fade, fade_away)
        else:
            popup_window.destroy()

    popup_window.after(time_to_fade * 1000, fade_away)

