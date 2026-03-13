from flask import jsonify, request, Blueprint  
from services.GCPservices import FileService
from services.userServices import UserService
from cloudStorage.userInfoStorage import GCPUserInfoStorage
from utils.config import BaseConfig as config


update_user_bp = Blueprint("update_user", __name__, url_prefix="/user")

files = FileService()
user = UserService()
gcs = GCPUserInfoStorage()

GCP_BUCKET = config.GCS_BUCKET


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
        url, object_name = files.upload_profile_photo(email, file)
        return jsonify({"success": True, 
                        "message": "Profile photo uploaded.", 
                        "email": email,
                        "object_name": object_name,
                        "url": url}), 200
    
    else: # Update existing photo
        try:
            object_to_delete = current_url.split(f"https://storage.googleapis.com/{GCP_BUCKET}/")[1]
        except IndexError:
            return jsonify({"success": False, "message": "Invalid existing profile URL format."}), 500
        
        url, object_name, deleted_from_gcs, deleted_from_db = files.update_profile_photo(email, file, object_to_delete)
        if not deleted_from_gcs or not deleted_from_db:
            return jsonify({"success": False, "message": "Failed to delete existing profile photo."}), 500
        return jsonify({"success": True, 
                        "message": "Profile photo updated.", 
                        "email": email,
                        "object_name": object_name,
                        "url": url}), 200
    
@update_user_bp.delete("/<email>/profile-photo")
def delete_profile_photo(email):

    existing_user = user.check_user_exists(email)
    if not existing_user:
        return jsonify({"success": False, "message": "User does not exist."}), 404
    
    current_url = user.get_user_profile_url(email)
    if not current_url:
        return jsonify({"success": False, "message": "No profile photo to delete."}), 404
    
    try:
        object_to_delete = current_url.split(f"https://storage.googleapis.com/{GCP_BUCKET}/")[1]
    except IndexError:
        return jsonify({"success": False, "message": "Invalid profile URL format."}), 500
    
    deleted_from_gcs, deleted_from_db = files.delete_profile_photo(email, object_to_delete)
    if not deleted_from_gcs:
        return jsonify({"success": False, "message": "Failed to delete profile photo from GCS."}), 500
    if not deleted_from_db:
        return jsonify({"success": False, "message": "Failed to delete profile photo URL from database."}), 500
    
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
    
    url, object_name = files.upload_description(email, description_text)
    return jsonify({"success": True, 
                    "message": "Description uploaded.", 
                    "email": email,
                    "object_name": object_name,
                    "url": url}), 200

@update_user_bp.delete("/<email>/description")
def delete_description(email):

    existing_user = user.check_user_exists(email)
    if not existing_user:
        return jsonify({"success": False, "message": "User does not exist."}), 404

    current_url = user.get_user_description_url(email)
    if not current_url:
        return jsonify({"success": False, "message": "No description to delete."}), 404
    
    try:
        object_to_delete = current_url.split(f"https://storage.googleapis.com/{GCP_BUCKET}/")[1]
    except IndexError:
        return jsonify({"success": False, "message": "Invalid description URL format."}), 500
    
    deleted_from_gcs, deleted_from_db = files.delete_description(email, object_to_delete)
    if not deleted_from_gcs:
        return jsonify({"success": False, "message": "Failed to delete description from GCS."}), 500
    if not deleted_from_db:
        return jsonify({"success": False, "message": "Failed to delete description URL from database."}), 500
    
    return jsonify({"success": True, "message": "Description deleted."}), 200