# Samsung Frame TV Dashboard

Generates and displays an info dashboard on the Samsung Frame TV.

## Files
- `dashboard.py` — Main dashboard generator (weather, crypto, markets, news)
- `update-dashboard.sh` — Shell wrapper for LaunchAgent
- `state.json` — Persistent state (last update time, etc.)
- `backgrounds/` — Background images

## Data Sources
- Open-Meteo — Weather for Braga, Portugal
- CoinGecko — Crypto prices (BTC, ETH)
- Yahoo Finance — Market indices
- The Portugal Brief Ghost API — Latest news headlines

## Layout
Time 1/3 | Weather 2/3 // Crypto 1/2 | Markets 1/2 // News full width (8 headlines)

## Schedule
LaunchAgent `com.openclaw.frame-dashboard.plist` — runs every 15 minutes, active hours 7am–10pm.

## TV Config
- IP: 192.168.68.151
- Library: samsungtvws (Python 3.9)
