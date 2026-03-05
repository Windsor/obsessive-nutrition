#!/usr/bin/env python3
"""Samsung Frame Dashboard - Math-based proportional layout"""

import sys
import json
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Users/jarvis/Library/Python/3.9/lib/python/site-packages')

from PIL import Image, ImageDraw, ImageFont
from samsungtvws.art import SamsungTVArt

TV_IP = "192.168.68.151"
SCRIPT_DIR = Path(__file__).parent
BACKGROUNDS_DIR = SCRIPT_DIR / "backgrounds"
OUTPUT_PATH = SCRIPT_DIR / "dashboard.jpg"
STATE_FILE = SCRIPT_DIR / "state.json"

LOCATION = "Braga"

BACKGROUNDS = {
    "starry_night.jpg": "Starry Night",
    "great_wave.jpg": "The Great Wave",
    "girl_pearl_earring.jpg": "Girl with a Pearl Earring",
    "sunflowers.jpg": "Sunflowers",
    "almond_blossoms.jpg": "Almond Blossoms",
    "birth_venus.jpg": "Birth of Venus",
    "wanderer_fog.jpg": "Wanderer Above the Sea of Fog",
    "nighthawks.jpg": "Nighthawks",
}

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"bg_index": 0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_next_background(state):
    bgs = list(BACKGROUNDS.keys())
    idx = state.get("bg_index", 0) % len(bgs)
    state["bg_index"] = (idx + 1) % len(bgs)
    return bgs[idx], BACKGROUNDS[bgs[idx]]

