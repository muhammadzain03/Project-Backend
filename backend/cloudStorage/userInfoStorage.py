import json
import logging

from google.cloud.exceptions import NotFound

from cloudStorage.GCP import set_gcs_connection
from utils.config import BaseConfig as config

BUCKET = config.GCS_BUCKET


class GCPUserInfoStorage:
    def upload_profile_image(self, object_name: str, stream, content_type: str) -> str:
        bucket = set_gcs_connection()
        blob = bucket.blob(object_name)
        blob.upload_from_file(stream, content_type=content_type)
        return f"https://storage.googleapis.com/{BUCKET}/{object_name}"

    def upload_description_json(self, object_name: str, description_text: str) -> str:
        bucket = set_gcs_connection()
        blob = bucket.blob(object_name)

        payload = {"description": description_text}
        json_data = json.dumps(payload, ensure_ascii=False)
        blob.upload_from_string(json_data, content_type="application/json")

        return f"https://storage.googleapis.com/{BUCKET}/{object_name}"

    def delete_object(self, object_name: str) -> bool:
        bucket = set_gcs_connection()
        blob = bucket.blob(object_name)

        try:
            blob.delete()
            return True
        except NotFound:
            logging.warning(f"GCS object not found during delete: {object_name}")
            return True
        except Exception as e:
            logging.error(f"Error deleting GCS object: {object_name}, error: {e}")
            return False
