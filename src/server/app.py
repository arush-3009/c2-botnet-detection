from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from src.db.database import init_db, insert_log, get_all_logs, get_logs_by_bot, get_unique_bots

app = FastAPI(title="C2 Server Simulation")

init_db()

#define what the data that the bots send should look like
class CheckinRequest(BaseModel):
    bot_id: str
    source_ip: str = "127.0.0.1"
    payload_size: int = 0
    metadata: dict = {}

class CommandResultRequest(BaseModel):
    bot_id: str
    command_id: str
    output: str
    source_ip: str = "127.0.0.1"