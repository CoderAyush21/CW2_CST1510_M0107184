from typing import Optional, Tuple
import bcrypt
from app.advanced_services.database_manager import DatabaseManager


class PasswordHasher:
    '''
    Class to manage hashing of passwords 

    '''

    @staticmethod
    def hash_password(plain: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def check_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


class AuthManager:
    '''
    Class to manage user registration, user login and validating usernames & passwords

    '''

    '''
    Class constructor that takes the database path when creating an object of its type
    '''
    def __init__(self, db: DatabaseManager):
        self.db = db

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        if not username.isidentifier():
            return False, "Username contains invalid characters."
        return True, "Valid username."

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        if " " in password:
            return False, "Password cannot contain spaces."
        if len(password) <= 8:
            return False, "Password must be more than 8 characters."
        if not any(c.isupper() for c in password):
            return False, "Must contain at least one uppercase letter."
        if not any(c.islower() for c in password):
            return False, "Must contain at least one lowercase letter."
        if not any(c.isdigit() for c in password):
            return False, "Must contain at least one digit."
        if not any(c in "@#$%^&*!?" for c in password):
            return False, "Must contain at least one special character."
        return True, "Strong password."


    def user_exists(self, username: str) -> bool:
        row = self.db.fetch_one(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        )
        return row is not None

    def register_user(self, username: str, password: str, role: str = "user") -> Tuple[bool, str]:
        
        '''
        Call the validation methods to check the username and password
  
        '''
        is_valid, msg = self.validate_username(username)
        if not is_valid:
            return False, msg

        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg

        if self.user_exists(username):
            return False, f"Username '{username}' already exists."

        '''
        Produce hashed password by calling the static method hash_password from the class PasswordHasher
        '''
        hashed = PasswordHasher.hash_password(password)

        
        self.db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed, role)
        )
        return True, f"User '{username}' registered successfully."

    def login_user(self, username: str, password: str) -> Optional[dict]:
        row = self.db.fetch_one(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        if row is None:
            return None

        username_db, password_hash_db, role_db = row
        if PasswordHasher.check_password(password, password_hash_db):
            return {"username": username_db, "role": role_db}

        return None
