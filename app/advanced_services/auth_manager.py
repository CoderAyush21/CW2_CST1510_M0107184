from typing import Optional, Tuple
import bcrypt
from app.advanced_services.database_manager import DatabaseManager


class PasswordHasher:
    """
    Class to manage hashing of passwords

    """

    @staticmethod
    def hash_password(plain: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def check_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


class AuthManager:
    """
    Class to manage user registration, login and validation

    """

    def __init__(self, db: DatabaseManager):
        self.db = db

    # ----------------------------
    # Username validation
    # ----------------------------
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        if not username.isidentifier():
            return False, "Username contains invalid characters."
        return True, "Valid username."

    # ----------------------------
    # Password validation
    # ----------------------------
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        if " " in password:
            return False, "Password cannot contain spaces."
        if len(password) <= 8:
            return False, "Password must be more than 8 characters."
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter."
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter."
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit."
        if not any(c in "@#$%^&*!?" for c in password):
            return False, "Password must contain at least one special character."
        return True, "Strong password."


    def user_exists(self, username: str) -> bool:
        row = self.db.fetch_one(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        )
        return row is not None




    def register_user(self, username: str, password: str, role: str = "user") -> Tuple[bool, str]:
        # Validate username
        is_valid, msg = self.validate_username(username)
        if not is_valid:
            return False, msg

        # Validate password
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg

        # Check if user already exists
        if self.user_exists(username):
            return False, f"Username '{username}' already exists."

        # Hash the password
        hashed = PasswordHasher.hash_password(password)

        # Insert user
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed, role)
        )


        row = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ?", (username,)
        )
        user_id = row[0] if row else None

        return True, f"User '{username}' registered successfully with ID {user_id}. You can now Login ! "


    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        row = self.db.fetch_one(
            "SELECT password_hash, role FROM users WHERE username = ?",
            (username,)
        )

        if row is None:
            return False, "Username not found!"

        password_hash_db, role_db = row

        if PasswordHasher.check_password(password, password_hash_db):
            return True, f"Login successful for Role {role_db}!"
        else:
            return False, "Incorrect password."

