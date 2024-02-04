from mysql.connector import Error


def db_time_write(self, hours, minutes, seconds, email):
    try:
        # Check time passed
        self.connection.ping(reconnect=True, attempts=3, delay=5)
        connection = self.connection

        cursor = connection.cursor()

        total_seconds = hours * 3600 + minutes * 60 + seconds

        query = "UPDATE users SET today_time = %s WHERE email = %s"
        cursor.execute(query, (total_seconds, email))

        connection.commit()
        print(f"Time saved for {email}")

    except Error as e:
        print("Error while connecting to MySQL", e)
