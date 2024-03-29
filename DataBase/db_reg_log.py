import bcrypt

from mysql.connector import Error
from DataBase.db_connection import create_db_connection



def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def register_user(email, first_name, last_name, password):
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        query = "INSERT INTO users (email, first_name, last_name, password_hash) VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(query, (email, first_name, last_name, hashed_password))
            connection.commit()
            print("User registered successfully")
            return True
        except Error as e:
            print(f"The error '{e}' occurred")
            return False
    except Error as e:
        print(f"The error '{e}' occurred")
        return False
    finally:
        cursor.close()


def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode(), hashed_password.encode())


def login_user(email, password):
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        query = "SELECT password_hash, first_name, last_name FROM users WHERE email = %s "
        try:
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            try:
                print(result[0], result[1])
            except TypeError:
                print("User not found")
                return False, None, None

            if result and check_password(result[0], password):
                return True, result[1], result[2]
            else:
                print("Wrong password")
                return False, None, None
        except Error as e:
            print(f"The error '{e}' occurred")

        return False, None, None
    except Error as e:
        print(f"The error '{e}' occurred")
        return False, None, None
    finally:
        cursor.close()
