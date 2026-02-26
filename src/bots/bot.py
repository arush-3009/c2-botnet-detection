import asyncio
import random
import yaml
import httpx
from pathlib import Path

def load_config(config_path=None):
    if config_path is not None:
        path = config_path
    else:
        path = str(Path(__file__).parent.parent.parent / "config" / "bots.yaml")
    
    with open(path, "r") as f:
        return yaml.safe_load(f)
    
async def run_bot(bot_config, server_url):
    bot_id = bot_config["bot_id"]
    interval = bot_config["beacon_interval"]
    jitter = bot_config["jitter"]
    payload_size = bot_config["payload_size"]
    bot_type = bot_config["type"]

    print(f"[{bot_id}] Starting ({bot_type}) - interval = {interval}s, jitter = ±{jitter}s")

    async with httpx.AsyncClient() as client:

        while True:
            sleep_time = max(1, interval + random.uniform(-jitter, jitter))

            await asyncio.sleep(sleep_time)

            # checkin
            try:
                resp = await client.post(
                    f"{server_url}/checkin",
                    json={
                        "bot_id": bot_id,
                        "source_ip": f"192.168.1.{random.randint(10, 250)}",
                        "payload_size": payload_size,
                        "metadata": {"type": bot_type},
                    },
                )
                data = resp.json()
                print(f"[{bot_id}] Checkin OK - interval_logged: {data.get('interval_logged')}")
            except Exception as e:
                print(f"[{bot_id}] Checkin FAILED: {e}")
                continue

            # ask for commands
            try:
                resp = await client.get(f"{server_url}/command/{bot_id}")
                cmd_data = resp.json()

                if cmd_data["status"] == "command":
                    print(f"[{bot_id}] Got command: {cmd_data['command']}")

                    # execute command and report result
                    await client.post(
                        f"{server_url}/result",
                        json={
                            "bot_id": bot_id,
                            "command_id": cmd_data["command"].get("id", "unknown"),
                            "output": f"Executed: {cmd_data['command']}",
                            "source_ip": f"192.168.1.{random.randint(10, 250)}",
                        },
                    )
            except Exception as e:
                print(f"[{bot_id}] Command fetch FAILED: {e}")
