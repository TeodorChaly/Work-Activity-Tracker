import random
import tkinter as tk
from time import strftime, gmtime, time
from App_Files.notification import PopupNotification
from DataBase.db_time_writing import db_time_write, get_time_from_db


class TimerApp:
    def __init__(self, root, user_name, user_surname, email):
        self.root = root
        self.email = email
        root.title("Timer")

        self.user_info_label = tk.Label(root, text=f"{user_name} {user_surname}", font=("Arial", 10))
        self.user_info_label.pack()

        self.email_label = tk.Label(root, text=email, font=("Arial", 10))
        self.email_label.pack()

        self.time_label = tk.Label(root, text="00:00:00", font=("Arial", 30))
        self.time_label.pack()

        self.start_button = tk.Button(root, text="GO", command=self.start_timer)
        self.start_button.pack()

        self.pause_button = tk.Button(root, text="PAUSE", command=self.pause_timer, state=tk.DISABLED)
        self.pause_button.pack()

        self.running = False
        self.elapsed_time = get_time_from_db(email)
        self.time_last_break = 0
        self.next_notification_time = self.get_next_notification_time()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.save_interval = 20 * 60 * 1000
        self.display_time()

    def save_time(self):
        hours, remainder = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        db_time_write(hours, minutes, seconds, self.email)

    def on_close(self):
        self.save_time()
        self.root.destroy()

    def start_timer(self):
        if not self.running:
            self.running = True
            self.update_timer()
            self.start_button['state'] = tk.DISABLED
            self.pause_button['state'] = tk.NORMAL

    def pause_timer(self):
        self.save_time()
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED

    def display_time(self):
        hours, remainder = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.time_label.config(text=time_string)

    def get_next_notification_time(self):
        return random.randint(10 * 60, 25 * 60)  # Random check from 600 to 900 sec

    def show_notification(self):
        PopupNotification(self.root, "Time for a break!").show()

    def update_timer(self):
        if self.running:
            self.elapsed_time += 1
            self.display_time()
            TIME_REMAINDER = 1 * 60  # Change time remainder
            time_string = strftime('%H:%M:%S', gmtime(self.elapsed_time))
            self.time_label.config(text=time_string)

            if self.elapsed_time - self.time_last_break >= TIME_REMAINDER:
                self.show_break_notification()
                self.time_last_break = self.elapsed_time

            self.next_notification_time -= 1
            if self.next_notification_time <= 0:
                self.show_notification()
                self.next_notification_time = self.get_next_notification_time()

            print(self.next_notification_time)
            self.root.after(1000, self.update_timer)

    def show_break_notification(self):
        PopupNotification(self.root, "It is time for little break!").show()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TimerApp(root)
#     root.mainloop()