def fetch_json(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except:
        return None

def fetch_weather():
    # Open-Meteo API - Braga center coordinates: 41.5454, -8.4265
    url = "https://api.open-meteo.com/v1/forecast?latitude=41.5454&longitude=-8.4265&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=Europe/Lisbon&forecast_days=3"
    data = fetch_json(url)
    if not data:
        print("Weather fetch failed")
        return None
    try:
        temp = int(data["current"]["temperature_2m"])
        code = data["current"]["weather_code"]
        # Weather code to description
        conditions = {0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
                     45:"Foggy",48:"Depositing rime fog",51:"Light drizzle",53:"Moderate drizzle",
                     55:"Dense drizzle",61:"Slight rain",63:"Moderate rain",65:"Heavy rain",
                     71:"Slight snow",73:"Moderate snow",75:"Heavy snow",80:"Slight showers",
                     81:"Moderate showers",82:"Violent showers",95:"Thunderstorm"}
        cond = conditions.get(code, "Unknown")
        daily = data["daily"]
        # Dynamic day names from actual dates
        from datetime import timedelta
        today = datetime.now()
        days = [(today + timedelta(days=i)).strftime("%a:") for i in range(3)]
        forecast = [{"day": days[i], "hi": int(daily["temperature_2m_max"][i]), 
                    "lo": int(daily["temperature_2m_min"][i])} for i in range(3)]
        return {"temp": temp, "cond": cond, "forecast": forecast}
    except Exception as e:
        print(f"Weather parse error: {e}")
        return None

def fetch_crypto():
    data = fetch_json("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true")
    gold = fetch_json("https://api.coingecko.com/api/v3/simple/price?ids=tether-gold&vs_currencies=usd&include_24hr_change=true")
    if not data: return None
    r = {"BTC": {"p": data["bitcoin"]["usd"], "c": data["bitcoin"].get("usd_24h_change",0)},
         "ETH": {"p": data["ethereum"]["usd"], "c": data["ethereum"].get("usd_24h_change",0)}}
    if gold and "tether-gold" in gold:
        r["GOLD"] = {"p": gold["tether-gold"]["usd"], "c": gold["tether-gold"].get("usd_24h_change",0)}
    return r

def fetch_markets():
    """Fetch market data using yfinance library (Yahoo direct API returns 401)."""
    try:
        import yfinance as yf
        syms = [("^GSPC","S&P 500"),("^DJI","DOW"),("^IXIC","NASDAQ")]
        r = {}
        for sym, name in syms:
            try:
                ticker = yf.Ticker(sym)
                info = ticker.fast_info
                p = info.last_price
                prev = info.previous_close
                r[name] = {"p": p, "c": ((p-prev)/prev*100) if prev else 0}
            except Exception:
                pass
        return r if r else None
    except ImportError:
        # Fallback: try Yahoo v8 (may still work for some)
        syms = [("^GSPC","S&P 500"),("^DJI","DOW"),("^IXIC","NASDAQ")]
        r = {}
        for sym, name in syms:
            data = fetch_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=2d")
            if data and "chart" in data:
                try:
                    m = data["chart"]["result"][0]["meta"]
                    p, prev = m["regularMarketPrice"], m.get("previousClose", m["regularMarketPrice"])
                    r[name] = {"p": p, "c": ((p-prev)/prev*100) if prev else 0}
                except: pass
        return r if r else None

def fetch_news():
    # Primary: Ghost API on r2d2
    try:
        url = "https://theportugalbrief.pt/ghost/api/content/posts/?key=572ac18cd3e84202174908842b&limit=8&fields=title,published_at&order=published_at%20desc"
        data = fetch_json(url, timeout=5)
        if data and "posts" in data:
            titles = [p["title"] for p in data["posts"] if p.get("title")]
            if titles:
                return [t[:115]+"..." if len(t) > 115 else t for t in titles[:8]]
    except:
        pass
    
    # Fallback: local RSS aggregator cache
    try:
        cache_file = Path(__file__).parent.parent / "news-aggregator" / "cache.json"
        if cache_file.exists():
            import json as _json
            with open(cache_file) as f:
                cache = _json.load(f)
            items = cache.get("items", [])
            titles = [item["title"] for item in items[:8] if item.get("title")]
            if titles:
                print("Using RSS cache fallback for news")
                return [t[:115]+"..." if len(t) > 115 else t for t in titles]
    except:
        pass
    
    return None

def create_dashboard(bg_file, bg_name, weather, crypto, markets, news):
    bg_path = BACKGROUNDS_DIR / bg_file
    img = Image.open(bg_path).convert('RGBA') if bg_path.exists() else Image.new('RGBA', (1920,1080), (20,20,40,255))
    if img.size != (1920, 1080):
        img = img.resize((1920, 1080), Image.Resampling.LANCZOS)
    
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    
    # === LAYOUT MATH ===
    MARGIN = 40
    GAP = 20
    WIDTH = 1920 - 2 * MARGIN  # 1840px usable
    
    # Top row: Time 1/3, Weather 2/3
    TOP_Y = 40
    TOP_H = 180
    TIME_W = WIDTH // 3  # ~613px
    WEATHER_W = WIDTH - TIME_W - GAP  # ~1207px
    
    # Middle row: Crypto 1/2, Markets 1/2
    MID_Y = TOP_Y + TOP_H + GAP  # 240
    MID_H = 220
    HALF_W = (WIDTH - GAP) // 2  # ~910px each
    
    # Bottom row: News full width (expanded for 8 headlines)
    BOT_Y = MID_Y + MID_H + GAP  # 480
    BOT_H = 420
    
    W, G, R, BOX = (255,255,255), (76,217,100), (255,69,58), (0,0,0,150)
    
    # Draw boxes
    # Time box
    od.rectangle((MARGIN, TOP_Y, MARGIN + TIME_W, TOP_Y + TOP_H), fill=BOX)
    # Weather box (temp + condition + forecast)
    od.rectangle((MARGIN + TIME_W + GAP, TOP_Y, MARGIN + WIDTH, TOP_Y + TOP_H), fill=BOX)
    # Crypto box
    od.rectangle((MARGIN, MID_Y, MARGIN + HALF_W, MID_Y + MID_H), fill=BOX)
    # Markets box
    od.rectangle((MARGIN + HALF_W + GAP, MID_Y, MARGIN + WIDTH, MID_Y + MID_H), fill=BOX)
    # News box
    od.rectangle((MARGIN, BOT_Y, MARGIN + WIDTH, BOT_Y + BOT_H), fill=BOX)
    # Footer
    od.rectangle((MARGIN, 1010, MARGIN + 280, 1055), fill=BOX)
    od.rectangle((1600, 1010, 1880, 1055), fill=BOX)
    
    img = Image.alpha_composite(img, overlay)
    d = ImageDraw.Draw(img)
    
    # Fonts scaled to fit
    try:
        f_time = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        f_temp = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
        f_head = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        f_data = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        f_forecast = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        f_news = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)
        f_sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except:
        f_time = f_temp = f_head = f_data = f_forecast = f_news = f_sm = ImageFont.load_default()
    
    def t(xy, txt, font, col=W):
        d.text((xy[0]+2, xy[1]+2), txt, font=font, fill=(0,0,0))
        d.text(xy, txt, font=font, fill=col)
    
    now = datetime.now()
    PAD = 20  # padding inside boxes
    
    # ===== TIME BOX (1/3 width) =====
    time_x = MARGIN + PAD
    t((time_x, TOP_Y + 15), now.strftime("%H:%M"), f_time)
    t((time_x, TOP_Y + 130), now.strftime("%A, %B %d"), f_sm)
    t((time_x, TOP_Y + 158), LOCATION, f_sm)
    
    # ===== WEATHER BOX (2/3 width) - includes temp + condition + forecast =====
    weather_x = MARGIN + TIME_W + GAP + PAD
    if weather:
        # Left side: temp + condition
        t((weather_x, TOP_Y + 20), f"{weather['temp']}°C", f_temp)
        t((weather_x, TOP_Y + 130), weather['cond'][:20], f_sm)
        # Right side: forecast
        forecast_x = weather_x + 350
        for i, fc in enumerate(weather['forecast'][:3]):
            t((forecast_x, TOP_Y + 30 + i*50), f"{fc['day']} {fc['hi']}°/{fc['lo']}°", f_forecast)
    else:
        # Fallback when weather unavailable
        t((weather_x, TOP_Y + 60), "Weather", f_temp)
        t((weather_x, TOP_Y + 130), "Unavailable", f_sm)
    
    # ===== CRYPTO BOX (1/2 width) =====
    crypto_x = MARGIN + PAD
    t((crypto_x, MID_Y + 15), "CRYPTO", f_head)
    if crypto:
        y = MID_Y + 65
        for sym, v in crypto.items():
            col = G if v['c'] >= 0 else R
            price = f"${v['p']:,.0f}" if v['p'] >= 100 else f"${v['p']:.2f}"
            chg = f"+{v['c']:.1f}%" if v['c'] >= 0 else f"{v['c']:.1f}%"
            t((crypto_x, y), sym, f_data)
            t((crypto_x + 120, y), price, f_data)
            t((crypto_x + 320, y), chg, f_data, col)
            y += 52
    
    # ===== MARKETS BOX (1/2 width) =====
    markets_x = MARGIN + HALF_W + GAP + PAD
    t((markets_x, MID_Y + 15), "MARKETS", f_head)
    if markets:
        y = MID_Y + 65
        for name, v in markets.items():
            col = G if v['c'] >= 0 else R
            chg = f"+{v['c']:.1f}%" if v['c'] >= 0 else f"{v['c']:.1f}%"
            t((markets_x, y), name, f_data)
            t((markets_x + 180, y), f"{v['p']:,.0f}", f_data)
            t((markets_x + 340, y), chg, f_data, col)
            y += 52
    
    # ===== NEWS BOX (full width) =====
    news_x = MARGIN + PAD
    t((news_x, BOT_Y + 15), "THE PORTUGAL BRIEF", f_head)
    if news:
        for i, h in enumerate(news[:8]):
            t((news_x, BOT_Y + 60 + i*40), h, f_news)
    
    # ===== FOOTER =====
    t((MARGIN + 10, 1018), f"Art: {bg_name}", f_sm)
    t((1610, 1018), f"Updated {now.strftime('%H:%M')}", f_sm)
    
    img.convert('RGB').save(OUTPUT_PATH, "JPEG", quality=92)
    print(f"Dashboard saved: {OUTPUT_PATH}")
    return OUTPUT_PATH

def upload_to_tv(path):
    try:
        art = SamsungTVArt(TV_IP)
        with open(path, 'rb') as f:
            data = f.read()
        cid = art.upload(data, file_type='JPEG', matte='none')
        print(f"Uploaded: {cid}")
        art.select_image(cid)
        print("Displaying dashboard")
    except Exception as e:
        print(f"Upload failed (TV may be off): {e}")
        # Don't crash - just log and continue

def main():
    print(f"{datetime.now()}: Dashboard updated")
    
    # Only upload between 7am and 10pm
    now = datetime.now()
    hour = now.hour
    should_upload = 7 <= hour < 22
    
    state = load_state()
    bg, name = get_next_background(state)
    print(f"Background: {bg}")
    save_state(state)
    
    path = create_dashboard(bg, name, fetch_weather(), fetch_crypto(), fetch_markets(), fetch_news())
    
    if should_upload:
        upload_to_tv(path)
    else:
        print(f"Skipping upload (outside 7am-10pm window, current hour: {hour})")

if __name__ == "__main__":
    main()
