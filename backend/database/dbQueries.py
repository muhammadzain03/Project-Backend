from database.Database import Database


class UserModel:
    @staticmethod
    def _close_resources(cursor=None, conn=None) -> None:
        """
        Safely close cursor and connection.

        Important:
        For mysql.connector pooling, conn.close() returns the connection
        back to the pool. Do not guard it with conn.is_connected(),
        because even a stale/closed-looking pooled connection should still
        be closed/released if the object exists.
        """
        if cursor is not None:
            try:
                cursor.close()
            except Exception as e:
                print(f"Error closing cursor: {e}")

        if conn is not None:
            try:
                conn.close()
            except Exception as e:
                print(f"Error closing connection: {e}")

    @staticmethod
    def _insert_user_db(
        email: str,
        username: str,
        password: str,
        pictureURL: str | None,
        userDescriptionURL: str | None,
    ) -> bool:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            if not conn.is_connected():
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
                    userDescriptionURL,
                ),
            )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error inserting user: {e}")
            return False

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _remove_user_db(email: str) -> bool:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM users WHERE email = %s",
                (email,),
            )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error removing user: {e}")
            return False

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _save_profile_url_db(email: str, profile_url: str) -> bool:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET pictureURL = %s WHERE email = %s",
                (profile_url, email),
            )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error updating profile URL: {e}")
            return False

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _remove_profile_url_db(email: str) -> bool:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET pictureURL = NULL WHERE email = %s",
                (email,),
            )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error removing profile URL: {e}")
            return False

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _save_description_url_db(email: str, description_url: str) -> bool:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET userDescriptionURL = %s WHERE email = %s",
                (description_url, email),
            )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error updating description URL: {e}")
            return False

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _remove_description_url_db(email: str) -> bool:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET userDescriptionURL = NULL WHERE email = %s",
                (email,),
            )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error removing description URL: {e}")
            return False

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _update_password_db(email: str, new_password: str) -> bool:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (new_password, email),
            )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error updating password: {e}")
            return False

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _get_full_profile_by_uid_db(email: str) -> dict | None:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, email, username, password, pictureURL, userDescriptionURL
                FROM users
                WHERE email = %s
                """,
                (email,),
            )

            result = cursor.fetchone()

            if result:
                return {
                    "id": result[0],
                    "email": result[1],
                    "username": result[2],
                    "password": result[3],
                    "pictureURL": result[4],
                    "userDescriptionURL": result[5],
                }

            return None

        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _get_username_by_email_db(email: str) -> str | None:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT username FROM users WHERE email = %s",
                (email,),
            )

            result = cursor.fetchone()

            if result:
                return result[0]

            return None

        except Exception as e:
            print(f"Error fetching username: {e}")
            return None

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _get_email_by_username_db(username: str) -> str | None:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT email FROM users WHERE username = %s",
                (username,),
            )

            result = cursor.fetchone()

            if result:
                return result[0]

            return None

        except Exception as e:
            print(f"Error fetching email: {e}")
            return None

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _get_user_id_by_email_db(email: str) -> str | None:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,),
            )

            result = cursor.fetchone()

            if result:
                return result[0]

            return None

        except Exception as e:
            print(f"Error fetching user ID: {e}")
            return None

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _get_user_profile_pic_url_by_email_db(email: str) -> str | None:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT pictureURL FROM users WHERE email = %s",
                (email,),
            )

            result = cursor.fetchone()

            if result:
                return result[0]

            return None

        except Exception as e:
            print(f"Error fetching profile URL: {e}")
            return None

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _get_user_description_url_by_email_db(email: str) -> str | None:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT userDescriptionURL FROM users WHERE email = %s",
                (email,),
            )

            result = cursor.fetchone()

            if result:
                return result[0]

            return None

        except Exception as e:
            print(f"Error fetching description URL: {e}")
            return None

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _get_user_password_by_email_db(email: str) -> str | None:
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT password FROM users WHERE email = %s",
                (email,),
            )

            result = cursor.fetchone()

            if result:
                return result[0]

            return None

        except Exception as e:
            print(f"Error fetching password: {e}")
            return None

        finally:
            UserModel._close_resources(cursor, conn)

    @staticmethod
    def _update_username_email_db(
        old_email: str,
        new_username: str,
        new_email: str,
    ) -> tuple[bool, str]:
        """
        Update username and email for the row identified by old_email.
        """
        conn = None
        cursor = None

        try:
            conn = Database.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, username, email FROM users WHERE email = %s",
                (old_email,),
            )

            row = cursor.fetchone()

            if not row:
                return False, "User not found."

            user_id, cur_username, cur_email = row[0], row[1], row[2]

            nu = new_username.strip()
            ne = new_email.strip()

            if not nu or not ne:
                return False, "Username and email are required."

            if nu != cur_username:
                cursor.execute(
                    "SELECT email FROM users WHERE username = %s",
                    (nu,),
                )

                taken = cursor.fetchone()

                if taken and taken[0] != cur_email:
                    return False, "Username already taken."

            if ne != cur_email:
                cursor.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (ne,),
                )

                taken = cursor.fetchone()

                if taken and taken[0] != user_id:
                    return False, "Email already in use."

            cursor.execute(
                "UPDATE users SET username = %s, email = %s WHERE email = %s",
                (nu, ne, old_email),
            )

            conn.commit()
            return True, ""

        except Exception as e:
            print(f"Error updating account fields: {e}")
            return False, str(e)

        finally:
            UserModel._close_resources(cursor, conn)