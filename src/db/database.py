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