import os
import tkinter as tk
from PIL import Image, ImageTk


def Pop():
    background_image_path = "\App_image\\notification_section_bg.png"
    # Import module
    current_dir = os.path.dirname(__file__)
    abs_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + background_image_path

    # Create a Toplevel window
    popup_window = tk.Toplevel()

    # Уберите верхний таб
    popup_window.overrideredirect(True)

    # Получите размеры экрана
    screen_width = popup_window.winfo_screenwidth()
    screen_height = popup_window.winfo_screenheight()

    # Установите размер окна
    window_width = 200
    window_height = 90

    # Вычислите позицию окна в правом нижнем углу
    x = screen_width - window_width
    y = screen_height - window_height

    # Установите геометрию окна
    popup_window.geometry(f'{window_width}x{window_height}+{x}+{y}')

    # Откройте изображение с использованием PIL
    image = Image.open(abs_image_path)
    image.thumbnail((window_width, window_height))

    # Создайте PhotoImage изображения для использования в tkinter
    tk_image = ImageTk.PhotoImage(image)

    # Создайте фрейм и добавьте на него изображение
    frame = tk.Frame(popup_window)
    frame.pack(fill="both", expand=True)

    # Сохраните ссылку на изображение в переменной, чтобы избежать удаления сборщиком мусора
    label_image = tk_image
    label = tk.Label(frame, image=label_image)
    label.image = label_image
    label.pack(fill="both", expand=True)

    # Запустите mainloop для всплывающего окна
    popup_window.mainloop()