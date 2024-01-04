import json
import os
from datetime import datetime, timedelta


def check_last_visit(last_visit_date):
    current_date = load_last_day()
    last_visit_date = last_visit_date
    print(current_date, last_visit_date)
    days_absent = (current_date - last_visit_date).days

    if days_absent == 0:
        print("Today")
        save_last_day()
    elif days_absent < -7:
        print("Last seen more than a week")  # Remainder - delete today time
    elif 0 > days_absent > -7:
        print(f"Last seen {abs(days_absent)} days before.")  # Remainder - delete today time
    else:
        print("-")


def load_last_day():
    with open("Time_Activity/last_seen.json", "r") as file:
        data = json.load(file)
        last_visit_date_str = data["last-time-online"]

    last_visit_date = datetime.strptime(last_visit_date_str, "%Y-%m-%d").date()
    return last_visit_date


def save_last_day():
    current_date = datetime.now().date()
    last_seen_info = {
        "last-time-online": str(current_date),
    }
    if not os.path.exists("Time_Activity"):
        os.makedirs("Time_Activity")

    with open("Time_Activity/last_seen.json", "w") as file:
        json.dump(last_seen_info, file)
