# Lifeweb Server Uptime Monitor

Monitors a BYOND server and alerts when it comes online.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python pinger.py`

## Building EXE
```
pyinstaller --onefile --windowed pinger.py
```