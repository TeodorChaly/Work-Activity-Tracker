from datetime import datetime, timedelta

def check_last_visit(self):
    current_date = datetime.now().date()
    days_absent = (current_date - self.last_visit_date).days
    print(current_date, self.last_visit_date)

    if days_absent > 7:
        print("Больше недели")
    elif 0 < days_absent < 7:
        print(f"Последний раз был {days_absent} дней назад")
    else:
        print("Current day")
