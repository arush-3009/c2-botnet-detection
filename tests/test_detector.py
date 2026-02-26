import os
import tempfile
import pytest
import random
from src.db.database import init_db, insert_log
from src.detection.detector import analyze_beacon, analyze_payload, analyze_frequency,analyze_bot, load_detection_config


@pytest.fixture
def config():
    return load_detection_config()


@pytest.fixture
def tmp_db():

    fd, path = tempfile.mkstemp(suffix=".db")

    os.close(fd)

    init_db(db_path=path)

    yield path

    os.unlink(path)


def test_beacon_regular_is_suspicious(config):
    #flagged
    intervals = [60.1, 59.8, 60.3, 59.9, 60.0, 60.2]

    result = analyze_beacon(intervals, config)

    assert result["suspicious"] is True
    assert result["score"] > 0.5


def test_beacon_irregular_is_clean(config):
    #clean
    intervals = [30.0, 180.0, 45.0, 200.0, 10.0, 150.0]

    result = analyze_beacon(intervals, config)

    assert result["suspicious"] is False


def test_beacon_insufficient_samples(config):
    # can't determine due to too few samples
    intervals = [60.0]

    result = analyze_beacon(intervals, config)

    assert result["suspicious"] is False
    assert result["score"] == 0.0


def test_payload_uniform_is_suspicious(config):

    logs = []

    for i in range(10):
        logs.append({"event_type": "checkin", "payload_size": 128})
    
    result = analyze_payload(logs, config)

    assert result["suspicious"] is True


def test_payload_varied_is_clean(config):

    sizes = [128, 512, 64, 1024, 256, 32, 768, 100, 900, 50]
    logs = []
    for s in sizes:
        logs.append({"event_type": "checkin", "payload_size": s})
    
    result = analyze_payload(logs, config)

    assert result["suspicious"] is False


def test_frequency_high_rate(config):
    from datetime import datetime, timedelta, timezone

    base = datetime(2026, 1, 1, tzinfo=timezone.utc)

    # 120 checkins in 1 hour --> i.e. very high frequency
    logs = []
    for i in range(120):
        logs.append({
            "event_type": "checkin",
            "timestamp": (base + timedelta(seconds=i * 30)).isoformat(),
        })

    result = analyze_frequency(logs, config)

    assert result["checkins_per_hour"] > 100


def test_full_pipeline_malicious(config, tmp_db):
    # malicious bot with regular intervals

    for i in range(10):

        insert_log(
            bot_id="test_mal",
            event_type="checkin",
            payload_size=128,
            beacon_interval=60.0 + (i % 3) * 0.5,
            db_path=tmp_db,
        )

    result = analyze_bot("test_mal", config, db_path=tmp_db)

    assert result["suspicious"] is True


def test_full_pipeline_benign(config, tmp_db):
    
    for i in range(10):

        insert_log(
            bot_id="test_benign",
            event_type="checkin",
            payload_size=random.randint(50, 2000),
            beacon_interval=random.uniform(10, 300),
            db_path=tmp_db,
        )

    result = analyze_bot("test_benign", config, db_path=tmp_db)
    
    assert result["suspicious"] is False