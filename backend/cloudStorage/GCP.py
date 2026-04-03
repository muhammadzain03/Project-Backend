from pathlib import Path

from google.cloud import storage

from utils import config  # loads root .env via BaseConfig

BUCKET = config.BaseConfig.GCS_BUCKET
GCP_CREDENTIALS = config.BaseConfig.GOOGLE_APPLICATION_CREDENTIALS


def set_gcs_connection():
    """Return a Google Cloud Storage bucket using the service account key from .env."""
    creds_path = GCP_CREDENTIALS
    if not creds_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set in .env")

    if not Path(creds_path).is_file():
        raise FileNotFoundError(
            f"GCP credentials file not found at: {creds_path}. "
            "Place the JSON key under credentials/ at the project root (or backend/credentials/) "
            "and set GOOGLE_APPLICATION_CREDENTIALS=credentials/your-key.json in .env."
        )

    client = storage.Client.from_service_account_json(str(creds_path))
    bucket = client.bucket(BUCKET)
    return bucket
