# High-Level Design Document

## 1. System Overview

This system simulates C2 botnet communication and provides automated detection of malicious beacon patterns. It is designed for security research and as a training environment for adversarial ML agents.

## 2. Components

### 2.1 C2 Server (src/server/app.py)
- **Technology**: FastAPI + Uvicorn
- **Responsibilities**: Accept bot checkins, issue commands, log all traffic
- **Endpoints**:
  - POST /checkin — Bot heartbeat with beacon interval tracking
  - GET /command/{bot_id} — Command distribution
  - POST /result — Command output collection
  - GET /api/logs, /api/bots — Detection pipeline data access
- **State**: In-memory tracking of last checkin times and command queues

### 2.2 Bot Simulator (src/bots/bot.py)
- **Technology**: asyncio + httpx
- **Responsibilities**: Simulate concurrent bot agents with configurable beacon behavior
- **Configuration**: YAML-driven (interval, jitter, payload size, bot type)
- **Concurrency**: All bots run in a single process via asyncio tasks

### 2.3 Database Layer (src/db/database.py)
- **Technology**: SQLite3
- **Schema**: traffic_logs table with timestamp, bot_id, event_type, source_ip, payload_size, beacon_interval, metadata
- **Indexes**: bot_id, timestamp for query performance

### 2.4 Detection Pipeline (src/detection/detector.py)
- **Technology**: Pure Python (no ML dependencies)
- **Methods**:
  - Beacon regularity: Coefficient of Variation analysis
  - Payload consistency: CV of payload sizes
  - Frequency analysis: Checkins per hour
- **Scoring**: Weighted combination with configurable thresholds

## 3. Data Flow

1. Bot simulator reads config from YAML
2. Bots send periodic HTTP checkins to C2 server
3. Server calculates beacon intervals and logs to SQLite
4. Detection pipeline queries database, analyzes each bot
5. Bots exceeding suspicion threshold are flagged

## 4. Deployment

- **Local**: Direct Python execution
- **Docker**: Multi-container setup via Docker Compose (server, bots, detector)
- **Cloud**: AWS EC2 free tier (server), local bots pointing at public IP
- **CI/CD**: GitHub Actions runs pytest on every push

## 5. Security Note

This tool is for educational and research purposes only. The C2 simulation runs in a controlled environment and does not interact with any real systems.

## 6. Future Work

- Wrap simulation as OpenAI Gymnasium environment for RL training
- Multi-agent RL swarm for autonomous botnet disruption
- DNS tunneling and domain generation algorithm simulation
- Real-time detection dashboard