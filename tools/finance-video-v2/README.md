# Finance Video V2 — Savvy Finance Style

Dark neon aesthetic video renderer for the Daily Finance Pulse newsletter.
Generates YouTube-ready market recap videos with kinetic typography, glassmorphism data cards, and AI narration.

## Visual Features
- **Glassmorphism cards** — frosted glass with glow accents and crypto logos
- **Animated particle system** — 80 particles with varied colors and pulsing
- **Fear & Greed gauge** — semicircular colored meter with needle
- **Scrolling ticker strip** — continuous bottom ticker with all assets
- **Kinetic typography** — slam, slide, fade, typewriter effects
- **Neon border frame** — glowing corner brackets, grid background
- **Highlighted numbers** — regex-based coloring (green/red/accent)
- **Scene transitions** — dark pulse between sections

## Pipeline
```
market data (JSON) → render_video.py → frames (JPEG) → ffmpeg → MP4
                    ↑
         generate_script.py → generate_voice.py → audio sync
```

## Usage
```bash
# Basic render (no audio)
python3 render_video.py --data market_data.json --profile landscape --output video.mp4

# Full pipeline with narration
python3 pipeline.py --data market_data.json
```

## Profiles
- `landscape` — 1920×1080 (YouTube)
- `shorts` — 1080×1920 (YouTube Shorts, TikTok, Reels)

## Assets
- `assets/logos/` — Crypto logos (BTC, ETH, SOL, XRP, ADA, DOGE) — 2000×2000 RGBA PNGs
- Add more logos as `SYMBOL.png` — auto-loaded by renderer

## Quality Assessment
- Data frames: **8/10** — clean layout, logos, color coding
- Analysis frames: **8.5/10** — F&G gauge, highlighted numbers, two-column layout
- Title card: **7/10** — cinematic with stats row
- **Overall: ~7.5-8/10**

## Next Improvements
- Sparkline mini-charts for price trends
- Stock footage B-roll layer
- Smoother gauge anti-aliasing (use larger canvas + downscale)
- Animated number counters
- More logos (stock indices, commodities)

## Dependencies
- Python 3.9+
- Pillow (PIL)
- ffmpeg
