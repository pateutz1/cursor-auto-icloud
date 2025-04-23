import sqlite3
import os
import sys

# Add parent directory to path to import language module
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from src.utils.language import getTranslation, _
except ImportError:
    from utils.language import getTranslation, _


class CursorAuthManager:
    """Cursor Authentication Information Manager"""

    def __init__(self):
        # Determine operating system
        if sys.platform == "win32":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError(getTranslation("appdata_not_set"))
            self.db_path = os.path.join(
                appdata, "Cursor", "User", "globalStorage", "state.vscdb"
            )
        elif sys.platform == "darwin": # macOS
            self.db_path = os.path.abspath(os.path.expanduser(
                "~/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
            ))
        elif sys.platform == "linux" : # Linux and other Unix-like systems
            self.db_path = os.path.abspath(os.path.expanduser(
                "~/.config/Cursor/User/globalStorage/state.vscdb"
            ))
        else:
            raise NotImplementedError(getTranslation("unsupported_os").format(sys.platform))

    def update_auth(self, email=None, access_token=None, refresh_token=None):
        """
        Update Cursor's authentication information
        :param email: New email address
        :param access_token: New access token
        :param refresh_token: New refresh token
        :return: bool Success status of the update
        """
        updates = []
        # Login status
        updates.append(("cursorAuth/cachedSignUpType", "Auth_0"))

        if email is not None:
            updates.append(("cursorAuth/cachedEmail", email))
        if access_token is not None:
            updates.append(("cursorAuth/accessToken", refresh_token))
        if refresh_token is not None:
            updates.append(("cursorAuth/refreshToken", refresh_token))

        if not updates:
            print(getTranslation("no_values_to_update"))
            return False

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for key, value in updates:

                # If no rows were updated, it means the key doesn't exist, so insert it
                # Check if accessToken exists
                check_query = f"SELECT COUNT(*) FROM itemTable WHERE key = ?"
                cursor.execute(check_query, (key,))
                if cursor.fetchone()[0] == 0:
                    insert_query = "INSERT INTO itemTable (key, value) VALUES (?, ?)"
                    cursor.execute(insert_query, (key, value))
                else:
                    update_query = "UPDATE itemTable SET value = ? WHERE key = ?"
                    cursor.execute(update_query, (value, key))

                if cursor.rowcount > 0:
                    print(getTranslation("value_updated_success").format(key.split('/')[-1]))
                else:
                    print(getTranslation("value_not_found_or_unchanged").format(key.split('/')[-1]))

            conn.commit()
            return True

        except sqlite3.Error as e:
            print(getTranslation("database_error").format(str(e)))
            return False
        except Exception as e:
            print(getTranslation("general_error").format(str(e)))
            return False
        finally:
            if conn:
                conn.close()
