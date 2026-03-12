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


if __name__ == "__main__":
    signup_status = AuthServices.signup("test@example.com", "testuser", "password123")
    if signup_status is True:
        print("Signup successful.")
    else:
        print("Signup failed. User may already exist.")

    login_status = AuthServices.login("test@example.com", "password123")
    if login_status is True:
        print("Login successful.")
    else:
        print("Login failed:", login_status["message"])

    remove_status = UserService.delete_user("test@example.com")
    if remove_status is True:
        print("User removed successfully.")
    else:
        print("Failed to remove user.")