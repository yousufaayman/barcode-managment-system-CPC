import hashlib
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "your_mysql_user"),
    "password": os.getenv("DB_PASSWORD", "your_mysql_password"),
    "database": os.getenv("DB_NAME", "barcode_management"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "autocommit": True
}

class Auth:
    @staticmethod
    def hash_password(password):
        """Returns a SHA-256 hashed password."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate_user(username, password):
        """Authenticates a user by checking the hashed password."""
        db_conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = db_conn.cursor()

        try:
            cursor.execute("SELECT user_id, username, password, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and user["password"] == Auth.hash_password(password):
                return {"user_id": user["user_id"], "username": user["username"], "role": user["role"]}
            else:
                return None  

        except pymysql.MySQLError as e:
            print(f"Database Error: {e}")
            return None

        finally:
            cursor.close()
            db_conn.close()

    @staticmethod
    def register_user(username, password, role):
        """Registers a new user with a hashed password and validates inputs."""
        db_conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = db_conn.cursor()

        try:
            # Check if username already exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return {"success": False, "message": "Username already exists!"}

            # Validate role
            allowed_roles = ["Admin", "Cutting", "Sewing", "Packaging"]
            if role not in allowed_roles:
                return {"success": False, "message": "Invalid role. Choose from Admin, Cutting, Sewing, Packaging."}

            # Insert new user
            hashed_password = Auth.hash_password(password)
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                           (username, hashed_password, role))
            db_conn.commit()
            return {"success": True, "message": "User created successfully!"}

        except pymysql.MySQLError as e:
            return {"success": False, "message": f"Database Error: {e}"}

        finally:
            cursor.close()
            db_conn.close()

    @staticmethod
    def get_users():
        """Fetches all users from the database excluding passwords."""
        db_conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = db_conn.cursor()

        try:
            cursor.execute("SELECT user_id, username, role FROM users")
            users = cursor.fetchall()
            return users

        except pymysql.MySQLError as e:
            print(f"Database Error: {e}")
            return []

        finally:
            cursor.close()
            db_conn.close()

    @staticmethod
    def delete_user(user_id):
        """Deletes a user from the database."""
        db_conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = db_conn.cursor()

        try:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            db_conn.commit()
            return {"success": True, "message": "User deleted successfully!"}
        except pymysql.MySQLError as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            db_conn.close()

    @staticmethod
    def reset_user_password(user_id, new_password):
        """Resets the user's password."""
        db_conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = db_conn.cursor()

        try:
            cursor.execute("UPDATE users SET password = %s WHERE user_id = %s", (Auth.hash_password(new_password), user_id))
            db_conn.commit()
            return {"success": True, "message": "Password reset successfully!"}
        except pymysql.MySQLError as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            db_conn.close()

    @staticmethod
    def update_user_role(user_id, new_role):
        """Updates the user's role."""
        db_conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        cursor = db_conn.cursor()

        try:
            allowed_roles = ["Admin", "Cutting", "Sewing", "Packaging"]
            if new_role not in allowed_roles:
                return {"success": False, "message": "Invalid role. Choose from Admin, Cutting, Sewing, Packaging."}

            cursor.execute("UPDATE users SET role = %s WHERE user_id = %s", (new_role, user_id))
            db_conn.commit()
            return {"success": True, "message": "User role updated successfully!"}
        except pymysql.MySQLError as e:
            return {"success": False, "message": f"Database Error: {e}"}
        finally:
            cursor.close()
            db_conn.close()
