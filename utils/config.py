import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv()


class BaseConfig:
    GCP_BUCKET = os.environ.get("GCP_BUCKET")

    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_USER = os.environ.get("DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    DATABASE_PORT = int(os.environ.get("DATABASE_PORT", "3306"))

