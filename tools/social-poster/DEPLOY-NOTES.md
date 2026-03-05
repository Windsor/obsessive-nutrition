# Social Poster — Deploy Notes

## New: Reddit Module (2026-03-01)
- `posters/reddit.py` — cross-posts to r/portugal and r/PortugalExpats
- Tag-based subreddit targeting (politics→portugal, expat-life→PortugalExpats, etc.)
- Rate limiting per subreddit (24h for r/portugal, 12h for PortugalExpats)
- Link posts by default (no resubmit of same URL)
- `config.py` updated with Reddit + Mastodon env vars

### To deploy on r2d2:
1. Copy `posters/reddit.py` to `~/social-poster/posters/`
2. Merge config.py changes (Reddit/Mastodon env vars)
3. Add to app.py webhook handler (after Bluesky block):
```python
from posters.reddit import post_to_reddit

# In ghost_webhook():
if config.REDDIT_CLIENT_ID:
    try:
        tags = [t.get("name", "") for t in post.get("tags", [])]
        reddit_results = post_to_reddit(data["title"], data["url"], tags=tags)
        results["reddit"] = reddit_results
        log.info(f"Reddit: {reddit_results}")
    except Exception as e:
        results["reddit"] = f"error: {e}"
        log.error(f"❌ Reddit failed: {e}")
```
4. `pip install praw` on r2d2
5. Add Reddit app credentials to `.env`
6. Restart social-poster: `sudo systemctl restart social-poster`

### Reddit App Setup (Glenn needs to do):
1. Go to https://www.reddit.com/prefs/apps/
2. Create "script" type app
3. Note client_id (under app name) and client_secret
4. Set env vars: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
