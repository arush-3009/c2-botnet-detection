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


#tracking bot state - last check in time and what commands are queued for it
last_checkin: dict[str, datetime] = {}
command_queue: dict[str, list[dict]] = {}

@app.post("/checkin")
def checkin(request: CheckinRequest):

    now = datetime.now(tz=timezone.utc)

    #calculate beacon interval
    interval = None
    if request.bot_id in last_checkin:
        diff = now - last_checkin[request.bot_id]
        interval = diff.total_seconds()
    
    last_checkin[request.bot_id] = now

    #log
    insert_log(
        bot_id = request.bot_id,
        event_type = "checkin",
        source_ip = request.source_ip,
        payload_size=request.payload_size,
        beacon_interval = interval,
        metadata = request.metadata 
    )

    return {"status": "ok", "bot_id": request.bot_id, "interval_logged": interval}

@app.get("/command/{bot_id}")
def get_command(bot_id):

    if bot_id in command_queue and command_queue[bot_id]:

        cmd = command_queue[bot_id].pop(0)

        insert_log(
            bot_id = bot_id,
            event_type = "command",
            payload_size = len(str(cmd)),
            metadata = cmd
        )

        return {"status": "command", "command": cmd}
    
    return {"status": "idle"}

@app.post("/result")
def post_result(request: CommandResultRequest):
    insert_log(
        bot_id = request.bot_id,
        event_type="result",
        source_ip=request.source_ip,
        payload_size=len(request.output),
        metadata={"command_id": request.command_id, "output": request.output},
    )
    return {"status": "received", "command_id": request.command_id}