from mysql.connector import Error


def db_time_write(self, hours, minutes, seconds, email):
    try:
        # Check time passed
        connection = self.connection

        cursor = connection.cursor()

        total_seconds = hours * 3600 + minutes * 60 + seconds

        query = "UPDATE users SET today_time = %s WHERE email = %s"
        cursor.execute(query, (total_seconds, email))

        connection.commit()
        print(f"Time saved for {email}")

    except Error as e:
        print("Error while connecting to MySQL", e)

    # finally:
    #     if connection.is_connected():
    #         cursor.close()
    #         connection.close()

#
# def get_time_from_db(email):
#     try:
#         connection = create_db_connection()
#         cursor = connection.cursor()
#
#         query = "SELECT today_time FROM users WHERE email = %s"
#         cursor.execute(query, (email,))
#
#         result = cursor.fetchone()
#         if result:
#             return result[0] if result[0] is not None else 0
#         else:
#             return 0
#
#     except Error as e:
#         print("Error while connecting to MySQL", e)
#         return 0
#     #
#     # finally:
#     #     if connection.is_connected():
#     #         cursor.close()
#     #         connection.close()
