import os
import re

import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime, timedelta

from DataBase.db_connection import create_db_connection


def aggregate_activity_by_hour(data):
    activity_by_date_hour = {}

    for item in data:
        start_time = datetime.combine(item[2], datetime.min.time()) + item[3]
        end_time = start_time + timedelta(seconds=item[4])

        while start_time < end_time:
            next_hour = start_time.replace(minute=0, second=0) + timedelta(hours=1)
            overlap = min(end_time, next_hour) - start_time

            date_key = start_time.strftime('%Y-%m-%d')
            hour_key = start_time.strftime('%H:00')
            if date_key not in activity_by_date_hour:
                activity_by_date_hour[date_key] = {}
            activity_by_date_hour[date_key][hour_key] = activity_by_date_hour[date_key].get(hour_key,
                                                                                            0) + overlap.seconds

            start_time = next_hour

    return activity_by_date_hour


def open_second_window(self):
    self.second_window = tk.Toplevel(self.root)
    self.second_window.title(f"Activity")  # of {self.user_name} 7 days)

    ico = Image.open('App_image/Logo_Small.ico')
    photo_1 = ImageTk.PhotoImage(ico)
    self.second_window.wm_iconphoto(False, photo_1)

    background_image_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    big_image_path = background_image_path + "\\App_image\\bg_activity.png"

    window_width = int(500)
    window_height = int(800)
    position_right = int(self.root.winfo_x() + (self.root.winfo_width() / 2 - window_width / 2))
    position_down = int(self.root.winfo_y() + (self.root.winfo_height() / 2 - window_height / 2))
    self.second_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down + 150}")
    self.second_window.grab_set()

    self.second_window.resizable(False, False)

    self.canvas = tk.Canvas(self.second_window, width=window_width, height=window_height)
    self.canvas.pack(fill="both", expand=True)

    background_image_path = os.path.join(big_image_path)
    bg_image = Image.open(background_image_path)
    bg_image = bg_image.resize((window_width, window_height))
    bg_photo = ImageTk.PhotoImage(bg_image)

    self.canvas.create_image(0, 0, anchor="nw", image=bg_photo)
    self.canvas.image = bg_photo

    background_color = '#545454'

    text_widget = tk.Text(self.second_window, wrap="word", state="disabled", bg=background_color, borderwidth=0,
                          highlightthickness=0)
    text_widget.place(x=60, y=160, width=window_width - 150, height=window_height - 290)

    def on_date_hover(event, date):
        text_widget.tag_configure(f"hover_{date}", foreground="white")
        text_widget.tag_add(f"hover_{date}", f"date_{date.replace(':', '_').replace('-', '_')}.first",
                            f"date_{date.replace(':', '_').replace('-', '_')}.last")

    def on_date_leave(event, date):
        text_widget.tag_configure(f"hover_{date}", foreground="black")
        text_widget.tag_remove(f"hover_{date}", f"date_{date.replace(':', '_').replace('-', '_')}.first",
                               f"date_{date.replace(':', '_').replace('-', '_')}.last")

    raw_data = db_activity_of_last_days(self)
    aggregated_data = aggregate_activity_by_hour(raw_data)

    total_week_seconds = sum(sum(hours.values()) for hours in aggregated_data.values())

    text = f"Total time per week\n          {data_formatting(total_week_seconds)}"
    self.canvas.create_text(window_width / 2, 39, text=text, font=("Arial", 13, "bold"), fill="black", anchor="n")

    row_num = 2

    for date, hours in sorted(aggregated_data.items(), reverse=True):
        text_widget.configure(state="normal")

        total_day_seconds = sum(hours.values())

        date_tag = f"date_{date.replace(':', '_').replace('-', '_')}"
        try:
            text_widget.tag_bind(date_tag, "<Enter>", lambda e, d=date: on_date_hover(e, d))
        except Exception as e:
            print("Next")
        try:
            text_widget.tag_bind(date_tag, "<Leave>", lambda e, d=date: on_date_leave(e, d))
        except Exception as e:
            print("Next")

        text_widget.insert("end",
                           f"  {date} ({divmod(total_day_seconds, 60)[0]} min, {divmod(total_day_seconds, 60)[1]}"
                           f" sec)\n",
                           date_tag)

        text_widget.tag_bind(date_tag, "<Button-1>",
                             lambda e, d=date: show_date_info(e, d, self.email))

        for hour, duration in sorted(hours.items()):
            minutes, seconds = divmod(duration, 60)
            info_text = f"   {hour} - {minutes} min and {seconds} sec\n"
            text_widget.insert("end", info_text)

        text_widget.insert("end", f"\n")

        text_widget.configure(state="disabled")
        row_num += 1

    text_widget.tag_configure("date", font=("Arial", 14, "bold"))
    text_widget.tag_configure("total_week", font=("Arial", 12, "bold"))

    close_button = tk.Button(self.second_window, text="Close", command=self.second_window.destroy, pady=10,
                             font=("Arial", 14, "bold"), fg="white", background="#a6a6a6", borderwidth=0,
                             highlightthickness=0)
    close_button.place(x=window_width / 2 - 50, y=window_height - 67, width=100, height=40)

    text_widget.config(state="disabled")

    def show_date_info(event, data, email):
        self.canvas.forget()

        screen_width = self.second_window.winfo_screenwidth()
        screen_height = self.second_window.winfo_screenheight()
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.75)

        x = (screen_width // 2) - (window_width // 2)
        y = 0

        size_x = window_width
        size_y = window_height

        self.second_window.geometry(f"{size_x}x{size_y}+{position_right}+{position_down + 150}")
        self.second_window.title("Activity Info")

        result = day_info_db(data, email)
        activity_data = remake(result)

        canvas = tk.Canvas(self.second_window)
        scrollbar = tk.Scrollbar(self.second_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        def _configure_canvas(event):
            canvas_width = event.width
            canvas.itemconfig(frame_id, width=canvas_width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind('<Configure>', _configure_canvas)

        frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

        date_label = tk.Label(scrollable_frame, text=f"Info about: {data}", font=("Arial", 14, "bold"))
        date_label.pack()

        canvas.pack(side="bottom", fill="both", expand=True)
        scrollbar.place(x=window_width - 20, y=10, width=20, height=window_height - 60)

        screenshots = []

        for hour, data in activity_data.items():
            total_time_seconds = data["total_seconds"]
            total_time_label = tk.Label(scrollable_frame,
                                        text=f"Hour: {hour.strftime('%H:%M:%S')} -"
                                             f" Total time: {data_formatting(total_time_seconds)}")
            total_time_label.pack()

            for i in data["screenshots"]:
                if i not in screenshots and i is not None:
                    if i != "path/to/screenshots123" and i != "None":
                        screenshots.append(i)

            if screenshots:

                print(screenshots)

                screenshot_frame = tk.Frame(scrollable_frame, highlightthickness=2, highlightbackground="gray")
                screenshot_frame.pack(pady=5, padx=70, fill=tk.BOTH, expand=True)

                for i in range(0, len(screenshots), 3):
                    screenshot_row = screenshots[i:i + 3]
                    screenshot_frame = tk.Frame(scrollable_frame)
                    screenshot_frame.pack()

                    for screenshot_data in screenshot_row:

                        time_match = re.search(r'_(\d{2})(\d{2})\.png$', screenshot_data)
                        if time_match:
                            hour_img, minute_img = time_match.groups()
                            extracted_time = f"{hour_img}"
                        else:
                            extracted_time = "Time not found"

                        if screenshot_data:
                            if str(hour.strftime('%H')) == extracted_time:
                                try:
                                    image = Image.open(screenshot_data)
                                    image.thumbnail((400, 400))
                                    tk_image = ImageTk.PhotoImage(image)

                                    screenshot_img_label = tk.Label(screenshot_frame, image=tk_image)
                                    screenshot_img_label.image = tk_image
                                    screenshot_img_label.pack(side=tk.LEFT)

                                    screenshot_img_label.bind("<Button-1>",
                                                              lambda e, path=screenshot_data: open_image(path))
                                except Exception as e:
                                    pass
                        else:
                            no_screenshot_label = tk.Label(screenshot_frame, text="No screenshot")
                            no_screenshot_label.pack(side=tk.LEFT, padx=5)

            else:
                self.second_window.geometry(f"{500}x{500}+{position_right}+{position_down + 150}")

        new_button = tk.Button(scrollable_frame, text="Back", command=restore_previous_layer)
        new_button.pack(anchor='n', expand=True, pady=10)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.second_window.bind_all("<MouseWheel>", _on_mousewheel)
        self.second_window.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def open_image(image_path):
        image_window = tk.Toplevel()
        image_window.title("Screenshot")

    def restore_previous_layer():
        window_width = int(500)
        window_height = int(800)
        self.second_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down + 150}")

        for widget in self.second_window.winfo_children():
            widget.pack_forget()

        self.canvas.pack(fill="both", expand=True)


def remake(data):
    activity_by_hour = {}

    for item in data:
        start_time = datetime.combine(item[2], datetime.min.time()) + item[3]
        end_time = start_time + timedelta(seconds=item[4])

        while start_time < end_time:
            rounded_hour = start_time.replace(minute=0, second=0)
            next_hour = rounded_hour + timedelta(hours=1)

            overlap_seconds = (min(end_time, next_hour) - start_time).total_seconds()

            if rounded_hour not in activity_by_hour:
                activity_by_hour[rounded_hour] = {"total_seconds": 0, "screenshots": []}

            activity_by_hour[rounded_hour]["total_seconds"] += overlap_seconds
            activity_by_hour[rounded_hour]["screenshots"].extend(item[5:])

            start_time = next_hour

    return activity_by_hour


def data_formatting(data):
    hours, remainder = divmod(data, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


def db_activity_of_last_days(self):
    connection = create_db_connection()

    query = "SELECT id FROM users WHERE email = %s;"
    cursor = connection.cursor()

    cursor.execute(query, (self.email,))
    user_id = cursor.fetchone()

    if user_id:
        user_id = user_id[0]
    else:
        print("False")

    cursor = connection.cursor()

    seven_days_ago = datetime.now() - timedelta(days=7)

    print(user_id)
    query = """
        SELECT * FROM logs_table
        WHERE user_id = %s AND data >= %s
        ORDER BY data DESC, start_time DESC
        """
    cursor.execute(query, (user_id, seven_days_ago.date()))

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return results


def day_info_db(date, email):
    connection = create_db_connection()

    query = "SELECT id FROM users WHERE email = %s;"
    cursor = connection.cursor()
    cursor.execute(query, (email,))
    user_id = cursor.fetchone()

    if user_id:
        user_id = user_id[0]
    else:
        print("User not found")

    cursor = connection.cursor()

    query = """
        SELECT * FROM logs_table
        WHERE user_id = %s AND data = %s
        ORDER BY start_time ASC
        """
    cursor.execute(query, (user_id, date))

    results = cursor.fetchall()
    cursor.close()
    connection.close()

    return results
