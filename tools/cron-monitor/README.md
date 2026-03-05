# Cron Job Monitor

Monitors that Portugal Brief publish cron jobs run successfully.

## What It Checks
1. **OpenClaw cron jobs** — Last run status/time for morning (7am) and afternoon (2pm) editions
2. **Ghost posts today** — Verifies posts were actually published to Ghost CMS
3. **Service health** — Ghost, Project Tracker, Quiz Generator, Social Poster

## How It Works
- `monitor.py` — Standalone script checking Ghost API and service health
- The agent checks cron job status during heartbeats using the `cron list` tool
- If a publish job shows `lastStatus: "error"`, the agent should alert Glenn

## Monitoring Checklist (for HEARTBEAT.md)
After 7:30am: Check morning edition ran (cron list → Portugal Brief Morning job lastStatus)
After 2:30pm: Check afternoon edition ran (cron list → Portugal Brief Afternoon job lastStatus)
If either failed: Message Glenn with the error details

## Manual Check
```bash
python3 tools/cron-monitor/monitor.py
```
