# extensions/GoogleCloudStorage.py
from flask import Blueprint
from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv
import config


load_dotenv(override=True)

gcs_bp = Blueprint("gcs", __name__)
BUCKET = config.BaseConfig.GCS_BUCKET
GCP_CREDENTIALS = config.BaseConfig.GOOGLE_APPLICATION_CREDENTIALS


#  GOOGLE CLOUD STORAGE Connection
def set_gcs_connection():
    """Return a Google Cloud Storage client using the service account key from .env."""
    creds_path = GCP_CREDENTIALS
    if not creds_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set in .env")

    if not Path(creds_path).is_file():
        raise FileNotFoundError(f"GCP credentials file not found at: {creds_path}")
    
    client = storage.Client.from_service_account_json(str(creds_path))
    bucket = client.bucket(BUCKET)
    return bucket
