# Finance Publisher — Daily Finance Pulse

Automated financial newsletter publishing to Ghost CMS.

## Architecture

- **Ghost CMS:** http://192.168.68.139:2370 (systemd: `ghost-finance`, DB: `ghost_finance`)
- **Admin API Key:** `6998e826bb07b687f6c5a2b1:224fbf8e1b29fe60ba40410532d0f8e968c32e82b97a558db6adad1c58a72906`
- **Content API Key:** `495686c7f28fa54a5dea9d13eb`
- **Server scripts:** `~/finance-publisher/` on r2d2

## Data Sources

- **CoinGecko:** BTC, ETH, SOL, XRP, ADA + top 100 movers
- **Yahoo Finance (yfinance):** S&P 500, NASDAQ, STOXX 600, Nikkei 225, PSI-20, EUR/USD, GBP/USD, DXY, Gold, Silver, Oil, Nat Gas, US 10Y Yield, VIX
- **Alternative.me:** Crypto Fear & Greed Index

## Scripts

- `config.py` — Configuration and asset lists
- `data_pipeline.py` — Fetches all market data
- `template.py` — Generates Ghost-ready HTML
- `publish.py` — Orchestrates fetch → template → publish

## Usage

```bash
cd ~/finance-publisher
python3 publish.py              # Publish live
python3 publish.py --draft      # Publish as draft
python3 publish.py --dry-run    # Preview without publishing
python3 publish.py --data-only  # Just fetch data (JSON)
```

## Cron

Daily at 7:00 AM Lisbon time via OpenClaw cron job.

## Dependencies

- Python 3, requests, yfinance, PyJWT
