#!/usr/bin/env python3
"""
AI-powered market analysis article generator.
Uses Claude to create expert-level daily market analysis.
"""
import os
import json
import requests
from datetime import datetime, timezone

from log_config import get_logger
log = get_logger("analysis")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def generate_daily_analysis(market_data: dict, macro_data: dict = None, 
                            crypto_global: dict = None, defi: dict = None) -> dict:
    """Generate an expert market analysis article using Claude."""
    
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    day_name = now.strftime("%A")
    
    # Build data summary for Claude
    data_summary = _build_data_summary(market_data, macro_data, crypto_global, defi)
    
    # Weekend context
    weekend_note = ""
    if day_name in ("Saturday", "Sunday"):
        weekend_note = ("\n\nNOTE: Today is a weekend. Traditional markets (stocks, forex, commodities) "
            "are closed - the data shown reflects Friday's close. Crypto markets trade 24/7 "
            "and the data is live. Frame your analysis accordingly - focus on the week's recap, "
            "crypto weekend moves, and the outlook for Monday's open.")
    prompt = f"""You are a senior financial analyst writing a daily market analysis for a finance newsletter called "Daily Finance Pulse". Today is {day_name}, {date_str}.{weekend_note}

Here is today's market data:

{data_summary}

Write a comprehensive daily market analysis article with the following structure:

1. **Market Overview** (2-3 paragraphs) — What happened today across markets. Lead with the most significant moves. Connect the dots between asset classes.

2. **Key Drivers** (3-5 bullet points with brief analysis) — What's driving today's moves? Fed/central bank signals, economic data, geopolitical events, earnings, technical levels.

3. **Crypto Spotlight** (1-2 paragraphs) — Deep dive on crypto market. BTC dominance trends, altcoin rotation, DeFi TVL, institutional flows, on-chain signals.

4. **Expert Consensus** (1-2 paragraphs) — Synthesize what major market strategists and analysts are likely thinking based on current conditions. Reference typical institutional positioning for these market conditions.

5. **What to Watch** (3-5 bullet points) — Key events, levels, and catalysts for the next 24-48 hours.

6. **Risk Dashboard** — Brief assessment: overall risk appetite (risk-on/risk-off/mixed), yield curve signal, credit conditions, volatility regime.

Style guidelines:
- Professional but accessible. Think Bloomberg meets Morning Brew.
- Use specific numbers and data points from the data provided.
- No disclaimers or "this is not financial advice" — this is editorial content.
- Bold key figures and important terms.
- Around 800-1200 words total.
- Use HTML formatting (h2, h3, p, strong, ul/li, em).

Return ONLY the HTML content (no wrapper div, no title — just the article body starting with the first <h2>)."""

    if not ANTHROPIC_API_KEY:
        return _fallback_analysis(market_data, date_str, day_name)
    
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(ANTHROPIC_URL, json=body, headers=headers, timeout=60)
        r.raise_for_status()
        html = r.json()["content"][0]["text"]
        
        # Generate excerpt
        btc = market_data.get("crypto", {}).get("BTC", {})
        fg = market_data.get("fear_greed", {})
        excerpt = f"Daily market analysis for {date_str}. BTC at ${btc.get('price', 0):,.0f}, Fear & Greed {fg.get('value', 'N/A')}. Expert breakdown of crypto, equities, macro, and what to watch next."
        
        return {
            "title": f"Market Analysis — {date_str}",
            "html": html,
            "excerpt": excerpt,
            "tags": ["analysis", "markets", "daily-analysis"],
            "meta_description": excerpt[:300],
        }
    except Exception as e:
        log.warning(f" Claude analysis failed: {e}")
        return _fallback_analysis(market_data, date_str, day_name)


