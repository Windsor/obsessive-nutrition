#!/usr/bin/env python3
"""
Finance Newsletter Publisher — fetches market data, generates Daily Pulse + Analysis, publishes to Ghost.

Usage:
    python3 publish.py                  # Full publish (pulse + analysis + deep dive)
    python3 publish.py --pulse-only     # Just the data pulse
    python3 publish.py --analysis-only  # Just the AI analysis
    python3 publish.py --deep-only      # Just the premium deep dive
    python3 publish.py --draft          # Publish as draft
    python3 publish.py --dry-run        # Print without publishing
    python3 publish.py --data-only      # Just fetch and print data (JSON)
"""

import sys
import os
import json
import time
import jwt
import requests
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import GHOST_URL, GHOST_ADMIN_KEY, FRED_API_KEY, FRED_SERIES
from data_pipeline import collect_all_data
from template import generate_daily_pulse
from macro_data import fetch_fred_data, fetch_btc_dominance, fetch_defi_data
from analysis_generator import generate_daily_analysis, generate_deep_dive
import traceback
from log_config import get_logger
log = get_logger("publish")


def retry(func, max_attempts=3, delay=5):
    """Retry a function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                log.error(f"Failed after {max_attempts} attempts: {e}")
                raise
            wait = delay * (2 ** attempt)
            log.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)


def get_ghost_token():
    key_id, secret = GHOST_ADMIN_KEY.split(":")
    iat = int(time.time())
    header = {"alg": "HS256", "typ": "JWT", "kid": key_id}
    payload = {"iat": iat, "exp": iat + 300, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)


def check_existing_post(title):
    token = get_ghost_token()
    headers = {"Authorization": f"Ghost {token}"}
    url = f"{GHOST_URL}/ghost/api/admin/posts/?filter=title:'{title}'&limit=1"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        posts = r.json().get("posts", [])
        if posts:
            return posts[0]
    except Exception:
        pass
    return None


def publish_to_ghost(title, html, excerpt, tags, meta_description, status="published", visibility="public", feature_image=None):
    existing = check_existing_post(title)
    if existing:
        log.warning(f"Post exists: {existing['slug']} — updating")
        return update_ghost_post(existing, html, excerpt, tags, meta_description)
    
    token = get_ghost_token()
    url = f"{GHOST_URL}/ghost/api/admin/posts/?source=html"
    headers = {"Authorization": f"Ghost {token}", "Content-Type": "application/json"}
    tag_objects = [{"name": t} for t in tags]
    
    post_data = {"posts": [{
        "title": title,
        "html": html,
        "excerpt": excerpt,
        "custom_excerpt": excerpt[:300] if excerpt else None,
        "tags": tag_objects,
        "meta_description": meta_description or (excerpt[:300] if excerpt else None),
        "status": status,
        "visibility": visibility,
        "featured": visibility == "public",
        "feature_image": feature_image,
        "meta_title": f"{title} | Daily Finance Pulse"[:65] if title else None,
        "og_title": title,
        "og_description": excerpt[:300] if excerpt else None,
    }]}
    
    r = requests.post(url, json=post_data, headers=headers, timeout=30)
    r.raise_for_status()
    post = r.json()["posts"][0]
    log.info(f"Published: {post['title']}")
    log.info(f"URL: {GHOST_URL}/{post['slug']}/")
    return post


def update_ghost_post(existing, html, excerpt, tags, meta_description):
    token = get_ghost_token()
    post_id = existing["id"]
    url = f"{GHOST_URL}/ghost/api/admin/posts/{post_id}/?source=html"
    headers = {"Authorization": f"Ghost {token}", "Content-Type": "application/json"}
    tag_objects = [{"name": t} for t in tags]
    title = existing.get("title", "")
    post_data = {"posts": [{
        "html": html, "excerpt": excerpt, "custom_excerpt": excerpt[:300] if excerpt else None, "tags": tag_objects,
        "meta_description": meta_description or (excerpt[:300] if excerpt else None),
        "meta_title": f"{title} | Daily Finance Pulse"[:65] if title else None,
        "og_title": title,
        "og_description": excerpt[:300] if excerpt else None,
        "updated_at": existing["updated_at"],
    }]}
    r = requests.put(url, json=post_data, headers=headers, timeout=30)
    r.raise_for_status()
    post = r.json()["posts"][0]
    log.info(f"Updated: {post['title']}")
    return post


def main():
    parser = argparse.ArgumentParser(description="Finance Daily Pulse Publisher")
    parser.add_argument("--pulse-only", action="store_true")
    parser.add_argument("--analysis-only", action="store_true")
    parser.add_argument("--deep-only", action="store_true")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--data-only", action="store_true")
    parser.add_argument("--save-data", type=str)
    parser.add_argument("--topic", type=str, help="Deep dive topic override")
    args = parser.parse_args()
    
    do_all = not (args.pulse_only or args.analysis_only or args.deep_only)
    
    log.info("📊 Finance Daily Pulse Generator v2")
    log.info("=" * 45)
    
    # ── Fetch all data ──
    log.info("\n[1/4] Fetching market data...")
    market_data = collect_all_data()
    
    log.info("[2/4] Fetching macro indicators...")
    macro_data = fetch_fred_data(FRED_API_KEY, FRED_SERIES)
    
    log.info("[3/4] Fetching crypto global data...")
    crypto_global = fetch_btc_dominance()
    time.sleep(1)
    
    log.info("[4/4] Fetching DeFi data...")
    defi_data = fetch_defi_data()
    
    if args.save_data:
        all_data = {"market": market_data, "macro": macro_data, "crypto_global": crypto_global, "defi": defi_data}
        with open(args.save_data, "w") as f:
            json.dump(all_data, f, indent=2, default=str)
        log.info(f"💾 Data saved to {args.save_data}")
    
    if args.data_only:
        all_data = {"market": market_data, "macro": macro_data, "crypto_global": crypto_global, "defi": defi_data}
        print(json.dumps(all_data, indent=2, default=str))
        return
    
    status = "draft" if args.draft else "published"
    results = []
    
    # ── 1. Daily Pulse (data tables) ──
    if do_all or args.pulse_only:
        log.info("\n📈 Generating Daily Pulse...")
        pulse = generate_daily_pulse(market_data)
        if args.dry_run:
            log.info(f"  Title: {pulse['title']}")
            log.info(f"  Excerpt: {pulse['excerpt']}")
        else:
            post = publish_to_ghost(pulse["title"], pulse["html"], pulse["excerpt"],
                                    pulse["tags"], pulse["meta_description"], status,
                                    feature_image="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200")
            results.append(("Pulse", post))
    
    # ── 2. AI Analysis (free) ──
    if do_all or args.analysis_only:
        log.info("\n🧠 Generating AI Market Analysis...")
        analysis = generate_daily_analysis(market_data, macro_data, crypto_global, defi_data)
        if analysis:
            if args.dry_run:
                log.info(f"  Title: {analysis['title']}")
                log.info(f"  Excerpt: {analysis['excerpt']}")
                log.info(f"  Preview: {analysis['html'][:300]}...")
            else:
                post = publish_to_ghost(analysis["title"], analysis["html"], analysis["excerpt"],
                                        analysis["tags"], analysis["meta_description"], status,
                                        feature_image="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200")
                results.append(("Analysis", post))
    
    # ── 3. Deep Dive (paid/premium) ──
    if do_all or args.deep_only:
        log.info("\n🔒 Generating Premium Deep Dive...")
        deep = generate_deep_dive(market_data, macro_data, crypto_global, defi_data, topic=args.topic)
        if deep:
            if args.dry_run:
                log.info(f"  Title: {deep['title']}")
                log.info(f"  Visibility: {deep.get('visibility', 'public')}")
                log.info(f"  Preview: {deep['html'][:300]}...")
            else:
                vis = deep.pop("visibility", "paid")
                post = publish_to_ghost(deep["title"], deep["html"], deep["excerpt"],
                                        deep["tags"], deep["meta_description"], status, visibility=vis)
                results.append(("Deep Dive", post))
        else:
            log.info("  ⏭️ Skipped (no API key or generation failed)")
    
    # ── Summary ──
    if results:
        log.info(f"\n{'=' * 45}")
        log.info(f"✅ Published {len(results)} posts:")
        for label, post in results:
            log.info(f"   {label}: {post.get('slug', 'unknown')}")
    elif args.dry_run:
        log.info("\n[Dry run — nothing published]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.error(f"Publisher crashed: {e}")
        log.error(traceback.format_exc())
        sys.exit(1)
