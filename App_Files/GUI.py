import os
import tkinter as tk
from PIL import Image, ImageTk


def popup_notification(message, time):
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

    frame = tk.Frame(popup_window)
    frame.pack(fill="both", expand=True)

    label_image = tk_image
    label = tk.Label(frame, image=label_image)
    label.image = label_image
    label.pack(fill="both", expand=True)

    text_label = tk.Label(frame, text=message, bg="white", fg="black")
    text_label.place(relx=0.5, rely=0.5, anchor='center')

    label_image.image = tk_image

    popup_window.after(time*1000, popup_window.destroy)

    popup_window.mainloop()
