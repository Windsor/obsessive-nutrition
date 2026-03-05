#!/usr/bin/env python3
"""
Sector rotation & market breadth analysis for Daily Finance Pulse.
Tracks S&P 500 sector ETFs (SPDR XL series), computes 1d/5d/1m performance,
identifies leading & lagging sectors, and generates a market breadth summary.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_config import get_logger
log = get_logger("sector")

SECTOR_ETFS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLI": "Industrials",
    "XLC": "Communication",
    "XLRE": "Real Estate",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
    "XLB": "Materials",
    "XLY": "Consumer Discret.",
}

RISK_ON_SECTORS  = {"XLK", "XLY", "XLC", "XLI", "XLF"}
RISK_OFF_SECTORS = {"XLU", "XLP", "XLRE", "XLV", "GLD"}


def pct_change(prices, n_days):
    """Compute % change over n_days from the tail of a price series."""
    if len(prices) < n_days + 1:
        return None
    return round((prices[-1] / prices[-(n_days + 1)] - 1) * 100, 2)


def get_sector_analysis() -> dict:
    """
    Fetch 30 days of sector ETF data and compute performance metrics.
    Returns structured data for inclusion in the newsletter.
    """
    try:
        import yfinance as yf
    except ImportError:
        log.error("yfinance not installed")
        return {}

    tickers = list(SECTOR_ETFS.keys())
    try:
        raw = yf.download(tickers, period="35d", interval="1d",
                          auto_adjust=True, progress=False)
        closes = raw["Close"] if "Close" in raw.columns else raw
    except Exception as e:
        log.error(f"yfinance download failed: {e}")
        return {}

    results = {}
    for ticker in tickers:
        try:
            prices = closes[ticker].dropna().tolist()
            if len(prices) < 6:
                continue
            results[ticker] = {
                "name": SECTOR_ETFS[ticker],
                "price": round(prices[-1], 2),
                "1d": pct_change(prices, 1),
                "5d": pct_change(prices, 5),
                "1m": pct_change(prices, 21),
            }
        except Exception as e:
            log.warning(f"Error processing {ticker}: {e}")

    return results


def format_sector_summary(data: dict) -> str:
    """
    Format sector data into a newsletter-ready summary string.
    Includes a top/bottom 3 ranking, risk-on/risk-off signal,
    and a simple market breadth reading.
    """
    if not data:
        return "Sector data unavailable."

    # Sort by 1d performance
    sorted_1d = sorted(data.items(), key=lambda x: x[1].get("1d") or -99, reverse=True)

    lines = ["## 📊 Sector Rotation Snapshot\n"]
    lines.append("| Sector | ETF | 1D | 5D | 1M |")
    lines.append("|--------|-----|----|----|-----|")

    for ticker, d in sorted_1d:
        def fmt(v):
            if v is None:
                return "N/A"
            arrow = "▲" if v > 0 else "▼"
            return f"{arrow} {abs(v):.1f}%"
        lines.append(f"| {d['name']} | {ticker} | {fmt(d['1d'])} | {fmt(d['5d'])} | {fmt(d['1m'])} |")

    # Top 3 and bottom 3
    valid = [(t, d) for t, d in sorted_1d if d.get("1d") is not None]
    if len(valid) >= 3:
        leaders = [f"{d['name']} ({d['1d']:+.1f}%)" for t, d in valid[:3]]
        laggards = [f"{d['name']} ({d['1d']:+.1f}%)" for t, d in valid[-3:]]
        lines.append(f"\n**Leading:** {', '.join(leaders)}")
        lines.append(f"**Lagging:** {', '.join(laggards)}")

    # Risk-on / Risk-off signal
    risk_on_perf  = [d["1d"] for t, d in data.items() if t in RISK_ON_SECTORS  and d.get("1d") is not None]
    risk_off_perf = [d["1d"] for t, d in data.items() if t in RISK_OFF_SECTORS and d.get("1d") is not None]
    if risk_on_perf and risk_off_perf:
        avg_risk_on  = sum(risk_on_perf)  / len(risk_on_perf)
        avg_risk_off = sum(risk_off_perf) / len(risk_off_perf)
        if avg_risk_on > avg_risk_off + 0.3:
            signal = "🟢 Risk-ON — cyclicals & growth leading"
        elif avg_risk_off > avg_risk_on + 0.3:
            signal = "🔴 Risk-OFF — defensives & safe havens leading"
        else:
            signal = "🟡 Mixed — no clear risk-on/risk-off bias"
        lines.append(f"**Market Sentiment:** {signal}")

    # Breadth: % of sectors positive on the day
    pos = sum(1 for t, d in data.items() if (d.get("1d") or 0) > 0)
    total = len(data)
    breadth_pct = round(pos / total * 100)
    lines.append(f"**Sector Breadth:** {pos}/{total} sectors positive ({breadth_pct}%)")

    return "\n".join(lines)


def get_sector_context_for_llm(data: dict) -> str:
    """
    Return a compact text block suitable for injection into an LLM prompt.
    """
    if not data:
        return ""

    sorted_1d = sorted(data.items(), key=lambda x: x[1].get("1d") or -99, reverse=True)
    lines = ["SECTOR PERFORMANCE (today):"]
    for ticker, d in sorted_1d:
        v = d.get("1d")
        s = f"+{v:.1f}%" if v and v > 0 else (f"{v:.1f}%" if v else "N/A")
        lines.append(f"  {d['name']:20s} {ticker}: {s} (5d: {(d.get('5d') or 0):+.1f}%, 1m: {(d.get('1m') or 0):+.1f}%)")

    pos = sum(1 for _, d in data.items() if (d.get("1d") or 0) > 0)
    risk_on  = [d["1d"] for t, d in data.items() if t in RISK_ON_SECTORS  and d.get("1d") is not None]
    risk_off = [d["1d"] for t, d in data.items() if t in RISK_OFF_SECTORS and d.get("1d") is not None]
    avg_ro  = sum(risk_on)  / len(risk_on)  if risk_on  else 0
    avg_rof = sum(risk_off) / len(risk_off) if risk_off else 0

    lines.append(f"Breadth: {pos}/{len(data)} sectors positive")
    lines.append(f"Risk-on avg: {avg_ro:+.2f}%, Risk-off avg: {avg_rof:+.2f}%")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Fetching sector data...")
    data = get_sector_analysis()
    if data:
        print(format_sector_summary(data))
        print("\n--- LLM Context ---")
        print(get_sector_context_for_llm(data))
    else:
        print("No data returned.")
