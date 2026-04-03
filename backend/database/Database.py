import mysql.connector  # type: ignore

import utils.config as config  # loads root .env via utils.config


class Database:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host=config.BaseConfig.DATABASE_HOST,
            user=config.BaseConfig.DATABASE_USER,
            password=config.BaseConfig.DATABASE_PASSWORD,
            database=config.BaseConfig.DATABASE_NAME,
            port=config.BaseConfig.DATABASE_PORT,
        )
