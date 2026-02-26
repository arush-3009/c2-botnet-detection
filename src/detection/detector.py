import yaml
import math
from pathlib import Path
from src.db.database import get_unique_bots, get_bot_checkin_intervals, get_logs_by_bot


def load_detection_config(config_path=None):
    if config_path is not None:
        path = config_path
    else:
        path = str(Path(__file__).parent.parent.parent / "config" / "detection.yaml")

    with open(path, "r") as f:
        return yaml.safe_load(f)