def generate_deep_dive(market_data: dict, macro_data: dict = None,
                       crypto_global: dict = None, defi: dict = None,
                       topic: str = None) -> dict:
    """Generate a premium deep-dive analysis for the paid tier."""
    
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    day_name = now.strftime("%A")
    
    data_summary = _build_data_summary(market_data, macro_data, crypto_global, defi)
    
    topic_instruction = ""
    if topic:
        topic_instruction = f"Focus this deep dive on: {topic}"
    else:
        topic_instruction = "Choose the most significant market theme from today's data for the deep dive."
    
    # Weekend context for deep dive
    weekend_note_dd = ""
    if day_name in ("Saturday", "Sunday"):
        weekend_note_dd = ("\n\nNOTE: Today is a weekend. Traditional markets are closed - "
            "equity/forex/commodity data reflects Friday's close. Crypto is live 24/7. "
            "Frame analysis as a weekly review + forward outlook for the coming week.")
    prompt = f"""You are the lead strategist at a macro hedge fund writing the premium daily deep-dive for institutional subscribers of "Daily Finance Pulse PRO". Today is {day_name}, {date_str}.{weekend_note_dd}

{topic_instruction}

Here is today's market data:
{data_summary}

Write a premium deep-dive analysis (1500-2500 words) with:

1. **Thesis** — Clear, bold statement about the current market regime and what's changing.

2. **Deep Analysis** (4-6 paragraphs) — Institutional-grade breakdown. Cross-asset correlations, macro regime analysis, positioning signals, flow analysis. Reference historical analogs where relevant.

3. **Crypto On-Chain & Structural** (2-3 paragraphs) — Deep crypto analysis: exchange reserves, whale movements, funding rates, open interest patterns, network fundamentals, regulatory landscape.

4. **Cross-Asset Playbook** — How different asset classes are interacting. Dollar-gold-yields triangle. Equity-crypto correlation regime. Credit signals.

5. **Scenario Analysis** — Bull case (30%), base case (50%), bear case (20%) with specific levels and triggers for each.

6. **Institutional Positioning Summary** — What smart money is likely doing. COT positioning hints, dark pool signals, options skew analysis.

7. **Tactical Watchlist** — 5-8 specific levels, events, or triggers with clear significance.

Style:
- Think Bridgewater Daily Observations meets Delphi Digital.
- Dense with insight, no filler. Every sentence should inform.
- Use specific numbers. Reference historical analogs.
- Professional HTML formatting (h2, h3, p, strong, ul/li, em, blockquote for key insights).
- This is PREMIUM content — it should feel substantially more valuable than the free version.

Return ONLY the HTML content body."""

    if not ANTHROPIC_API_KEY:
        return None
    
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 6000,
            "messages": [{"role": "user", "content": prompt}],
        }
        r = requests.post(ANTHROPIC_URL, json=body, headers=headers, timeout=90)
        r.raise_for_status()
        html = r.json()["content"][0]["text"]
        
        btc = market_data.get("crypto", {}).get("BTC", {})
        excerpt = f"Premium deep-dive analysis for {date_str}. Institutional-grade market intelligence covering macro regime, crypto on-chain signals, cross-asset positioning, and tactical scenarios."
        
        return {
            "title": f"🔒 Deep Dive — {date_str}",
            "html": html,
            "excerpt": excerpt,
            "tags": ["deep-dive", "premium", "analysis"],
            "meta_description": excerpt[:300],
            "visibility": "paid",  # Ghost paid-members only
        }
    except Exception as e:
        log.warning(f" Claude deep dive failed: {e}")
        return None


