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
    
