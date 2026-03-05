# Ghost Publisher

Publishes articles to The Portugal Brief Ghost CMS.

## Files
- `publish.py` — Main publishing script. Creates/updates posts via Ghost Admin API.
- `briefing-header.png` — Default header image for briefings
- `general-header.png` — Default header image for general articles

## Usage
Used by OpenClaw cron jobs (morning & afternoon editions) to publish articles.

## Config
- Ghost Admin API key in `TOOLS.md`
- Ghost URL: `https://theportugalbrief.pt`
