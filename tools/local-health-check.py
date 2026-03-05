#!/usr/bin/env python3
"""
Local Mac Mini Health Check
Checks all LaunchAgents and local services.
"""

import subprocess
import json
import urllib.request
from datetime import datetime


def check_launchagent(label):
    """Check if a LaunchAgent is loaded and running."""
    try:
        out = subprocess.check_output(["launchctl", "list"], text=True)
        for line in out.strip().split("\n"):
            if label in line:
                parts = line.split("\t")
                pid = parts[0].strip()
                exit_code = parts[1].strip()
                return {
                    "loaded": True,
                    "pid": pid if pid != "-" else None,
                    "exit_code": int(exit_code) if exit_code != "-" else None,
                    "running": pid != "-"
                }
        return {"loaded": False, "pid": None, "exit_code": None, "running": False}
    except Exception as e:
        return {"loaded": False, "error": str(e)}


def check_http(url, timeout=5):
    """Check if an HTTP endpoint responds."""
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=timeout)
        return {"status": resp.status, "ok": True}
    except Exception as e:
        return {"status": None, "ok": False, "error": str(e)}


def main():
    print(f"=== Local Health Check — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    # LaunchAgents
    agents = {
        "OpenClaw Gateway": "ai.openclaw.gateway",
        "HA Proxy": "com.openclaw.ha-proxy",
        "BTC Monitor": "com.openclaw.btc-monitor",
        "Frame Dashboard": "com.openclaw.frame-dashboard",
        "r2d2 Watcher": "com.openclaw.r2d2-watcher",
    }

    print("LaunchAgents:")
    for name, label in agents.items():
        info = check_launchagent(label)
        status = "✅ running" if info.get("running") else ("⚠️ loaded (not running)" if info.get("loaded") else "❌ not loaded")
        pid = f" (PID {info['pid']})" if info.get("pid") else ""
        print(f"  {name}: {status}{pid}")

    # HTTP services
    print("\nHTTP Services:")
    services = {
        "HA Proxy": "http://localhost:8199/health",
        "Home Assistant": "http://192.168.68.138:8123",
        "r2d2 Project Tracker": "http://192.168.68.139:3001",
        "r2d2 Ghost PT": "http://192.168.68.139:2368",
        "r2d2 Ghost Finance": "http://192.168.68.139:2370",
    }

    for name, url in services.items():
        info = check_http(url)
        status = f"✅ {info['status']}" if info["ok"] else "❌ down"
        print(f"  {name}: {status}")

    # BTC state
    from pathlib import Path
    btc_state = Path(__file__).parent / "bitcoin-alert/state.json"
    if btc_state.exists():
        try:
            state = json.loads(btc_state.read_text())
            price = state.get("last_price", 0)
            last = state.get("last_check", "unknown")
            print(f"\nBTC: ${price:,.0f} (last check: {last})")
        except:
            pass

    # r2d2 recovery alert
    alert_file = Path(__file__).parent / "r2d2-watcher/alert.json"
    if alert_file.exists():
        alert = json.loads(alert_file.read_text())
        print(f"\n🔔 r2d2 RECOVERY ALERT: {alert.get('message', 'recovered')}")

    print()


if __name__ == "__main__":
    main()
