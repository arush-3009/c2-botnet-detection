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

