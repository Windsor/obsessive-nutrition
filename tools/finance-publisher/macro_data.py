#!/usr/bin/env python3
"""
Macro economic data fetcher — FRED + supplementary sources.
Falls back to web scraping if no FRED API key.
"""
import requests
from log_config import get_logger
log = get_logger("macro_data")
from datetime import datetime, timedelta

HEADERS = {"User-Agent": "Mozilla/5.0 (finance-newsletter/1.0)"}


def fetch_fred_data(api_key, series_dict):
    """Fetch latest values from FRED API."""
    if not api_key:
        return fetch_macro_fallback()
    
    results = {}
    for series_id, label in series_dict.items():
        try:
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 2,
            }
            r = requests.get(url, params=params, headers=HEADERS, timeout=15)
            r.raise_for_status()
            obs = r.json().get("observations", [])
            if obs:
                latest = obs[0]
                prev = obs[1] if len(obs) > 1 else obs[0]
                val = float(latest["value"]) if latest["value"] != "." else None
                prev_val = float(prev["value"]) if prev["value"] != "." else None
                change = None
                if val is not None and prev_val is not None and prev_val != 0:
                    change = ((val - prev_val) / abs(prev_val)) * 100
                results[label] = {
                    "value": val,
                    "prev_value": prev_val,
                    "change_pct": change,
                    "date": latest["date"],
                    "series_id": series_id,
                }
        except Exception as e:
            log.warning(f" FRED {series_id}: {e}")
    return results


def fetch_macro_fallback():
    """Fallback: scrape key macro numbers from public APIs."""
    results = {}
    
    # Treasury yields from Yahoo (already in main pipeline)
    # Fed rate from FRED public page
    try:
        # Use Treasury.gov API for yield curve
        url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"
        params = {"sort": "-record_date", "page[size]": 5}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                results["Avg Interest Rate (Treasury)"] = {
                    "value": float(data[0].get("avg_interest_rate_amt", 0)),
                    "date": data[0].get("record_date"),
                    "change_pct": None,
                }
    except Exception as e:
        log.warning(f" Treasury fallback: {e}")
    
    return results


def fetch_btc_dominance():
    """Fetch BTC dominance from CoinGecko global data."""
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json().get("data", {})
        return {
            "btc_dominance": round(data.get("market_cap_percentage", {}).get("btc", 0), 1),
            "eth_dominance": round(data.get("market_cap_percentage", {}).get("eth", 0), 1),
            "total_market_cap": data.get("total_market_cap", {}).get("usd", 0),
            "total_volume_24h": data.get("total_volume", {}).get("usd", 0),
            "market_cap_change_24h": round(data.get("market_cap_change_percentage_24h_usd", 0), 2),
            "active_cryptos": data.get("active_cryptocurrencies", 0),
        }
    except Exception as e:
        log.warning(f" BTC dominance: {e}")
        return {}


def fetch_defi_data():
    """Fetch DeFi TVL from DefiLlama."""
    try:
        r = requests.get("https://api.llama.fi/v2/historicalChainTvl", headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data and len(data) >= 2:
            latest = data[-1]
            prev = data[-2]
            tvl = latest.get("tvl", 0)
            prev_tvl = prev.get("tvl", 0)
            change = ((tvl - prev_tvl) / prev_tvl * 100) if prev_tvl else 0
            return {
                "total_tvl": tvl,
                "tvl_change_24h": round(change, 2),
            }
    except Exception as e:
        log.warning(f" DeFi TVL: {e}")
    return {}


if __name__ == "__main__":
    import json
    from config import FRED_API_KEY, FRED_SERIES
    
    print("=== FRED Data ===")
    fred = fetch_fred_data(FRED_API_KEY, FRED_SERIES)
    print(json.dumps(fred, indent=2, default=str))
    
    print("\n=== BTC Dominance ===")
    dom = fetch_btc_dominance()
    print(json.dumps(dom, indent=2, default=str))
    
    print("\n=== DeFi TVL ===")
    defi = fetch_defi_data()
    print(json.dumps(defi, indent=2, default=str))
