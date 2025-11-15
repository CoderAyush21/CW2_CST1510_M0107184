import sqlite3
from pathlib import Path

DB_PATH = Path("DATA") / "intelligence_platform.db"

DB_PATH.parent.mkdir(exist_ok=True)

def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))