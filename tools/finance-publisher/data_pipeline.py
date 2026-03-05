#!/usr/bin/env python3
"""
Financial Data Pipeline — pulls market data from CoinGecko + Yahoo Finance.
Returns structured dict for template rendering.
"""

import requests
import time
from datetime import datetime, timezone
from config import CRYPTO, ALL_TICKERS, COINGECKO_BASE

from log_config import get_logger
log = get_logger("data_pipeline")

HEADERS = {"User-Agent": "Mozilla/5.0 (finance-newsletter/1.0)"}


def fetch_crypto():
    """Fetch crypto prices, 24h change, and market cap from CoinGecko."""
    ids = ",".join(CRYPTO.keys())
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ids,
        "order": "market_cap_desc",
        "sparkline": "false",
        "price_change_percentage": "24h,7d",
    }
    try:
        for attempt in range(3):
            r = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                log.info(f" CoinGecko rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            break
        else:
            print("[WARN] CoinGecko: max retries exceeded")
            return {}
        data = r.json()
        result = {}
        for coin in data:
            symbol = coin["symbol"].upper()
            result[symbol] = {
                "name": coin["name"],
                "price": coin["current_price"],
                "change_24h": coin.get("price_change_percentage_24h", 0) or 0,
                "change_7d": coin.get("price_change_percentage_7d_in_currency", 0) or 0,
                "market_cap": coin.get("market_cap", 0),
                "volume_24h": coin.get("total_volume", 0),
            }
        return result
    except Exception as e:
        log.warning(f" CoinGecko error: {e}")
        return {}


def fetch_fear_greed():
    """Fetch Bitcoin Fear & Greed Index from alternative.me."""
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        r.raise_for_status()
        data = r.json()["data"][0]
        return {
            "value": int(data["value"]),
            "label": data["value_classification"],
        }
    except Exception as e:
        log.warning(f" Fear & Greed error: {e}")
        return {"value": 50, "label": "Neutral"}


def fetch_yahoo_quotes(tickers: dict):
    """Fetch quotes using yfinance library."""
    try:
        import yfinance as yf
        symbols = list(tickers.keys())
        data = yf.download(symbols, period="2d", progress=False, threads=True)
        
        results = {}
        for sym, label in tickers.items():
            try:
                if len(symbols) > 1:
                    close_today = data["Close"][sym].dropna().iloc[-1]
                    close_prev = data["Close"][sym].dropna().iloc[-2] if len(data["Close"][sym].dropna()) > 1 else close_today
                else:
                    close_today = data["Close"].dropna().iloc[-1]
                    close_prev = data["Close"].dropna().iloc[-2] if len(data["Close"].dropna()) > 1 else close_today
                
                change_pct = ((close_today - close_prev) / close_prev * 100) if close_prev else 0
                results[label] = {
                    "price": float(close_today),
                    "change_pct": float(change_pct),
                    "prev_close": float(close_prev),
                }
            except Exception as e:
                log.warning(f" Ticker {sym} ({label}): {e}")
        return results
    except Exception as e:
        log.warning(f" yfinance error: {e}")
        return {}


def fetch_top_crypto_movers():
    """Fetch top gainers and losers from CoinGecko top 100."""
    try:
        url = f"{COINGECKO_BASE}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h",
        }
        for attempt in range(3):
            r = requests.get(url, params=params, headers=HEADERS, timeout=15)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                log.info(f" CoinGecko movers rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            break
        else:
            return {"gainers": [], "losers": []}
        data = r.json()
        
        sorted_by_change = sorted(data, key=lambda x: x.get("price_change_percentage_24h") or 0)
        losers = sorted_by_change[:3]
        gainers = sorted_by_change[-3:][::-1]
        
        def fmt(coin):
            return {
                "symbol": coin["symbol"].upper(),
                "name": coin["name"],
                "price": coin["current_price"],
                "change_24h": coin.get("price_change_percentage_24h", 0) or 0,
            }
        
        return {
            "gainers": [fmt(c) for c in gainers],
            "losers": [fmt(c) for c in losers],
        }
    except Exception as e:
        log.warning(f" Top movers error: {e}")
        return {"gainers": [], "losers": []}


def collect_all_data():
    """Main function — collects all market data and returns structured dict."""
    log.info("Fetching crypto data...")
    crypto = fetch_crypto()
    time.sleep(1)  # CoinGecko rate limit
    
    log.info("Fetching top movers...")
    movers = fetch_top_crypto_movers()
    time.sleep(1)
    
    log.info("Fetching Fear & Greed index...")
    fear_greed = fetch_fear_greed()
    
    log.info("Fetching Yahoo Finance data...")
    yahoo = fetch_yahoo_quotes(ALL_TICKERS)
    
    # Separate Yahoo data into categories
    from config import INDICES, FOREX, COMMODITIES, BONDS, VOLATILITY
    
    def extract(mapping):
        return {label: yahoo.get(label, {"price": 0, "change_pct": 0}) for label in mapping.values()}
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "crypto": crypto,
        "crypto_movers": movers,
        "fear_greed": fear_greed,
        "indices": extract(INDICES),
        "forex": extract(FOREX),
        "commodities": extract(COMMODITIES),
        "bonds": extract(BONDS),
        "volatility": extract(VOLATILITY),
    }


if __name__ == "__main__":
    import json
    data = collect_all_data()
    print(json.dumps(data, indent=2, default=str))
