from services.userServices import UserService


class AuthServices:
    @staticmethod
    def signup(email: str, username: str, password: str):
        existing_user = UserService.get_user_id(email)
        if existing_user:
            return {"success": False, "message": "User already exists."}
        return UserService.create_user(email, username, password, None, None)

    @staticmethod
    def login(email: str, password: str):
        user_password = UserService.get_user_password(email)
        if user_password and user_password == password:
            return {"success": True, "message": "Login successful."}
        return {"success": False, "message": "Invalid email or password."}
