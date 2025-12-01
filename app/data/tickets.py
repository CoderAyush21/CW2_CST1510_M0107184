from app.data.db import connect_database
import pandas as pd

def insert_ticket(priority, description, status, assigned_to=None, resolution_time_hours=None, created_at = None):
    """Insert a new IT ticket."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets
        (priority, description, status, assigned_to, created_at, resolution_time_hours)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
    """, (priority, description, status, assigned_to, resolution_time_hours))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id



def get_ticket_by_id(ticket_id):
    conn = connect_database()

    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE ticket_id = ?",
        conn,
        params=(ticket_id,)
    )
    conn.close()
    return df

def get_all_tickets():
    """Retrieve all IT tickets as a pandas DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
    conn.close()
    return df

def update_ticket_status(ticket_id, new_status):
    """Update only the ticket status."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE it_tickets
        SET status = ?
        WHERE ticket_id = ?
    """, (new_status, ticket_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_ticket(ticket_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted