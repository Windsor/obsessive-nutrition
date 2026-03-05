#!/usr/bin/env python3
"""Print today's published article titles for The Portugal Brief.
Useful for checking what's already been published before creating new content.

Usage: python3 todays_titles.py
"""
import jwt, time, requests, json
from datetime import datetime, timezone

GHOST_URL = "https://theportugalbrief.pt"
ADMIN_KEY = "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"


def get_token():
    kid, secret = ADMIN_KEY.split(":")
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/admin/"},
        bytes.fromhex(secret), algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "kid": kid})


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    token = get_token()
    r = requests.get(
        f"{GHOST_URL}/ghost/api/admin/posts/?limit=30&order=published_at%20desc&fields=title,published_at,slug",
        headers={"Authorization": f"Ghost {token}"}, timeout=15)
    r.raise_for_status()
    
    today_posts = [p for p in r.json()["posts"] if p.get("published_at", "").startswith(today)]
    
    if not today_posts:
        print("No posts published today yet.")
        return
    
    print(f"Published today ({today}):")
    for p in today_posts:
        t = p["published_at"][11:16]
        print(f"  [{t}] {p['title']}")


if __name__ == "__main__":
    main()
