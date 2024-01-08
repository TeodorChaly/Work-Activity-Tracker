import tkinter as tk


def open_second_window(self):
    self.second_window = tk.Toplevel(self.root)
    self.second_window.title("Second Window")

    tk.Label(self.second_window, text="Activity").pack()
