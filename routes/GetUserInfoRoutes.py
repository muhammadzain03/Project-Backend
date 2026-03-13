from flask import Blueprint, request, jsonify

from services.userServices import UserService
from services.GCPservices import FileService
from utils.config import BaseConfig as config

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.get("/<email>")
def get_user(email):
    user = UserService.get_complete_user_info(email)
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404
    user.pop("password", None)
    return jsonify(user), 200


@user_bp.delete("/<email>")
def delete_user(email):
    existing_user = UserService.check_user_exists(email)
    if not existing_user:
        return jsonify({"success": False, "message": "User does not exist."}), 404

    profile_url = UserService.get_user_profile_url(email)
    description_url = UserService.get_user_description_url(email)

    if profile_url:
        try:
            profile_object_name = profile_url.split(f"https://storage.googleapis.com/{config.GCS_BUCKET}/")[1]
        except IndexError:
            return jsonify({"success": False, "message": "Invalid profile URL format."}), 500

        pic_deleted_from_gcs, pic_deleted_from_db = FileService().delete_profile_photo(email, profile_object_name)
        if not pic_deleted_from_gcs or not pic_deleted_from_db:
            return jsonify({"success": False, "message": "Failed to delete user's profile photo."}), 500

    if description_url:
        try:
            description_object_name = description_url.split(f"https://storage.googleapis.com/{config.GCS_BUCKET}/")[1]
        except IndexError:
            return jsonify({"success": False, "message": "Invalid description URL format."}), 500

        desc_deleted_from_gcs, desc_deleted_from_db = FileService().delete_description(email, description_object_name)
        if not desc_deleted_from_gcs or not desc_deleted_from_db:
            return jsonify({"success": False, "message": "Failed to delete user's description."}), 500

    success = UserService.delete_user(email)
    if not success:
        return jsonify({"success": False, "message": "User not found or could not be deleted."}), 404

    return jsonify({"success": True, "message": "User deleted successfully."}), 200

@user_bp.get("/id/<email>")
def get_user_id(email):
    user_id = UserService.get_user_id(email)
    if not user_id:
        return jsonify({"success": False, "message": "User not found."}), 404
    return jsonify({"success": True, "user_id": user_id}), 200


@user_bp.get("/profile-url/<email>")
def get_profile_url(email):
    url = UserService.get_user_profile_url(email)
    if url is None:
        return jsonify({"success": False, "message": "User not found or no profile URL set."}), 404
    return jsonify({"success": True, "profile_url": url}), 200

@user_bp.get("/description-url/<email>")
def get_description_url(email):
    url = UserService.get_user_description_url(email)
    if url is None:
        return jsonify({"success": False, "message": "User not found or no description URL set."}), 404
    return jsonify({"success": True, "description_url": url}), 200