def _build_data_summary(market_data, macro_data, crypto_global, defi):
    """Build a text summary of all market data for the AI prompt."""
    parts = []
    
    # Crypto
    crypto = market_data.get("crypto", {})
    if crypto:
        parts.append("CRYPTO:")
        for sym, d in crypto.items():
            parts.append(f"  {sym}: ${d['price']:,.2f} ({d['change_24h']:+.1f}% 24h, {d.get('change_7d', 0):+.1f}% 7d) mcap: ${d.get('market_cap', 0)/1e9:.1f}B")
    
    # Fear & Greed
    fg = market_data.get("fear_greed", {})
    if fg:
        parts.append(f"\nFEAR & GREED INDEX: {fg.get('value')} ({fg.get('label')})")
    
    # Top movers
    movers = market_data.get("crypto_movers", {})
    if movers.get("gainers"):
        parts.append("\nTOP CRYPTO GAINERS (24h):")
        for g in movers["gainers"]:
            parts.append(f"  {g['symbol']}: ${g['price']:,.2f} ({g['change_24h']:+.1f}%)")
    if movers.get("losers"):
        parts.append("TOP CRYPTO LOSERS (24h):")
        for l in movers["losers"]:
            parts.append(f"  {l['symbol']}: ${l['price']:,.2f} ({l['change_24h']:+.1f}%)")
    
    # Indices, Forex, Commodities, Bonds, Vol
    for section in ["indices", "forex", "commodities", "bonds", "volatility"]:
        data = market_data.get(section, {})
        if data:
            parts.append(f"\n{section.upper()}:")
            for name, d in data.items():
                price = d.get("price", 0)
                change = d.get("change_pct", 0)
                parts.append(f"  {name}: {price:,.2f} ({change:+.2f}%)")
    
    # Macro
    if macro_data:
        parts.append("\nMACRO INDICATORS (FRED):")
        for label, d in macro_data.items():
            val = d.get("value")
            date = d.get("date", "")
            change = d.get("change_pct")
            change_str = f" ({change:+.2f}%)" if change is not None else ""
            parts.append(f"  {label}: {val}{change_str} (as of {date})")
    
    # Crypto global
    if crypto_global:
        parts.append(f"\nCRYPTO GLOBAL:")
        parts.append(f"  BTC Dominance: {crypto_global.get('btc_dominance', 'N/A')}%")
        parts.append(f"  ETH Dominance: {crypto_global.get('eth_dominance', 'N/A')}%")
        total_mc = crypto_global.get('total_market_cap', 0)
        parts.append(f"  Total Market Cap: ${total_mc/1e12:.2f}T")
        parts.append(f"  24h Volume: ${crypto_global.get('total_volume_24h', 0)/1e9:.1f}B")
        parts.append(f"  Market Cap Change 24h: {crypto_global.get('market_cap_change_24h', 0):+.2f}%")
    
    # DeFi
    if defi:
        parts.append(f"\nDEFI:")
        tvl = defi.get('total_tvl', 0)
        parts.append(f"  Total TVL: ${tvl/1e9:.1f}B")
        parts.append(f"  TVL Change 24h: {defi.get('tvl_change_24h', 0):+.2f}%")
    
    return "\n".join(parts)


def _fallback_analysis(market_data, date_str, day_name):
    """Generate a basic analysis without AI when API key is missing."""
    btc = market_data.get("crypto", {}).get("BTC", {})
    fg = market_data.get("fear_greed", {})
    
    html = f"""<h2>Market Overview</h2>
<p>Markets on {day_name}, {date_str}. Bitcoin trades at <strong>${btc.get('price', 0):,.0f}</strong> 
({btc.get('change_24h', 0):+.1f}% in 24h). The Fear & Greed Index reads 
<strong>{fg.get('value', 'N/A')}</strong> ({fg.get('label', 'N/A')}).</p>
<p><em>Full AI analysis requires ANTHROPIC_API_KEY environment variable.</em></p>"""
    
    return {
        "title": f"Market Analysis — {date_str}",
        "html": html,
        "excerpt": f"Markets overview for {date_str}.",
        "tags": ["analysis", "markets"],
        "meta_description": f"Daily market analysis for {date_str}.",
    }


if __name__ == "__main__":
    from data_pipeline import collect_all_data
    from macro_data import fetch_fred_data, fetch_btc_dominance, fetch_defi_data
    from config import FRED_API_KEY, FRED_SERIES
    
    market = collect_all_data()
    macro = fetch_fred_data(FRED_API_KEY, FRED_SERIES)
    crypto_global = fetch_btc_dominance()
    defi = fetch_defi_data()
    
    result = generate_daily_analysis(market, macro, crypto_global, defi)
    print(f"Title: {result['title']}")
    print(f"Tags: {result['tags']}")
    print(result["html"][:500])
