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

def analyze_beacon(intervals, config):
    result = {
        "suspicious": False,
        "score": 0.0,
        "mean_interval": None,
        "std_dev": None,
        "cv": None,
        "sample_count": len(intervals),
    }

    min_samples = config["beacon"]["min_samples"]

    if len(intervals) < min_samples:
        return result


    mean = sum(intervals) / len(intervals)


    variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
    std_dev = math.sqrt(variance)

    # coefficient of variation
    if mean > 0:
        cv = std_dev / mean
    else:
        cv = 0


    result["mean_interval"] = round(mean, 2)
    result["std_dev"] = round(std_dev, 2)
    result["cv"] = round(cv, 4)

    # lower CV --> more regular --> more suspicious
    # invert into 0-1 score where 1 = maximum suspicion

    threshold = config["beacon"]["cv_threshold"]
    
    if cv < threshold:
        result["suspicious"] = True
        result["score"] = min(1.0, 1.0 - (cv / threshold))

    else:
        result["score"] = max(0.0, 1.0 - (cv / threshold))

    return result