from services.userServices import UserService



class authServices:


    def Signup(email, username, password):
        # Check if user already exists
        existing_user = UserService.get_user_id(email)
        if existing_user:
            return {"success": False, "message": "User already exists."}

        # Create new user
        return  UserService.create_user(email, username, password, None, None)
        
        

    def Login(email, password):

        user_password = UserService.get_user_password(email)
        if user_password and user_password == password:
            return {"success": True, "message": "Login successful."}
        else:
            return {"success": False, "message": "Invalid email or password."}
        


if __name__ == "__main__":
    authServices()

    signup_status = authServices.Signup("test@example.com", "testuser", "password123")
    if signup_status == True:
        print("Signup successful.")
    else:
        print("Signup failed. User may already exist.")


    login_status = authServices.Login("test@example.com", "password123")
    if login_status == True:
        print("Login successful.")
    else:
        print("Login failed:", login_status["message"])


    remove_status = UserService.delete_user("test@example.com")
    if remove_status == True:
        print("User removed successfully.")
    else:
        print("Failed to remove user.")