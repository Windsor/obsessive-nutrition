# Finance Newsletter Configuration

GHOST_URL = "http://192.168.68.139:2370"
GHOST_ADMIN_KEY = "6998e826bb07b687f6c5a2b1:224fbf8e1b29fe60ba40410532d0f8e968c32e82b97a558db6adad1c58a72906"
GHOST_CONTENT_KEY = "495686c7f28fa54a5dea9d13eb"

# FRED API (free key from fred.stlouisfed.org)
FRED_API_KEY = ""  # Will use web scraping fallback if empty

# Data Sources
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# ── Crypto ──
CRYPTO = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "cardano": "ADA",
    "chainlink": "LINK",
    "avalanche-2": "AVAX",
    "polkadot": "DOT",
}

# ── Stock Indices ──
INDICES = {
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    "^DJI": "Dow Jones",
    "^RUT": "Russell 2000",
    "^STOXX50E": "Euro Stoxx 50",
    "^FTSE": "FTSE 100",
    "^GDAXI": "DAX",
    "^N225": "Nikkei 225",
    "^HSI": "Hang Seng",
    "PSI20.LS": "PSI-20",
}

# ── Forex ──
FOREX = {
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "USDCHF=X": "USD/CHF",
    "DX-Y.NYB": "DXY",
}

# ── Commodities ──
COMMODITIES = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "CL=F": "Oil (WTI)",
    "BZ=F": "Oil (Brent)",
    "NG=F": "Nat Gas",
    "HG=F": "Copper",
}

# ── Bonds ──
BONDS = {
    "^IRX": "US 3M Yield",
    "^FVX": "US 5Y Yield",
    "^TNX": "US 10Y Yield",
    "^TYX": "US 30Y Yield",
}

# ── Volatility ──
VOLATILITY = {
    "^VIX": "VIX",
    "^MOVE": "MOVE (Bond Vol)",
}

# ── FRED Macro Series ──
FRED_SERIES = {
    "FEDFUNDS": "Fed Funds Rate",
    "T10Y2Y": "10Y-2Y Spread (Yield Curve)",
    "T10YIE": "10Y Breakeven Inflation",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "CPI (All Urban)",
    "GDP": "Real GDP",
    "M2SL": "M2 Money Supply",
    "DTWEXBGS": "Trade-Weighted Dollar",
    "BAMLH0A0HYM2": "HY Credit Spread (OAS)",
    "WALCL": "Fed Balance Sheet",
}

# All Yahoo tickers combined
ALL_TICKERS = {**INDICES, **FOREX, **COMMODITIES, **BONDS, **VOLATILITY}
