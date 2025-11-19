from app.data.db import connect_database
import sqlite3
import pandas as pd
def insert_user(username, password_hash, role='user'):
    """Insert new user."""
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        user_ID = cursor.lastrowid
        
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()
    return user_ID

def get_user_by_username(username):
    """Retrieve user by username."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM users WHERE username = ?", 
        conn,
        params=(username,)
    )
    conn.close()
    return df

def get_all_users():
    """Retrieve all users as a pandas DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

def update_user_password(username, new_password_hash):
    """Update the password of a user. Returns True if updated, False if user not found."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (new_password_hash, username)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_user(username):
    """Delete a user by username. Returns True if deleted, False if user not found."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted