# C2 Botnet Traffic Simulator & Detection System

A full-stack security research tool that simulates Command-and-Control (C2) botnet infrastructure and detects malicious beacon patterns using statistical anomaly detection.

## Architecture
```
Bot Simulator ──→ C2 Server (FastAPI) ──→ SQLite Database ──→ Detection Pipeline (Beacon Analysis)              
```

## Components

- **C2 Server** — FastAPI REST API simulating an attacker's command-and-control server. Logs all bot interactions to SQLite.
- **Bot Simulator** — Async Python agents simulating both malicious (regular beacon) and benign (irregular) network clients.
- **Detection Pipeline** — Statistical analyzer using coefficient of variation on beacon intervals, payload sizes, and checkin frequency to flag suspicious bots.
- **SQLite Database** — Stores timestamped traffic logs with beacon intervals, payload sizes, and metadata.

## Detection Methodology

The detector analyzes three signals per bot:

| Signal | Method | Suspicious When |
|--------|--------|----------------|
| Beacon regularity | Coefficient of Variation (std/mean) | CV < 0.15 (very regular) |
| Payload consistency | CV of checkin payload sizes | CV < 0.10 (uniform sizes) |
| Checkin frequency | Checkins per hour | > 100/hr |

Scores are weighted (50% beacon, 30% payload, 20% frequency) and bots exceeding 0.6 combined score are flagged.

## Quick Start

### Local
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Terminal 1: Start server
uvicorn src.server.app:app --reload --port 8000

# Terminal 2: Launch bots
python -m src.bots.bot

# Terminal 3: Run detection (after 2-3 min)
python -m src.detection.detector
```

### Docker
```bash
docker compose up --build -d
docker compose logs -f
docker compose --profile detect run detector
docker compose down
```

### AWS
Deploy the server on EC2, point bots at the public IP. See docs/HLD.md for details.

## Testing
```bash
python -m pytest tests/ -v
```

14 tests covering database operations, beacon detection accuracy, payload analysis, and full pipeline integration.

## Tech Stack

Python, FastAPI, SQLite, Docker, Docker Compose, GitHub Actions CI, AWS EC2, pytest, YAML configuration

## Configuration

- `config/bots.yaml` — Bot parameters (intervals, jitter, types)
- `config/detection.yaml` — Detection thresholds and scoring weights