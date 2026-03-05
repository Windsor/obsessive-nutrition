#!/usr/bin/env python3
"""
Daily Pulse HTML template generator.
Takes structured data dict and produces Ghost-ready HTML.
"""

from datetime import datetime, timezone


def _arrow(change):
    """Return colored arrow HTML for price change."""
    if change > 0:
        return f'<span style="color:#16a34a">▲ +{change:.2f}%</span>'
    elif change < 0:
        return f'<span style="color:#dc2626">▼ {change:.2f}%</span>'
    return '<span style="color:#6b7280">― 0.00%</span>'


def _format_price(price, is_pct=False):
    """Format price with appropriate precision."""
    if is_pct:
        return f"{price:.2f}%"
    if price >= 10000:
        return f"${price:,.0f}"
    elif price >= 100:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:,.3f}"
    else:
        return f"${price:,.4f}"


def _format_mcap(val):
    """Format market cap in B/T."""
    if val >= 1e12:
        return f"${val/1e12:.2f}T"
    elif val >= 1e9:
        return f"${val/1e9:.1f}B"
    elif val >= 1e6:
        return f"${val/1e6:.0f}M"
    return f"${val:,.0f}"


def _fear_greed_color(value):
    if value <= 25:
        return "#dc2626"  # Extreme Fear
    elif value <= 45:
        return "#f59e0b"  # Fear
    elif value <= 55:
        return "#6b7280"  # Neutral
    elif value <= 75:
        return "#16a34a"  # Greed
    return "#059669"  # Extreme Greed


def _table_row(name, price_str, change_html):
    return f"""<tr>
<td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;font-weight:500">{name}</td>
<td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:right;font-family:monospace">{price_str}</td>
<td style="padding:8px 12px;border-bottom:1px solid #e5e7eb;text-align:right">{change_html}</td>
</tr>"""


def generate_daily_pulse(data: dict) -> dict:
    """Generate the Daily Pulse HTML and metadata.
    
    Returns dict with: title, html, excerpt, tags, meta_description
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    day_name = now.strftime("%A")
    
    # --- Crypto Section ---
    crypto_rows = ""
    for sym in ["BTC", "ETH", "SOL", "XRP", "ADA"]:
        c = data.get("crypto", {}).get(sym)
        if c:
            crypto_rows += _table_row(
                f"{c['name']} ({sym})",
                _format_price(c["price"]),
                _arrow(c["change_24h"])
            )
    
    # --- Crypto Movers ---
    movers = data.get("crypto_movers", {})
    gainers_html = ""
    for g in movers.get("gainers", []):
        gainers_html += f'<li><strong>{g["symbol"]}</strong> ({g["name"]}) — {_format_price(g["price"])} {_arrow(g["change_24h"])}</li>'
    
    losers_html = ""
    for l in movers.get("losers", []):
        losers_html += f'<li><strong>{l["symbol"]}</strong> ({l["name"]}) — {_format_price(l["price"])} {_arrow(l["change_24h"])}</li>'
    
    # --- Fear & Greed ---
    fg = data.get("fear_greed", {"value": 50, "label": "Neutral"})
    fg_color = _fear_greed_color(fg["value"])
    
    # --- Indices ---
    indices_rows = ""
    for name, vals in data.get("indices", {}).items():
        price = vals.get("price", 0)
        change = vals.get("change_pct", 0)
        indices_rows += _table_row(name, f"{price:,.2f}" if price else "—", _arrow(change) if price else "—")
    
    # --- Forex ---
    forex_rows = ""
    for name, vals in data.get("forex", {}).items():
        price = vals.get("price", 0)
        change = vals.get("change_pct", 0)
        price_str = f"{price:.4f}" if "USD" in name else f"{price:.2f}"
        forex_rows += _table_row(name, price_str if price else "—", _arrow(change) if price else "—")
    
    # --- Commodities ---
    commodities_rows = ""
    for name, vals in data.get("commodities", {}).items():
        price = vals.get("price", 0)
        change = vals.get("change_pct", 0)
        commodities_rows += _table_row(name, _format_price(price) if price else "—", _arrow(change) if price else "—")
    
    # --- Bonds & Volatility ---
    bonds_vol_rows = ""
    for section in ["bonds", "volatility"]:
        for name, vals in data.get(section, {}).items():
            price = vals.get("price", 0)
            change = vals.get("change_pct", 0)
            is_pct = "Yield" in name
            price_str = _format_price(price, is_pct=is_pct) if price else "—"
            bonds_vol_rows += _table_row(name, price_str, _arrow(change) if price else "—")
    
    # --- BTC dominance from market cap ---
    btc_mcap = data.get("crypto", {}).get("BTC", {}).get("market_cap", 0)
    total_mcap = sum(c.get("market_cap", 0) for c in data.get("crypto", {}).values())
    
    # --- Build narrative excerpt ---
    btc = data.get("crypto", {}).get("BTC", {})
    btc_dir = "up" if btc.get("change_24h", 0) > 0 else "down"
    excerpt = f"Markets on {day_name}: BTC {btc_dir} {abs(btc.get('change_24h', 0)):.1f}% at {_format_price(btc.get('price', 0))}. Fear & Greed at {fg['value']} ({fg['label']})."
    
    # --- Full HTML ---
    html = f"""
