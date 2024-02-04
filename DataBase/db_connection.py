import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


def create_db_connection():
    load_dotenv(dotenv_path="Env_Settings/.env")
    connection = None
    try:
        connection = mysql.connector.connect(
            host=f'rayban247.beget.tech',
            user=f'123',
            passwd=f'123',
            database=f'123'
        )
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
