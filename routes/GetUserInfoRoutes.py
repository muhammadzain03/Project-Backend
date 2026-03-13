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