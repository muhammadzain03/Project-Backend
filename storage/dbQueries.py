from storage.Database import Database


class UserModel:

    @staticmethod
    def _insert_user_db(
        email:str,
        username:str,
        password:str,
        pictureURL:str | None,
        userDescriptionURL:str | None

    ) -> bool:
        try:

            conn = Database.get_connection()
            cursor = conn.cursor()
            connection_Status = conn.is_connected()
            if not connection_Status:
                raise ConnectionError("Failed to connect to the database.")

            cursor.execute(
                """
                INSERT INTO users (email, username, password, pictureURL, userDescriptionURL)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    email,
                    username,
                    password,
                    pictureURL,
                    userDescriptionURL
                )
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def _remove_user_db(email: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM users WHERE email = %s",
                (email,)
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()



    def _save_profile_url_db(email: str, profile_url: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET pictureURL = %s WHERE email = %s",
                (profile_url, email)
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating profile URL: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def _remove_profile_url_db(email: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET pictureURL = NULL WHERE email = %s",
                (email,)
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing profile URL: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


    def _save_description_url_db(email: str, description_url: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET userDescriptionURL = %s WHERE email = %s",
                (description_url, email)
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating description URL: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


    def _remove_description_url_db(email: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET userDescriptionURL = NULL WHERE email = %s",
                (email,)
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing description URL: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def _update_password_db(email: str, new_password: str) -> bool:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (new_password, email)
            )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

  
  
  
  
  
  # Getters for specific fields (username, email, user ID) based on email or username

    @staticmethod
    def _get_full_profile_by_uid_db(email: str) -> dict | None:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, email, username, password, pictureURL, userDescriptionURL FROM users WHERE email = %s",
                (email,)
            )

            result = cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "email": result[1],
                    "username": result[2],
                    "password": result[3],
                    "pictureURL": result[4],
                    "userDescriptionURL": result[5]
                }
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def _get_username_by_email_db(email: str) -> str | None:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT username FROM users WHERE email = %s",
                (email,)
            )

            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error fetching username: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


    def _get_email_by_username_db(username: str) -> str | None:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT email FROM users WHERE username = %s",
                (username,)
            )

            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error fetching email: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


    def _get_user_id_by_email_db(email: str) -> str | None:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error fetching user ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def _get_user_profile_pic_url_by_email_db(email: str) -> str | None:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT pictureURL FROM users WHERE email = %s",
                (email,)
            )

            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error fetching profile URL: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def _get_user_description_url_by_email_db(email: str) -> str | None:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT userDescriptionURL FROM users WHERE email = %s",
                (email,)
            )

            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error fetching description URL: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


    def _get_user_password_by_email_db(email: str) -> str | None:
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT password FROM users WHERE email = %s",
                (email,)
            )

            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Error fetching password: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

