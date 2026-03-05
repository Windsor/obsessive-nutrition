#!/usr/bin/env python3
"""
r2d2 Server Recovery Watcher
Checks if r2d2 (192.168.68.139) is back online.
Writes alert to a file when server recovers.
Run periodically via LaunchAgent or cron.
"""

import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path

SERVER_IP = "192.168.68.139"
STATE_FILE = Path(__file__).parent / "state.json"
ALERT_FILE = Path(__file__).parent / "alert.json"

CHECKS = [
    {"name": "Project Tracker", "url": f"http://{SERVER_IP}:3001/api/health", "critical": True},
    {"name": "Ghost PT", "url": f"http://{SERVER_IP}:2368", "critical": True},
    {"name": "Ghost Finance", "url": f"http://{SERVER_IP}:2370", "critical": True},
    {"name": "Quiz Generator", "url": f"http://{SERVER_IP}:5000", "critical": False},
    {"name": "Social Poster", "url": f"http://{SERVER_IP}:5555/health", "critical": False},
]


def check_service(url: str, timeout: int = 5) -> bool:
    try:
        req = urllib.request.Request(url)
        urllib.request.urlopen(req, timeout=timeout)
        return True
    except Exception:
        return False


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_status": "unknown", "down_since": None, "checks": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def main():
    state = load_state()
    state["checks"] = state.get("checks", 0) + 1
    now = datetime.now().isoformat()

    results = {}
    any_up = False
    for check in CHECKS:
        ok = check_service(check["url"])
        results[check["name"]] = ok
        if ok:
            any_up = True

    if any_up and state.get("last_status") != "up":
        # Server recovered!
        down_since = state.get("down_since", "unknown")
        alert = {
            "event": "r2d2_recovered",
            "timestamp": now,
            "down_since": down_since,
            "services": results,
            "message": f"🟢 r2d2 is back online! Services: {sum(results.values())}/{len(results)} up"
        }
        ALERT_FILE.write_text(json.dumps(alert, indent=2))
        print(f"🟢 RECOVERED: {alert['message']}")
        state["last_status"] = "up"
        state["down_since"] = None
    elif not any_up:
        if state.get("last_status") != "down":
            state["down_since"] = now
        state["last_status"] = "down"
        print(f"🔴 r2d2 still down (check #{state['checks']})")
    else:
        state["last_status"] = "up"
        print(f"🟢 r2d2 up: {sum(results.values())}/{len(results)} services")

    state["last_check"] = now
    state["last_results"] = results
    save_state(state)


if __name__ == "__main__":
    main()
