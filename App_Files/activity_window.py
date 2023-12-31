import tkinter as tk
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
    self.second_window.title("Second Window")

    scrollbar = tk.Scrollbar(self.second_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(self.second_window, wrap="word", yscrollcommand=scrollbar.set, state="disabled")
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)

    def on_date_hover(event, date):
        text_widget.tag_configure(f"hover_{date}", foreground="blue")  # Измените цвет на желаемый
        text_widget.tag_add(f"hover_{date}", f"date_{date.replace(':', '_').replace('-', '_')}.first",
                            f"date_{date.replace(':', '_').replace('-', '_')}.last")

    def on_date_leave(event, date):
        text_widget.tag_configure(f"hover_{date}", foreground="black")  # Верните обычный цвет
        text_widget.tag_remove(f"hover_{date}", f"date_{date.replace(':', '_').replace('-', '_')}.first",
                               f"date_{date.replace(':', '_').replace('-', '_')}.last")

    raw_data = db_activity_of_last_days(self)
    aggregated_data = aggregate_activity_by_hour(raw_data)

    total_week_seconds = sum(sum(hours.values()) for hours in aggregated_data.values())

    text_widget.configure(state="normal")
    text_widget.insert("end", f"Total time per week: {data_formatting(total_week_seconds)}\n", "total_week")

    for date, hours in sorted(aggregated_data.items(), reverse=True):
        text_widget.configure(state="normal")

        total_day_seconds = sum(hours.values())

        date_tag = f"date_{date.replace(':', '_').replace('-', '_')}"
        text_widget.tag_bind(date_tag, "<Enter>", lambda e, d=date: on_date_hover(e, d))
        text_widget.tag_bind(date_tag, "<Leave>", lambda e, d=date: on_date_leave(e, d))
        text_widget.insert("end",
                           f"{date} ({divmod(total_day_seconds, 60)[0]} minutes and {divmod(total_day_seconds, 60)[1]}"
                           f" seconds)\n",
                           date_tag)

        text_widget.tag_bind(date_tag, "<Button-1>", lambda e, d=date: on_date_click(e, d))

        for hour, duration in sorted(hours.items()):
            minutes, seconds = divmod(duration, 60)
            info_text = f" {hour} - {minutes} minutes and {seconds} seconds\n"
            text_widget.insert("end", info_text)

        text_widget.configure(state="disabled")

    text_widget.tag_configure("date", font=("Arial", 14, "bold"))
    text_widget.tag_configure("total_week", font=("Arial", 12, "bold"))


def on_date_click(event, date):
    print(f"Chosen date: {date}")


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
