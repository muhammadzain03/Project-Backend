from flask import Blueprint, jsonify, request

from services.userServices import UserService
from services.GCPservices import FileService
from utils.config import BaseConfig as config
from utils.gcs_errors import gcs_unavailable_response
from utils.gcs_signed_urls import object_name_from_stored_gcs_url, sign_user_dict_for_client

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.patch("/<email>")
def patch_user(email):
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    new_email = body.get("email")
    if username is None or new_email is None:
        return jsonify(
            {"success": False, "message": "username and email are required."}
        ), 400

    if not UserService.check_user_exists(email):
        return jsonify({"success": False, "message": "User not found."}), 404

    us = str(username).strip()
    ne = str(new_email).strip()
    ok, err = UserService.update_username_email(email, us, ne)
    if not ok:
        return jsonify({"success": False, "message": err}), 400

    updated = UserService.get_complete_user_info(ne)
    if updated:
        updated.pop("password", None)
        updated = sign_user_dict_for_client(updated)
    return jsonify({"success": True, "message": "Account updated.", "user": updated}), 200


# 1) Get user email
@user_bp.get("/<email>")
def get_user(email):
    user = UserService.get_complete_user_info(email)
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404
    user.pop("password", None)
    user = sign_user_dict_for_client(user)
    return jsonify(user), 200, {
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
    }

# 2) Delete user email 
@user_bp.delete("/<email>")
def delete_user(email):
    existing_user = UserService.check_user_exists(email)
    if not existing_user:   # If user does not exist = 404
        return jsonify({"success": False, "message": "User does not exist."}), 404

    profile_url = UserService.get_user_profile_url(email)
    description_url = UserService.get_user_description_url(email)

    if profile_url:     # Deletes profile photo from GCS and database
        profile_object_name = object_name_from_stored_gcs_url(profile_url)
        if not profile_object_name:
            return jsonify({"success": False, "message": "Invalid profile URL format."}), 500

        try:
            pic_deleted_from_gcs, pic_deleted_from_db = FileService().delete_profile_photo(email, profile_object_name)
        except (FileNotFoundError, RuntimeError) as e:
            err = gcs_unavailable_response(e)
            if err:
                return err
            raise
        if not pic_deleted_from_gcs or not pic_deleted_from_db:
            return jsonify({"success": False, "message": "Failed to delete user's profile photo."}), 500

    if description_url:     # Deletes description file from GCS and database
        description_object_name = object_name_from_stored_gcs_url(description_url)
        if not description_object_name:
            return jsonify({"success": False, "message": "Invalid description URL format."}), 500

        try:
            desc_deleted_from_gcs, desc_deleted_from_db = FileService().delete_description(email, description_object_name)
        except (FileNotFoundError, RuntimeError) as e:
            err = gcs_unavailable_response(e)
            if err:
                return err
            raise
        if not desc_deleted_from_gcs or not desc_deleted_from_db:   # Returns 500 if URL parsing fails or deletion fails at any step
            return jsonify({"success": False, "message": "Failed to delete user's description."}), 500

    success = UserService.delete_user(email)    # Deletes the user record itself
    if not success:
        return jsonify({"success": False, "message": "User not found or could not be deleted."}), 404

    return jsonify({"success": True, "message": "User deleted successfully."}), 200

# 3) Returns just the user ID for a given email.
@user_bp.get("/id/<email>")
def get_user_id(email):
    user_id = UserService.get_user_id(email)
    if not user_id:
        return jsonify({"success": False, "message": "User not found."}), 404
    return jsonify({"success": True, "user_id": user_id}), 200

# 4) Returns the GCS URL of the user's profile photo.
@user_bp.get("/profile-url/<email>")
def get_profile_url(email):
    url = UserService.get_user_profile_url(email)
    if url is None:
        return jsonify({"success": False, "message": "User not found or no profile URL set."}), 404
    return jsonify({"success": True, "profile_url": url}), 200

# 5) Returns the GCS URL of the user's description file.
@user_bp.get("/description-url/<email>")
def get_description_url(email):
    url = UserService.get_user_description_url(email)
    if url is None:
        return jsonify({"success": False, "message": "User not found or no description URL set."}), 404
    return jsonify({"success": True, "description_url": url}), 200