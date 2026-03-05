#!/usr/bin/env python3
"""
IndexNow URL Submission for Ghost CMS
Submits URLs to Bing/Yandex/other search engines for faster indexing.

Usage:
  python3 indexnow.py --url https://theportugalbrief.pt/some-article/
  python3 indexnow.py --all          # Submit all recent posts
  python3 indexnow.py --recent 24    # Submit posts from last 24 hours
"""

import argparse
import json
import os
import sys
import uuid
import requests
from datetime import datetime, timedelta, timezone

# ── Config ──
SITES = {
    "portugal": {
        "host": "theportugalbrief.pt",
        "content_api_key": "572ac18cd3e84202174908842b",
        "api_base": "https://theportugalbrief.pt/ghost/api/content",
    },
    "finance": {
        "host": "192.168.68.139:2370",
        "content_api_key": "495686c7f28fa54a5dea9d13eb",
        "api_base": "http://192.168.68.139:2370/ghost/api/content",
    },
}

INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"

# Generate a persistent key (store in a file)
KEY_FILE = os.path.join(os.path.dirname(__file__), ".indexnow-key")


def get_or_create_key():
    """Get existing IndexNow key or create a new one."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            return f.read().strip()
    key = uuid.uuid4().hex[:32]
    with open(KEY_FILE, "w") as f:
        f.write(key)
    print(f"Generated new IndexNow key: {key}")
    print(f"IMPORTANT: You must create a verification file at:")
    print(f"  https://theportugalbrief.pt/{key}.txt")
    print(f"  containing just: {key}")
    print(f"  (This can be done via Ghost code injection or a static file)")
    return key


def get_recent_posts(site, hours=24, limit=50):
    """Fetch recent Ghost posts."""
    cfg = SITES[site]
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    url = f"{cfg['api_base']}/posts/?key={cfg['content_api_key']}&limit={limit}&order=published_at%20desc&fields=url,published_at,title&filter=published_at:>'{since}'"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json().get("posts", [])
    except Exception as e:
        print(f"Error fetching posts from {site}: {e}")
        return []


def get_all_posts(site, limit=200):
    """Fetch all Ghost posts."""
    cfg = SITES[site]
    url = f"{cfg['api_base']}/posts/?key={cfg['content_api_key']}&limit={limit}&order=published_at%20desc&fields=url,published_at,title"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json().get("posts", [])
    except Exception as e:
        print(f"Error fetching posts from {site}: {e}")
        return []


def submit_urls(host, urls, key):
    """Submit URLs to IndexNow."""
    if not urls:
        print("No URLs to submit.")
        return False

    # Filter to only this host's URLs
    valid_urls = [u for u in urls if host in u]
    if not valid_urls:
        print(f"No URLs matching host {host}")
        return False

    # IndexNow accepts up to 10,000 URLs per batch
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": valid_urls,
    }

    try:
        r = requests.post(
            INDEXNOW_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=30,
        )
        if r.status_code in (200, 202):
            print(f"✅ Submitted {len(valid_urls)} URLs to IndexNow (status {r.status_code})")
            return True
        elif r.status_code == 422:
            print(f"⚠️ IndexNow returned 422 — key verification file may not exist at https://{host}/{key}.txt")
            return False
        else:
            print(f"❌ IndexNow returned {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ IndexNow submission failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="IndexNow URL submission")
    parser.add_argument("--url", help="Single URL to submit")
    parser.add_argument("--all", action="store_true", help="Submit all posts")
    parser.add_argument("--recent", type=int, default=0, help="Submit posts from last N hours")
    parser.add_argument("--site", choices=list(SITES.keys()) + ["all"], default="portugal",
                       help="Which site to submit (default: portugal)")
    parser.add_argument("--dry-run", action="store_true", help="Show URLs without submitting")
    args = parser.parse_args()

    key = get_or_create_key()

    sites = list(SITES.keys()) if args.site == "all" else [args.site]

    for site in sites:
        cfg = SITES[site]
        host = cfg["host"]
        print(f"\n--- {site} ({host}) ---")

        if args.url:
            urls = [args.url]
        elif args.all:
            posts = get_all_posts(site)
            urls = [p["url"] for p in posts if p.get("url")]
            print(f"Found {len(urls)} posts")
        elif args.recent > 0:
            posts = get_recent_posts(site, hours=args.recent)
            urls = [p["url"] for p in posts if p.get("url")]
            print(f"Found {len(urls)} posts from last {args.recent} hours")
        else:
            # Default: last 24 hours
            posts = get_recent_posts(site, hours=24)
            urls = [p["url"] for p in posts if p.get("url")]
            print(f"Found {len(urls)} posts from last 24 hours")

        if args.dry_run:
            for u in urls:
                print(f"  Would submit: {u}")
        else:
            if urls:
                # Only submit for portugal (public domain) — finance is local
                if site == "portugal":
                    submit_urls(host, urls, key)
                else:
                    print(f"  Skipping {site} — not publicly accessible (local IP)")


if __name__ == "__main__":
    main()
