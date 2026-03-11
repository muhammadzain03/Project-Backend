import mysql.connector  # type: ignore
from dotenv import load_dotenv
import utils.config as config

load_dotenv()

dbhost = config.BaseConfig.DATABASE_HOST
dbuser = config.BaseConfig.DATABASE_USER
dbpwd  = config.BaseConfig.DATABASE_PASSWORD
dbname = config.BaseConfig.DATABASE_NAME
dbport = config.BaseConfig.DATABASE_PORT

class Database:
    @staticmethod
    def get_connection():
        try:
            conn = mysql.connector.connect(
                host=dbhost,
                user=dbuser,
                password=dbpwd,
                database=dbname,
                port=dbport,
                connection_timeout=5,
            )
            if conn.is_connected():
                return conn
            raise ConnectionError("Database connection failed.")
        except mysql.connector.Error as err:
            raise ConnectionError(f"Connection error: {err}")
