from app.data.db import connect_database
import pandas as pd


def insert_dataset(dataset_id, name, rows, columns, uploaded_by=None):
    """Insert a new dataset."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO datasets_metadata
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (dataset_id, name, rows, columns, uploaded_by))
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

def get_all_datasets():
    """Retrieve all dataset metadata as a pandas DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM datasets_metadata", conn)
    conn.close()
    return df

def update_dataset_name(dataset_id, new_name):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE datasets_metadata SET name = ? WHERE dataset_id = ?",
        (new_name, dataset_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_dataset(dataset_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?", (dataset_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted