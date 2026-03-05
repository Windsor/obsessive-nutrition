# YouTube Automation Pipeline

Automated faceless YouTube channel: **Reddit Stories**

## Pipeline Flow

1. **Fetch** — Pull top Reddit posts from AITA, confessions, etc. (PRAW)
2. **Script** — AI rewrites post into engaging narration (Claude API)
3. **Voice** — TTS generates narration audio (ElevenLabs API)
4. **Video** — Composite background gameplay + audio + subtitles (FFmpeg)
5. **Thumbnail** — Generate eye-catching thumbnail (GoAPI/AI)
6. **Upload** — Push to YouTube via Data API v3
7. **Schedule** — Cron triggers daily

## Setup Required

- [x] Project structure
- [x] Reddit scraper (PRAW)
- [x] Script generator (Claude)
- [x] TTS integration (ElevenLabs)
- [x] Video compositor (FFmpeg)
- [ ] YouTube API OAuth credentials
- [ ] Background gameplay footage
- [ ] Channel branding (name, logo, banner)

## Config

Copy `config/config.example.json` → `config/config.json` and fill in API keys.

## Usage

```bash
# Full pipeline — generates and uploads one video
python3 scripts/pipeline.py

# Individual steps
python3 scripts/fetch_reddit.py      # Fetch stories
python3 scripts/generate_script.py   # AI rewrite
python3 scripts/generate_voice.py    # TTS
python3 scripts/compose_video.py     # FFmpeg composite
python3 scripts/upload_youtube.py    # Upload
```
