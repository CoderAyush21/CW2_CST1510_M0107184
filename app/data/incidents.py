from app.data.db import connect_database
import pandas as pd


def insert_incident(incident_id, severity, category, status, description, reported_by=None, timestamp=None):
    """Insert a new cyber incident. Returns ID of inserted row."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cyber_incidents
        (incident_id, timestamp, severity, category, status, description, reported_by)
        VALUES (?, COALESCE(?, CURRENT_TIMESTAMP), ?, ?, ?, ?, ?)
    """, (incident_id, timestamp, severity, category, status, description, reported_by))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def get_incident_by_id(incident_id):
    conn = connect_database()

    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents WHERE incident_id = ?",
        conn,
        params=(incident_id,)  
    )
    
    conn.close()
    return df


def get_all_incidents():
    """Retrieve all cyber incidents as a pandas DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
    conn.close()
    return df


def update_incident_status(incident_id, new_status):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?",
        (new_status, incident_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_incident(incident_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cyber_incidents WHERE incident_id = ?", (incident_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted