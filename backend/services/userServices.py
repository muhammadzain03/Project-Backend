from database.dbQueries import UserModel


class UserService:
    @staticmethod
    def create_user(
        email: str,
        username: str,
        password: str,
        pictureURL: str | None,
        userDescriptionURL: str | None,
    ) -> bool:
        return UserModel._insert_user_db(
            email,
            username,
            password,
            pictureURL,
            userDescriptionURL,
        )

    @staticmethod
    def delete_user(email: str) -> bool:
        return UserModel._remove_user_db(email)
    
    @staticmethod
    def check_user_exists(email: str) -> bool:
        return bool(UserModel._get_user_id_by_email_db(email))

    @staticmethod
    def save_user_profile_url(email: str, profile_url: str) -> bool:
        return UserModel._save_profile_url_db(email, profile_url)

    @staticmethod
    def remove_user_profile_url(email: str) -> bool:
        return UserModel._remove_profile_url_db(email)

    @staticmethod
    def save_user_description_url(email: str, description_url: str) -> bool:
        return UserModel._save_description_url_db(email, description_url)

    @staticmethod
    def remove_user_description_url(email: str) -> bool:
        return UserModel._remove_description_url_db(email)

    # Getter functions for user data

    @staticmethod
    def get_complete_user_info(email: str) -> dict | None:
        return UserModel._get_full_profile_by_uid_db(email)

    @staticmethod
    def get_user_profile_url(email: str) -> str | None:
        return UserModel._get_user_profile_pic_url_by_email_db(email)

    @staticmethod
    def get_user_description_url(email: str) -> str | None:
        return UserModel._get_user_description_url_by_email_db(email)

    @staticmethod
    def get_user_id(email: str) -> str | None:
        return UserModel._get_user_id_by_email_db(email)

    @staticmethod
    def get_user_email(username: str) -> str | None:
        return UserModel._get_email_by_username_db(username)

    @staticmethod
    def get_username(email: str) -> str | None:
        return UserModel._get_username_by_email_db(email)

    @staticmethod
    def get_user_password(email: str) -> str | None:
        return UserModel._get_user_password_by_email_db(email)

    @staticmethod
    def update_username_email(
        old_email: str, new_username: str, new_email: str
    ) -> tuple[bool, str]:
        return UserModel._update_username_email_db(old_email, new_username, new_email)
