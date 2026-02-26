"""
This is the database layer.
Every other component of the system either writes to this database,
or reads from it.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
import os

#Database file
DB_PATH = Path(os.environ.get("DB_PATH", str(Path(__file__).parent.parent.parent / "c2_traffic.db")))



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


def insert_log(bot_id, event_type, source_ip="127.0.0.1", payload_size=0, beacon_interval=None, metadata=None, db_path=None):
    """
    This function is called everytime a bot talks to the C2 server.
    """

    connection = get_connection(db_path)

    connection.execute(
        """
        INSERT INTO traffic_logs(
        timestamp, bot_id, event_type, source_ip, payload_size, beacon_interval, metadata
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(tz=timezone.utc).isoformat(),
            bot_id,
            event_type,
            source_ip,
            payload_size,
            beacon_interval,
            json.dumps(metadata or {}),
        ),
    )

    connection.commit()

    connection.close()


#get all logs for specific bot
def get_logs_by_bot(bot_id, db_path = None):
    connection = get_connection(db_path)

    rows = connection.execute("SELECT * FROM traffic_logs WHERE bot_id = ? ORDER BY timestamp", (bot_id,),).fetchall()

    connection.close()

    lst = []
    for row in rows:
        lst.append(dict(row))
    
    return lst

#get all logs
def get_all_logs(limit = 1000, db_path = None):
    connection = get_connection(db_path)

    rows = connection.execute("SELECT * FROM traffic_logs ORDER BY timestamp DESC LIMIT ?", (limit,),).fetchall()

    connection.close()

    lst = []

    for row in rows:
        lst.append(dict(row))
    
    return lst

def get_unique_bots(db_path=None):

    connection  = get_connection(db_path)

    rows = connection.execute("SELECT DISTINCT bot_id FROM traffic_logs").fetchall()

    connection.close()
    lst = []
    for row in rows:
        lst.append(row["bot_id"])

    return lst

#get beacon intervals for a specific bot
def get_bot_checkin_intervals(bot_id, db_path=None):

    connection = get_connection(db_path)

    rows = connection.execute(
        """
        SELECT beacon_interval FROM traffic_logs 
        WHERE bot_id = ? AND beacon_interval IS NOT NULL
        ORDER BY timestamp
        """,
        (bot_id,),
    ).fetchall()

    connection.close()

    lst = []

    for row in rows:
        lst.append(row["beacon_interval"])
    
    return lst