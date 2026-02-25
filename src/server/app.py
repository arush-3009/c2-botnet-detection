from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from src.db.database import init_db, insert_log, get_all_logs, get_logs_by_bot, get_unique_bots

app = FastAPI(title="C2 Server Simulation")

init_db()