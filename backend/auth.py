import hashlib
import sqlite3 

class Auth:
    @staticmethod
    def hash_password(password):
        """Returns a SHA-256 hashed password."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate_user(username, password):
        db_conn = sqlite3.connect("barcode_management.db")
        cursor = db_conn.cursor()

        try:
            cursor.execute("SELECT user_id, username, password, role FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user and user[2] == (password):
                return {"user_id": user[0], "username": user[1], "role": user[3]}
            else:
                return None  

        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return None

        finally:
            db_conn.close()

    @staticmethod
    def register_user(username, password, role):
        """Registers a new user with a hashed password."""
        db_conn = sqlite3.connect("barcode_management.db")
        cursor = db_conn.cursor()

        try:
            hashed_password = Auth.hash_password(password)
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, hashed_password, role))
            db_conn.commit()
            return True

        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            return False

        finally:
            db_conn.close()
