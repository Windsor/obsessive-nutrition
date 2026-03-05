#!/usr/bin/env python3
"""
Cron Job Monitor — checks if Portugal Brief publish jobs ran successfully.
Designed to be called from heartbeats or manually.

Checks:
1. OpenClaw cron job last run status (via cron list API — must be called from agent)
2. Ghost posts published today (via Content API)
3. Health of all r2d2 services

Usage: This is a reference/documentation script. The actual monitoring
is done by the agent during heartbeats using the cron tool + Ghost API.
"""

import json
import urllib.request
import sys
from datetime import datetime, timezone

GHOST_URL = "https://theportugalbrief.pt"
GHOST_CONTENT_KEY = "572ac18cd3e84202174908842b"

def check_ghost_posts_today():
    """Check how many posts were published today."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    url = f"{GHOST_URL}/ghost/api/content/posts/?key={GHOST_CONTENT_KEY}&filter=published_at:>'{today}'&limit=all"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            posts = data.get("posts", [])
            return {
                "status": "ok",
                "count": len(posts),
                "titles": [p["title"] for p in posts]
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_services():
    """Check r2d2 services are up."""
    services = {
        "ghost": f"{GHOST_URL}",
        "project-tracker": "http://192.168.68.139:3001",
        "quiz-generator": "http://192.168.68.139:5000",
        "social-poster": "http://192.168.68.139:5555/health",
    }
    results = {}
    for name, url in services.items():
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                results[name] = {"status": "ok", "code": resp.status}
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
    return results

if __name__ == "__main__":
    print("=== Ghost Posts Today ===")
    posts = check_ghost_posts_today()
    print(json.dumps(posts, indent=2))

    print("\n=== Service Health ===")
    health = check_services()
    print(json.dumps(health, indent=2))
