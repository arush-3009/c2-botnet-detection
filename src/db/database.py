"""
This is the database layer.
Every other component of the system either writes to this database,
or reads from it.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

#Database file
DB_PATH = Path(__file__).parent.parent.parent / "c2_traffic.db"


def get_connection(db_path = None):
    """
    Establish connection to database.
    """
    if db_path is not None:
        path = db_path
    else:
        path = str(DB_PATH)
    
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row

    return connection

def init_db(db_path = None):

    connection = get_connection(db_path)

    connection.execute("""
    CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            bot_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            source_ip TEXT DEFAULT '127.0.0.1',
            payload_size INTEGER DEFAULT 0,
            beacon_interval REAL DEFAULT NULL,
            metadata TEXT DEFAULT '{}'
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_bot_id ON traffic_logs(bot_id)
    """)
    
    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON traffic_logs(timestamp)
    """)

    connection.commit()

    connection.close()