import tkinter as tk


class Pop:
    def __init__(self, root, message, time=2):
        if time == 0:
            self.top = tk.Toplevel(root)
            self.top.overrideredirect(True)
            self.top.attributes('-topmost', True)

            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            window_width = 200
            window_height = 100
            x = screen_width - window_width
            y = screen_height - window_height
            self.top.geometry(f'{window_width}x{window_height}+{x}+{y}')

            tk.Label(self.top, text=message, font=("Arial", 10)).pack(fill='both', expand=True)
        else:
            self.top = tk.Toplevel(root)
            self.top.overrideredirect(True)
            self.top.attributes('-topmost', True)

            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            window_width = 200
            window_height = 100
            x = screen_width - window_width
            y = screen_height - window_height
            self.top.geometry(f'{window_width}x{window_height}+{x}+{y}')

            tk.Label(self.top, text=message, font=("Arial", 10)).pack(fill='both', expand=True)
            self.top.after(1000 * time, self.top.destroy)

    def show(self):
        pass