<div style="max-width:680px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1f2937">

<!-- Header -->
<div style="text-align:center;padding:24px 0;border-bottom:3px solid #1f2937">
<h1 style="margin:0;font-size:28px;letter-spacing:-0.5px">📊 Daily Finance Pulse</h1>
<p style="margin:8px 0 0;color:#6b7280;font-size:15px">{day_name}, {date_str}</p>
</div>

<!-- Fear & Greed -->
<div style="text-align:center;padding:20px;margin:20px 0;background:#f9fafb;border-radius:12px">
<p style="margin:0 0 4px;font-size:13px;color:#6b7280;text-transform:uppercase;letter-spacing:1px">Crypto Fear & Greed Index</p>
<p style="margin:0;font-size:48px;font-weight:700;color:{fg_color}">{fg['value']}</p>
<p style="margin:4px 0 0;font-size:16px;font-weight:600;color:{fg_color}">{fg['label']}</p>
</div>

<!-- Crypto -->
<h2 style="font-size:20px;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid #e5e7eb">🪙 Crypto</h2>
<table style="width:100%;border-collapse:collapse;font-size:14px">
<tr style="background:#f9fafb">
<th style="padding:8px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase">Asset</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Price</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">24h</th>
</tr>
{crypto_rows}
</table>

<!-- Top Movers -->
<div style="display:flex;gap:16px;margin:16px 0">
<div style="flex:1;background:#f0fdf4;padding:12px;border-radius:8px">
<p style="margin:0 0 8px;font-weight:600;color:#16a34a;font-size:13px">🚀 Top Gainers (24h)</p>
<ul style="margin:0;padding:0 0 0 16px;font-size:13px;list-style:none">{gainers_html}</ul>
</div>
<div style="flex:1;background:#fef2f2;padding:12px;border-radius:8px">
<p style="margin:0 0 8px;font-weight:600;color:#dc2626;font-size:13px">📉 Top Losers (24h)</p>
<ul style="margin:0;padding:0 0 0 16px;font-size:13px;list-style:none">{losers_html}</ul>
</div>
</div>

<!-- Stock Indices -->
<h2 style="font-size:20px;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid #e5e7eb">📈 Stock Indices</h2>
<table style="width:100%;border-collapse:collapse;font-size:14px">
<tr style="background:#f9fafb">
<th style="padding:8px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase">Index</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Level</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Change</th>
</tr>
{indices_rows}
</table>

<!-- Forex -->
<h2 style="font-size:20px;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid #e5e7eb">💱 Forex</h2>
<table style="width:100%;border-collapse:collapse;font-size:14px">
<tr style="background:#f9fafb">
<th style="padding:8px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase">Pair</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Rate</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Change</th>
</tr>
{forex_rows}
</table>

<!-- Commodities -->
<h2 style="font-size:20px;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid #e5e7eb">🛢️ Commodities</h2>
<table style="width:100%;border-collapse:collapse;font-size:14px">
<tr style="background:#f9fafb">
<th style="padding:8px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase">Commodity</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Price</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Change</th>
</tr>
{commodities_rows}
</table>

<!-- Bonds & Volatility -->
<h2 style="font-size:20px;margin:28px 0 12px;padding-bottom:8px;border-bottom:2px solid #e5e7eb">📊 Bonds & Volatility</h2>
<table style="width:100%;border-collapse:collapse;font-size:14px">
<tr style="background:#f9fafb">
<th style="padding:8px 12px;text-align:left;font-size:12px;color:#6b7280;text-transform:uppercase">Indicator</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Value</th>
<th style="padding:8px 12px;text-align:right;font-size:12px;color:#6b7280;text-transform:uppercase">Change</th>
</tr>
{bonds_vol_rows}
</table>

<!-- Footer -->
<div style="margin-top:32px;padding:16px 0;border-top:2px solid #e5e7eb;text-align:center;color:#9ca3af;font-size:12px">
<p>Data sourced from CoinGecko, Yahoo Finance, and Alternative.me</p>
<p>Daily Finance Pulse — Your morning market briefing</p>
<p style="margin-top:12px"><strong>Also from our team:</strong> <a href="https://theportugalbrief.pt" style="color:#3b82f6;text-decoration:none">The Portugal Brief</a> — Daily English-language news &amp; analysis for expats in Portugal</p>
</div>

</div>
"""
    
    title = f"Daily Pulse — {date_str}"
    meta = f"Markets overview for {date_str}. BTC at {_format_price(btc.get('price', 0))}, Fear & Greed {fg['value']}. Full crypto, equities, forex, commodities breakdown."
    
    return {
        "title": title,
        "html": html,
        "excerpt": excerpt,
        "tags": ["daily-pulse", "markets", "crypto"],
        "meta_description": meta[:300],
    }
