import bcrypt
from flask import Blueprint, request, jsonify

from services.userServices import UserService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/signup")
def signup():
    body = request.get_json()
    if not body:
        return jsonify({"success": False, "message": "Invalid request body."}), 400

    email = body.get("email")
    username = body.get("username")
    password = body.get("password")

    if not all([email, username, password]):
        return jsonify({"success": False, "message": "email, username and password are required."}), 400

    existing = UserService.get_user_id(email)
    if existing:
        return jsonify({"success": False, "message": "User already exists."}), 400

    hashed_pw = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    success = UserService.create_user(email, username, hashed_pw, None, None)
    if not success:
        return jsonify({"success": False, "message": "Failed to create user."}), 500

    return jsonify({"success": True, "message": "User created successfully."}), 201


@auth_bp.post("/login")
def login():
    body = request.get_json()
    if not body:
        return jsonify({"success": False, "message": "Invalid request body."}), 400

    email = body.get("email")
    password = body.get("password")

    if not all([email, password]):
        return jsonify({"success": False, "message": "email and password are required."}), 400

    stored_password = UserService.get_user_password(email)
    if not stored_password:
        return jsonify({"success": False, "message": "Invalid email or password."}), 400

    if not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
        return jsonify({"success": False, "message": "Invalid email or password."}), 400

    return jsonify({"success": True, "message": "Login successful."}), 200
