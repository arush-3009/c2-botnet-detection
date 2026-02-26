import yaml
import math
from pathlib import Path
from datetime import datetime
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

def analyze_payload(logs, config):
    result = {
        "suspicious": False,
        "score": 0.0,
        "cv": None,
    }

    # payload sizes from checkin events only
    sizes = []
    for log in logs:
        if log["event_type"] == "checkin":
            sizes.append(log["payload_size"])

    if len(sizes) < 3:

        return result

    mean = sum(sizes) / len(sizes)

    if mean == 0:
        return result

    variance = sum((x - mean) ** 2 for x in sizes) / len(sizes)
    std_dev = math.sqrt(variance)

    cv = std_dev / mean

    result["cv"] = round(cv, 4)

    threshold = config["payload"]["cv_threshold"]

    if cv < threshold:
        result["suspicious"] = True

        result["score"] = min(1.0, 1.0 - (cv / threshold))
    else:
        result["score"] = max(0.0, 1.0 - (cv / threshold))

    return result


def analyze_frequency(logs, config):
    result = {
        "suspicious": False,
        "score": 0.0,
        "checkins_per_hour": None,
    }

    checkins = []

    for log in logs:
        if log["event_type"] == "checkin":
            checkins.append(log)


    if len(checkins) < 2:
        return result


    first = checkins[0]["timestamp"]
    last = checkins[-1]["timestamp"]

    # Parse timestamps and get hours difference
    
    t_first = datetime.fromisoformat(first)
    t_last = datetime.fromisoformat(last)
    hours = (t_last - t_first).total_seconds() / 3600

    if hours == 0:

        return result

    rate = len(checkins) / hours

    result["checkins_per_hour"] = round(rate, 2)

    max_rate = config["frequency"]["max_checkins_per_hour"]

    if rate > max_rate:

        result["suspicious"] = True

        result["score"] = min(1.0, rate / max_rate)
    else:
        result["score"] = rate / max_rate

    return result



def analyze_bot(bot_id, config, db_path=None):

    intervals = get_bot_checkin_intervals(bot_id, db_path=db_path)

    logs = get_logs_by_bot(bot_id, db_path=db_path)

    #get different results
    beacon_result = analyze_beacon(intervals, config)
    payload_result = analyze_payload(logs, config)
    frequency_result = analyze_frequency(logs, config)

    # weighted combined score
    weights = config["scoring"]

    combined_score = (
        beacon_result["score"] * weights["beacon_weight"] + payload_result["score"] * weights["payload_weight"] + frequency_result["score"] * weights["frequency_weight"]
    )

    return {
        "bot_id": bot_id,
        "suspicious": combined_score >= weights["alert_threshold"],
        "combined_score": round(combined_score, 4),
        "beacon_analysis": beacon_result,
        "payload_analysis": payload_result,
        "frequency_analysis": frequency_result,
    }


def run_detection(config_path=None, db_path=None):

    config = load_detection_config(config_path)

    bots = get_unique_bots(db_path=db_path)

    print(f"\n{'='*60}")
    print(f"C2 BEACON DETECTION REPORT")
    print(f"Analyzing {len(bots)} bots...")
    print(f"{'='*60}\n")

    results = []

    for bot_id in bots:

        result = analyze_bot(bot_id, config, db_path=db_path)

        results.append(result)

        if result["suspicious"]:
            status = "SUSPICIOUS"
        else:
            status = "CLEAN"


        print(f"{status}    {bot_id}")
        print(f"Combined Score: {result['combined_score']}")
        print(f"Beacon CV: {result['beacon_analysis']['cv']} (mean interval: {result['beacon_analysis']['mean_interval']}s)")
        print(f"Payload CV: {result['payload_analysis']['cv']}")
        print(f"Frequency: {result['frequency_analysis']['checkins_per_hour']} checkins/hr")
        print()

    suspicious = []
    clean = []
    for r in results:
        if r["suspicious"]:
            suspicious.append(r)
        else:
            clean.append(r)

    print(f"{'='*60}")
    print(f"SUMMARY: {len(suspicious)} suspicious, {len(clean)} clean")
    print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    run_detection()