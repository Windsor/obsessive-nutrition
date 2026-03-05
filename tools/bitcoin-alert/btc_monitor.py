#!/usr/bin/env python3
"""
BTC Price Monitor — Tracks Bitcoin price and alerts on significant moves.
Runs every 5 minutes via LaunchAgent.
Alerts are written to a file for OpenClaw to pick up during heartbeats.
"""

import json
import urllib.request
import os
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = Path(__file__).parent / "state.json"
ALERT_FILE = Path(__file__).parent / "alerts.json"

# Thresholds
ALERT_PERCENT_1H = 3.0    # Alert if BTC moves >3% in 1 hour
ALERT_PERCENT_24H = 7.0   # Alert if BTC moves >7% in 24 hours
PRICE_ALERTS = []          # Static price alerts, e.g. [100000, 90000, 80000]

def get_btc_price():
    """Fetch BTC price from CoinGecko"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_1h_change=true"
    headers = {"Accept": "application/json", "User-Agent": "btc-monitor/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            btc = data.get("bitcoin", {})
            return {
                "price": btc.get("usd", 0),
                "change_24h": btc.get("usd_24h_change", 0),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Error fetching price: {e}", file=sys.stderr)
        return None

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {"last_price": 0, "last_alert_time": "", "price_history": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def add_alert(message, price):
    """Add alert to alerts file for OpenClaw to process"""
    alerts = []
    if ALERT_FILE.exists():
        try:
            alerts = json.loads(ALERT_FILE.read_text())
        except:
            pass
    
    alerts.append({
        "message": message,
        "price": price,
        "timestamp": datetime.now().isoformat(),
        "read": False
    })
    
    # Keep last 50 alerts
    alerts = alerts[-50:]
    ALERT_FILE.write_text(json.dumps(alerts, indent=2))

def main():
    data = get_btc_price()
    if not data or data["price"] == 0:
        print("Failed to get price")
        return
    
    price = data["price"]
    change_24h = data.get("change_24h", 0) or 0
    state = load_state()
    
    # Track price history (keep last 12 entries = 1 hour at 5min intervals)
    history = state.get("price_history", [])
    history.append({"price": price, "time": data["timestamp"]})
    history = history[-12:]
    
    # Calculate 1h change if we have enough history
    alerts_triggered = []
    
    if len(history) >= 2:
        oldest_price = history[0]["price"]
        if oldest_price > 0:
            pct_change_1h = ((price - oldest_price) / oldest_price) * 100
            if abs(pct_change_1h) >= ALERT_PERCENT_1H:
                # Cooldown: only alert once per 30 min for 1h change
                last_1h_alert = state.get("last_1h_alert_time", "")
                cooldown_ok = True
                if last_1h_alert:
                    try:
                        last_dt = datetime.fromisoformat(last_1h_alert)
                        elapsed = (datetime.now() - last_dt).total_seconds()
                        cooldown_ok = elapsed >= 1800  # 30 minutes
                    except:
                        pass
                if cooldown_ok:
                    direction = "📈" if pct_change_1h > 0 else "📉"
                    msg = f"{direction} BTC {pct_change_1h:+.1f}% in ~1h: ${price:,.0f}"
                    alerts_triggered.append(msg)
                    state["last_1h_alert_time"] = datetime.now().isoformat()
    
    # 24h change alert
    if abs(change_24h) >= ALERT_PERCENT_24H:
        direction = "🚀" if change_24h > 0 else "💥"
        msg = f"{direction} BTC {change_24h:+.1f}% in 24h: ${price:,.0f}"
        alerts_triggered.append(msg)
    
    # Static price level alerts
    last_price = state.get("last_price", 0)
    if last_price > 0:
        for level in PRICE_ALERTS:
            if (last_price < level <= price) or (last_price > level >= price):
                direction = "above" if price >= level else "below"
                msg = f"⚡ BTC crossed ${level:,.0f} ({direction}): ${price:,.0f}"
                alerts_triggered.append(msg)
    
    # Write alerts
    for alert_msg in alerts_triggered:
        print(f"ALERT: {alert_msg}")
        add_alert(alert_msg, price)
    
    # Update state
    state["last_price"] = price
    state["price_history"] = history
    state["last_check"] = data["timestamp"]
    state["last_24h_change"] = change_24h
    save_state(state)
    
    print(f"BTC: ${price:,.0f} ({change_24h:+.1f}% 24h)")

if __name__ == "__main__":
    main()
