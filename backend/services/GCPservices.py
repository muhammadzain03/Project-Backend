# Manages uploading, deleting, and updating user profile photos and 
# description files in GCS while keeping the database in sync.


import uuid
from werkzeug.utils import secure_filename

from services.userServices import UserService
from cloudStorage.userInfoStorage import GCPUserInfoStorage


class FileService:
    def __init__(self, user: UserService | None = None, gcs: GCPUserInfoStorage | None = None):
        self.user = user or UserService()
        self.gcs = gcs or GCPUserInfoStorage()

    # Uploads a profile image
    def upload_profile_photo(self, email: str, file) -> tuple:
        ext = secure_filename(file.filename).rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
        object_name = f"profile_pictures/{email}_{uuid.uuid4().hex}.{ext}"
        url = self.gcs.upload_profile_image(object_name, file.stream, file.content_type)
        self.user.save_user_profile_url(email, url)
        return url, object_name

    # Uploads a text description as JSON
    def upload_description(self, email: str, description_text: str) -> tuple:
        object_name = f"description_files/{email}_{uuid.uuid4().hex}.json"
        url = self.gcs.upload_description_json(object_name, description_text)
        self.user.save_user_description_url(email, url)
        return url, object_name

    # Deletes profile photo
    def delete_profile_photo(self, email: str, object_to_delete: str) -> tuple[bool, bool]:
        deleted_from_gcs = self.gcs.delete_object(object_to_delete)
        deleted_from_db = self.user.remove_user_profile_url(email)
        return deleted_from_gcs, deleted_from_db

    # Deletes description file
    def delete_description(self, email: str, object_to_delete: str) -> tuple[bool, bool]:
        deleted_from_gcs = self.gcs.delete_object(object_to_delete)
        deleted_from_db = self.user.remove_user_description_url(email)
        return deleted_from_gcs, deleted_from_db

    # Replaces exisiting profile photo
    def update_profile_photo(self, email: str, file, object_to_update: str) -> tuple:
        deleted_from_gcs, deleted_from_db = self.delete_profile_photo(email, object_to_update)
        if not deleted_from_gcs or not deleted_from_db:
            raise Exception("Failed to delete existing profile photo.")
        url, object_name = self.upload_profile_photo(email, file)
        return url, object_name, deleted_from_gcs, deleted_from_db

    # Replaces existing description
    def update_description(self, email: str, description_text: str, object_to_update: str) -> tuple:
        deleted_from_gcs, deleted_from_db = self.delete_description(email, object_to_update)
        if not deleted_from_gcs or not deleted_from_db:
            raise Exception("Failed to delete existing description.")
        url, object_name = self.upload_description(email, description_text)
        return url, object_name, deleted_from_gcs, deleted_from_db
