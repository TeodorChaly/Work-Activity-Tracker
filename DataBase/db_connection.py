import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os


def create_db_connection():
    load_dotenv(dotenv_path="Env_Settings/.env")
    connection = None
    try:
        connection = mysql.connector.connect(
            host=f'{os.getenv("DB_HOST")}',
            user=f'{os.getenv("DB_USER")}',
            passwd=f'{os.getenv("DB_PASSWORD")}',
            database=f'{os.getenv("DB_NAME")}'
        )
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection
