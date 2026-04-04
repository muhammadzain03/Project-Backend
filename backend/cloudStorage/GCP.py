"""
Google Cloud Storage connection.

Locally:  Uses the service-account JSON key specified in .env
          (GOOGLE_APPLICATION_CREDENTIALS=credentials/your-key.json)

Cloud Run: Uses the attached service account automatically via
           Application Default Credentials (no JSON key needed).
"""

from pathlib import Path

from google.cloud import storage

from utils import config

BUCKET = config.BaseConfig.GCS_BUCKET
GCP_CREDENTIALS = config.BaseConfig.GOOGLE_APPLICATION_CREDENTIALS


def set_gcs_connection():
    """Return a Google Cloud Storage bucket handle."""

    if not BUCKET:
        raise RuntimeError("GCS_BUCKET is not set.")

    # 1. Try explicit key file (local development)
    if GCP_CREDENTIALS and Path(GCP_CREDENTIALS).is_file():
        client = storage.Client.from_service_account_json(str(GCP_CREDENTIALS))
        return client.bucket(BUCKET)

    # 2. Fall back to Application Default Credentials (Cloud Run / gcloud auth)
    try:
        client = storage.Client()
        return client.bucket(BUCKET)
    except Exception as e:
        raise RuntimeError(
            "Could not connect to GCS. Locally: set GOOGLE_APPLICATION_CREDENTIALS "
            "in .env pointing to your service-account JSON key. "
            "On Cloud Run: attach a service account with Storage permissions. "
            f"Error: {e}"
        )
