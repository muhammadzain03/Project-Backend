from flask import Blueprint, request, jsonify

from services.userServices import UserService

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
    success = UserService.delete_user(email)
    if not success:
        return jsonify({"success": False, "message": "User not found or could not be deleted."}), 404
    return jsonify({"success": True, "message": "User deleted successfully."}), 200


@user_bp.put("/<email>/profile-url")
def update_profile_url(email):
    body = request.get_json()
    url = body.get("url") if body else None
    if not url:
        return jsonify({"success": False, "message": "url is required."}), 400
    success = UserService.save_user_profile_url(email, url)
    if not success:
        return jsonify({"success": False, "message": "Failed to update profile URL."}), 500
    return jsonify({"success": True, "message": "Profile URL updated."}), 200


@user_bp.delete("/<email>/profile-url")
def remove_profile_url(email):
    success = UserService.remove_user_profile_url(email)
    if not success:
        return jsonify({"success": False, "message": "Failed to remove profile URL."}), 500
    return jsonify({"success": True, "message": "Profile URL removed."}), 200


@user_bp.put("/<email>/description-url")
def update_description_url(email):
    body = request.get_json()
    url = body.get("url") if body else None
    if not url:
        return jsonify({"success": False, "message": "url is required."}), 400
    success = UserService.save_user_description_url(email, url)
    if not success:
        return jsonify({"success": False, "message": "Failed to update description URL."}), 500
    return jsonify({"success": True, "message": "Description URL updated."}), 200


@user_bp.delete("/<email>/description-url")
def remove_description_url(email):
    success = UserService.remove_user_description_url(email)
    if not success:
        return jsonify({"success": False, "message": "Failed to remove description URL."}), 500
    return jsonify({"success": True, "message": "Description URL removed."}), 200
