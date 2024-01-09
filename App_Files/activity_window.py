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
            activity_by_date_hour[date_key][hour_key] = activity_by_date_hour[date_key].get(hour_key, 0) + overlap.seconds

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

    # data = db_activity_of_last_days(self)
    # data.sort(key=lambda x: x[2], reverse=True)
    #
    # current_date = None
    # for item in data:
    #     # Преобразуем продолжительность в формат ЧЧ:ММ:СС
    #     duration_formatted = data_formatting(item[3].total_seconds())
    #     until_formatted = data_formatting(item[3].total_seconds() + item[4])
    #
    #     if current_date != item[2]:
    #         current_date = item[2]
    #         text_widget.configure(state="normal")
    #         text_widget.insert("end", f"{current_date}\n", "date")
    #         text_widget.configure(state="disabled")
    #
    #     info_text = f"Duration: {duration_formatted} - {until_formatted} , Number: {item[4]}, Screenshot: {item[5]}\n"
    #     text_widget.configure(state="normal")
    #     text_widget.insert("end", info_text)
    #     text_widget.configure(state="disabled")

    raw_data = db_activity_of_last_days(self)
    aggregated_data = aggregate_activity_by_hour(raw_data)

    for date, hours in sorted(aggregated_data.items(), reverse=True):
        text_widget.configure(state="normal")
        text_widget.insert("end", f"{date}\n", "date")
        for hour, duration in sorted(hours.items()):
            info_text = f"  {hour} - {duration} (sec)\n"
            text_widget.insert("end", info_text)
        text_widget.configure(state="disabled")

    text_widget.tag_configure("date", font=("Arial", 14, "bold"))


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
