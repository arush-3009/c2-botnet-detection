import os
import tempfile
import pytest
from src.db.database import init_db, insert_log, get_logs_by_bot, get_all_logs, get_unique_bots, get_bot_checkin_intervals



@pytest.fixture
def tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")

    os.close(fd)

    init_db(db_path=path)

    yield path

    os.unlink(path)


def test_init_creates_table(tmp_db):

    init_db(db_path=tmp_db)


def test_insert_and_retrieve(tmp_db):

    insert_log(
        bot_id="bot_001",
        event_type="checkin",
        source_ip="192.168.1.10",
        payload_size=128,
        beacon_interval=60.5,
        metadata={"status": "active"},
        db_path=tmp_db,
    )

    logs = get_logs_by_bot("bot_001", db_path=tmp_db)

    assert len(logs) == 1

    assert logs[0]["bot_id"] == "bot_001"
    assert logs[0]["event_type"] == "checkin"
    assert logs[0]["source_ip"] == "192.168.1.10"
    assert logs[0]["payload_size"] == 128
    assert logs[0]["beacon_interval"] == 60.5


def test_multiple_bots(tmp_db):

    insert_log(bot_id="bot_001", event_type="checkin", db_path=tmp_db)
    insert_log(bot_id="bot_002", event_type="checkin", db_path=tmp_db)
    insert_log(bot_id="bot_001", event_type="command", db_path=tmp_db)

    assert len(get_logs_by_bot("bot_001", db_path=tmp_db)) == 2
    assert len(get_logs_by_bot("bot_002", db_path=tmp_db)) == 1


def test_get_unique_bots(tmp_db):

    insert_log(bot_id="bot_001", event_type="checkin", db_path=tmp_db)
    insert_log(bot_id="bot_002", event_type="checkin", db_path=tmp_db)
    
    insert_log(bot_id="bot_001", event_type="checkin", db_path=tmp_db)

    assert sorted(get_unique_bots(db_path=tmp_db)) == ["bot_001", "bot_002"]


def test_get_checkin_intervals(tmp_db):

    insert_log(bot_id="bot_001", event_type="checkin", beacon_interval=60.2, db_path=tmp_db)

    insert_log(bot_id="bot_001", event_type="checkin", beacon_interval=58.7, db_path=tmp_db)
    insert_log(bot_id="bot_001", event_type="command", beacon_interval=None, db_path=tmp_db)

    assert get_bot_checkin_intervals("bot_001", db_path=tmp_db) == [60.2, 58.7]


def test_get_all_logs_limit(tmp_db):

    for i in range(10):

        insert_log(bot_id=f"bot_{i:03d}", event_type="checkin", db_path=tmp_db)

    assert len(get_all_logs(limit=5, db_path=tmp_db)) == 5