from app.data.db import connect_database
import sqlite3
import bcrypt
from pathlib import Path

print("=" * 60)
print("User Authentication Service")
print("=" * 60)

 # function to produce hashed password
def hash_password(plain_text_password) :
    password_bytes= plain_text_password.encode("utf-8")
    salt= bcrypt.gensalt()
    hashed_password= bcrypt.hashpw(password_bytes, salt)
    hashed_password_str= hashed_password.decode("utf-8")
    return hashed_password_str

 # function to verify if the hashed password is correct 
def verify_password(plain_text_password, hashed_password) :
    password_bytes= plain_text_password.encode("utf-8")
    hashed_password_bytes= hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

# function to check if database exists or if username already in database table
def user_exists(userName):
    
    conn = connect_database()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # Use a SELECT query to find the user
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (userName,))
        user = cursor.fetchone()
        conn.close()
        
        return user is not None
    except sqlite3.Error as e:
        print(f"Error checking user existence: {e}")
        return False
    finally:
        if conn:
            conn.close()

 # function for user registration
def register_user(user_name, password,role) :

    is_valid_user, user_msg = validate_userName(user_name)
    if not is_valid_user:
     return False, user_msg

    is_valid_pass, pass_msg = validate_password(password)
    if not is_valid_pass:
     return False, pass_msg

    if user_exists(user_name) == True:
     return False, f"Username {user_name} already exists ! "
    
    hashed_password = hash_password(password) 
    
    conn = connect_database()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (user_name, hashed_password, role)
        )
        conn.commit()
        return True, f"User '{user_name}' registered successfully."
    except sqlite3.Error as e:
        return False, "Registration failed due to a database error."
    finally:
        conn.close()


 # function to login existing user
def login_user(userName1, password1):

    conn = connect_database()
    if not conn:
        return False , "Database connection error."
        
    cursor = conn.cursor()
    
    # Retrieve the stored hash and role for the given username
    cursor.execute(
        "SELECT password_hash, role FROM users WHERE username = ?",
        (userName1,)
    )
    user_data = cursor.fetchone()
    conn.close()

    if user_data is None:
        return False, "Username not found!"
    
    stored_hash, role = user_data
    
    # Verify the password against the retrieved hash
    if verify_password(password1, stored_hash):
        return True, f"Login successful for Role {role}!"
    else:
        return False, "Incorrect password."
    
#validation for username
def validate_userName(user_name2) -> tuple[bool,str]: 
    if len(user_name2) < 3:
        return False, "Username must be at least 3 characters long."
    if not user_name2.isidentifier():  # checks if it's a valid name (letters, digits, underscores, no spaces)
        return False , "UserName does not contain valid characters"
    return True , "UserName is valid !"

#validation for password  
def validate_password(password) -> tuple[bool,str] :
        
       if " " in password:
        return False, "Password cannot contain spaces."
       if len(password) <= 8:
        return False, "Password must be more than 8 characters long."
       if not any(c.isupper() for c in password):
        return False, "Must contain at least one uppercase letter."
       if not any(c.islower() for c in password):
        return False, "Must contain at least one lowercase letter."
       if not any(c.isdigit() for c in password):
        return False, "Must contain at least one digit."
       if not any(c in "@#$%^&*!?" for c in password):
        return False, "Must contain at least one special character (@, #, $, etc.)."
       return True, "Strong password."

print("=" * 60)
print("User Migration Script")
print("=" * 60)
def migrate_users_from_file(conn, filepath= Path("DATA")/ "users.txt"):

    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   No users to migrate.")
        return
    conn = connect_database()
    cursor = conn.cursor()
    migrated_count = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Parse line: username,password_hash
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]
                
                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, 'user')
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")
    
    conn.commit()
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")