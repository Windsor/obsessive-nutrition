#!/usr/bin/env python3
"""
Ghost Newsletter Analytics — Track members, posts, and engagement.
Usage: python3 analytics.py [--json]
"""

import json
import sys
import time
import jwt
import requests
from datetime import datetime

GHOST_URL = "https://theportugalbrief.pt"
ADMIN_KEY = "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"
CONTENT_KEY = "572ac18cd3e84202174908842b"

def get_admin_token():
    key_id, secret = ADMIN_KEY.split(":")
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/admin/"},
        bytes.fromhex(secret), algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "kid": key_id}
    )

def admin_get(endpoint, params=None):
    token = get_admin_token()
    r = requests.get(f"{GHOST_URL}/ghost/api/admin/{endpoint}",
                     headers={"Authorization": f"Ghost {token}"},
                     params=params or {}, timeout=15)
    r.raise_for_status()
    return r.json()

def content_get(endpoint, params=None):
    p = params or {}
    p["key"] = CONTENT_KEY
    r = requests.get(f"{GHOST_URL}/ghost/api/content/{endpoint}", params=p, timeout=15)
    r.raise_for_status()
    return r.json()

def get_analytics():
    # Members
    members_data = admin_get("members/", {"limit": "all"})
    members = members_data.get("members", [])
    total_members = len(members)
    free_members = sum(1 for m in members if m["status"] == "free")
    paid_members = sum(1 for m in members if m["status"] == "paid")
    subscribed = sum(1 for m in members if m.get("subscribed"))

    # Posts
    posts_data = content_get("posts/", {"limit": "all", "fields": "id,title,slug,published_at,reading_time"})
    posts = posts_data.get("posts", [])
    total_posts = len(posts)
    published_posts = [p for p in posts if p.get("published_at")]

    # Posts by day
    posts_by_day = {}
    for p in published_posts:
        day = p["published_at"][:10]
        posts_by_day[day] = posts_by_day.get(day, 0) + 1

    # Newsletters
    newsletters = admin_get("newsletters/", {"limit": "all"}).get("newsletters", [])

    # Tags
    tags_data = content_get("tags/", {"limit": "all", "include": "count.posts"})
    tags = tags_data.get("tags", [])
    top_tags = sorted(tags, key=lambda t: t.get("count", {}).get("posts", 0), reverse=True)[:10]

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "members": {
            "total": total_members,
            "free": free_members,
            "paid": paid_members,
            "subscribed_to_newsletter": subscribed,
            "recent": [{"email": m["email"], "name": m.get("name", ""), "joined": m["created_at"],
                        "last_seen": m.get("last_seen_at"), "status": m["status"]}
                       for m in sorted(members, key=lambda m: m["created_at"], reverse=True)[:10]]
        },
        "posts": {
            "total": total_posts,
            "published": len(published_posts),
            "by_day": dict(sorted(posts_by_day.items(), reverse=True)),
            "avg_reading_time": round(sum(p.get("reading_time", 0) for p in published_posts) / max(len(published_posts), 1), 1)
        },
        "newsletters": [{"name": n["name"], "status": n["status"], "slug": n["slug"]} for n in newsletters],
        "top_tags": [{"name": t["name"], "posts": t.get("count", {}).get("posts", 0)} for t in top_tags],
        "notes": {
            "email_sending": "Not configured — posts published as web content only",
            "email_analytics": "Will be available once SMTP/Mailgun is configured for Ghost",
            "seo": "Google Search Console pending domain verification"
        }
    }

if __name__ == "__main__":
    analytics = get_analytics()
    if "--json" in sys.argv:
        print(json.dumps(analytics, indent=2))
    else:
        a = analytics
        print("═" * 50)
        print("  📰 The Portugal Brief — Analytics")
        print("═" * 50)
        print(f"\n👥 Members: {a['members']['total']} total ({a['members']['free']} free, {a['members']['paid']} paid)")
        print(f"   Newsletter subscribers: {a['members']['subscribed_to_newsletter']}")
        print(f"\n📝 Posts: {a['posts']['published']} published")
        print(f"   Avg reading time: {a['posts']['avg_reading_time']} min")
        if a['posts']['by_day']:
            print(f"   Recent days: {', '.join(f'{d}: {c}' for d, c in list(a['posts']['by_day'].items())[:5])}")
        if a['top_tags']:
            print(f"\n🏷️  Top tags: {', '.join(f'{t['name']} ({t['posts']})' for t in a['top_tags'][:5])}")
        print(f"\n📧 Email: {a['notes']['email_sending']}")
        print(f"🔍 SEO: {a['notes']['seo']}")
        print()
