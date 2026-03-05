# Social Auto-Poster

Receives Ghost webhooks and cross-posts articles to social media platforms.

## Architecture
Flask app running on r2d2 (192.168.68.139:5555) via gunicorn. Ghost sends webhook on `post.published`, app checks for "social" tag, then posts to enabled platforms.

## Files
- `app.py` — Flask webhook handler with stats tracking
- `config.py` — Environment-based configuration
- `posters/bluesky.py` — Bluesky via AT Protocol (with retry)
- `posters/twitter.py` — Twitter/X posting
- `posters/linkedin.py` — LinkedIn posting
- `linkedin_oauth.py` — OAuth helper for LinkedIn setup
- `social-poster.service` — Systemd unit file

## Endpoints
- `POST /webhook/ghost` — Ghost webhook receiver
- `GET /health` — Health check with stats (webhooks received, posts attempted/succeeded/failed, per-platform breakdown)

## Features
- Automatic retry with exponential backoff (2 retries per platform)
- Per-platform error tracking and stats
- Only cross-posts articles tagged "social"

## Deployment
```bash
# On r2d2
cd /home/windsor1337/social-poster
gunicorn -b 127.0.0.1:5555 -w 1 app:app
```

## Currently Active Platforms
- Bluesky ✅
- Twitter (needs API keys)
- LinkedIn (needs API keys)
