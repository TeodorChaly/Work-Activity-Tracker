from datetime import timedelta

from DataBase.db_connection import create_db_connection


def session_db_add(current_day, gmail, data, start_time, time, screenshot_path):
    connection = create_db_connection()

    query = "SELECT id FROM users WHERE email = %s;"
    cursor = connection.cursor()

    cursor.execute(query, (gmail,))
    user_id = cursor.fetchone()

    if user_id:
        user_id = user_id[0]
    else:
        print("False")

    query = """
    INSERT INTO logs_table (user_id, data, start_time, time, screenshot_path)
    VALUES (%s, %s, %s, %s, %s);
    """
    try:
        # print(data - timedelta(days=2))
        cursor.execute(query, (user_id, data, start_time, time, screenshot_path))
        connection.commit()
        print(f"{user_id} with email {gmail} added to logs_table")
        get_time_today(gmail, current_day)
    except Exception as e:  # No connection with wifi
        print(e)


def get_time_today(gmail, today_date):
    connection = create_db_connection()

    query = "SELECT id FROM users WHERE email = %s;"
    cursor = connection.cursor()

    cursor.execute(query, (gmail,))
    user_id = cursor.fetchone()

    if user_id:
        user_id = user_id[0]
    else:
        print("False")

    query = "SELECT time FROM logs_table WHERE user_id = %s AND data = %s;"
    cursor = connection.cursor()

    cursor.execute(query, (user_id, today_date))
    time = cursor.fetchall()
    total_time = 0

    if time:
        for time_minute in time:
            total_time += time_minute[0]
        return total_time
        # set_goals()

    else:
        return 0

# def set_goals():


# get_time_today("tc00121@rvt.lv", "2024-01-04")
