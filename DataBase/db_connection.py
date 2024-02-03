import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


def create_db_connection():
    load_dotenv(dotenv_path="Env_Settings/.env")
    connection = None
    try:
        connection = mysql.connector.connect(
            host=f'rayban247.beget.tech',
            user=f'rayban247_time',
            passwd=f'123_Pas',
            database=f'rayban247_time'
        )
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
