import logging

from flask import jsonify, request, Blueprint

from services.GCPservices import FileService
from services.userServices import UserService
from utils.gcs_errors import gcs_unavailable_response
from utils.gcs_signed_urls import object_name_from_stored_gcs_url, sign_gcs_https_url


update_user_bp = Blueprint("update_user", __name__, url_prefix="/user")

files = FileService()
user = UserService()


@update_user_bp.post("/<email>/profile-photo")
def upload_profile_photo(email):

    existing_user = user.check_user_exists(email)
    if not existing_user:
        return jsonify({"success": False, "message": "User does not exist."}), 404

    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"success": False, "message": "No file uploaded."}), 400
    
    current_url = user.get_user_profile_url(email)

    if not current_url: # First Upload
        try:
            url, object_name = files.upload_profile_photo(email, file)
        except (FileNotFoundError, RuntimeError) as e:
            err = gcs_unavailable_response(e)
            if err:
                return err
            raise
        return jsonify({"success": True, 
                        "message": "Profile photo uploaded.", 
                        "email": email,
                        "object_name": object_name,
                        "url": sign_gcs_https_url(url)}), 200
    
    else: # Update existing photo
        object_to_delete = object_name_from_stored_gcs_url(current_url)
        if not object_to_delete:
            return jsonify({"success": False, "message": "Invalid existing profile URL format."}), 500
        
        try:
            url, object_name, deleted_from_gcs, deleted_from_db = files.update_profile_photo(email, file, object_to_delete)
        except (FileNotFoundError, RuntimeError) as e:
            err = gcs_unavailable_response(e)
            if err:
                return err
            raise
        if not deleted_from_gcs or not deleted_from_db:
            return jsonify({"success": False, "message": "Failed to delete existing profile photo."}), 500
        return jsonify({"success": True, 
                        "message": "Profile photo updated.", 
                        "email": email,
                        "object_name": object_name,
                        "url": sign_gcs_https_url(url)}), 200
    
@update_user_bp.delete("/<email>/profile-photo")
def delete_profile_photo(email):

    existing_user = user.check_user_exists(email)
    if not existing_user:
        return jsonify({"success": False, "message": "User does not exist."}), 404
    
    current_url = user.get_user_profile_url(email)
    if not current_url:
        return jsonify({"success": False, "message": "No profile photo to delete."}), 404
    
    object_to_delete = object_name_from_stored_gcs_url(current_url)
    if not object_to_delete:
        return jsonify({"success": False, "message": "Invalid profile URL format."}), 500
    
    try:
        deleted_from_gcs, deleted_from_db = files.delete_profile_photo(email, object_to_delete)
    except (FileNotFoundError, RuntimeError) as e:
        err = gcs_unavailable_response(e)
        if err:
            return err
        raise
    if not deleted_from_db:
        return jsonify({"success": False, "message": "Failed to delete profile photo URL from database."}), 500
    if not deleted_from_gcs:
        logging.warning(
            "GCS delete failed for profile object %s; profile URL cleared in DB.",
            object_to_delete,
        )
    return jsonify({"success": True, "message": "Profile photo deleted."}), 200


@update_user_bp.post("/<email>/description")
def upload_description(email):

    existing_user = user.check_user_exists(email)
    if not existing_user:
        return jsonify({"success": False, "message": "User does not exist."}), 404
    
    data = request.get_json()
    description_text = data.get("description")
    if not description_text:
        return jsonify({"success": False, "message": "No description provided."}), 400
    
    try:
        url, object_name = files.upload_description(email, description_text)
    except (FileNotFoundError, RuntimeError) as e:
        err = gcs_unavailable_response(e)
        if err:
            return err
        raise
    return jsonify({"success": True, 
                    "message": "Description uploaded.", 
                    "email": email,
                    "object_name": object_name,
                    "url": sign_gcs_https_url(url)}), 200

@update_user_bp.delete("/<email>/description")
def delete_description(email):

    existing_user = user.check_user_exists(email)
    if not existing_user:
        return jsonify({"success": False, "message": "User does not exist."}), 404

    current_url = user.get_user_description_url(email)
    if not current_url:
        return jsonify({"success": False, "message": "No description to delete."}), 404
    
    object_to_delete = object_name_from_stored_gcs_url(current_url)
    if not object_to_delete:
        return jsonify({"success": False, "message": "Invalid description URL format."}), 500
    
    try:
        deleted_from_gcs, deleted_from_db = files.delete_description(email, object_to_delete)
    except (FileNotFoundError, RuntimeError) as e:
        err = gcs_unavailable_response(e)
        if err:
            return err
        raise
    if not deleted_from_db:
        return jsonify({"success": False, "message": "Failed to delete description URL from database."}), 500
    if not deleted_from_gcs:
        logging.warning(
            "GCS delete failed for description object %s; description URL cleared in DB.",
            object_to_delete,
        )
    return jsonify({"success": True, "message": "Description deleted."}), 200