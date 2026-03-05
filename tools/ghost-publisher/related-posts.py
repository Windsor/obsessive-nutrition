#!/usr/bin/env python3
"""Add related posts section to PT Brief articles that lack internal links.

Finds articles without a "Related Stories" section and adds one based on
shared tags. This improves SEO through internal linking and keeps readers
on the site longer.

Usage:
    python related-posts.py --dry-run       # Preview changes
    python related-posts.py --apply         # Apply to all posts missing related section
    python related-posts.py --apply --limit 10  # Apply to latest 10 posts only
"""

import jwt, time, requests, json, sys, argparse, re
from collections import Counter

GHOST_URL = "https://theportugalbrief.pt"
ADMIN_KEY = "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"

# Skip adding related posts to briefings (they're compilations already)
SKIP_TAGS = {"Daily Briefing", "Afternoon Update", "Markets Briefing"}


def get_token():
    kid, secret = ADMIN_KEY.split(":")
    iat = int(time.time())
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    payload = {"iat": iat, "exp": iat + 300, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)


def fetch_all_posts(token):
    """Fetch all published posts with tags and HTML."""
    posts = []
    page = 1
    while True:
        r = requests.get(
            f"{GHOST_URL}/ghost/api/admin/posts/?limit=50&page={page}&filter=status:published"
            f"&formats=html&include=tags&order=published_at%20desc",
            headers={"Authorization": f"Ghost {token}"}, timeout=30)
        if r.status_code != 200:
            break
        data = r.json()
        posts.extend(data["posts"])
        if page >= data["meta"]["pagination"]["pages"]:
            break
        page += 1
    return posts


def find_related(post, all_posts, max_related=3):
    """Find related posts by tag overlap. Returns list of (title, url, score)."""
    post_tags = {t["name"] for t in post.get("tags", [])} - SKIP_TAGS
    if not post_tags:
        return []

    scored = []
    for other in all_posts:
        if other["id"] == post["id"]:
            continue
        other_tags = {t["name"] for t in other.get("tags", [])}
        # Skip briefings as related articles
        if other_tags & SKIP_TAGS:
            continue
        overlap = post_tags & other_tags
        if overlap:
            scored.append((len(overlap), other["title"], other["url"]))

    # Sort by tag overlap (desc), take top N
    scored.sort(key=lambda x: -x[0])
    return [(title, url) for _, title, url in scored[:max_related]]


def has_related_section(html):
    """Check if post already has a related stories section."""
    if not html:
        return False
    lower = html.lower()
    return any(marker in lower for marker in [
        "related stories", "related articles", "you might also like",
        "also read", "more on this topic", "further reading"
    ])


def build_related_html(related_posts):
    """Build the related posts HTML section."""
    if not related_posts:
        return ""
    links = "\n".join(
        f'<li><a href="{url}">{title}</a></li>'
        for title, url in related_posts
    )
    return f"""
<hr>
<h3 id="related-stories">Related Stories</h3>
<ul>
{links}
</ul>"""


def update_post_html(post_id, html, updated_at, token):
    """Update a post's HTML via the Admin API."""
    r = requests.put(
        f"{GHOST_URL}/ghost/api/admin/posts/{post_id}/?source=html",
        json={"posts": [{"html": html, "updated_at": updated_at}]},
        headers={"Authorization": f"Ghost {token}"}, timeout=30)
    return r.status_code == 200


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--limit", type=int, default=0, help="Limit posts to process (0=all)")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply")
        sys.exit(1)

    token = get_token()
    print("Fetching all posts...")
    all_posts = fetch_all_posts(token)
    print(f"Found {len(all_posts)} published posts")

    # Filter to non-briefing posts that lack a related section
    candidates = []
    for post in all_posts:
        post_tags = {t["name"] for t in post.get("tags", [])}
        if post_tags & SKIP_TAGS:
            continue
        if has_related_section(post.get("html", "")):
            continue
        candidates.append(post)

    if args.limit > 0:
        candidates = candidates[:args.limit]

    print(f"\n{len(candidates)} posts need related links")
    
    updated = 0
    skipped = 0
    for post in candidates:
        related = find_related(post, all_posts)
        if not related:
            skipped += 1
            continue

        related_html = build_related_html(related)
        new_html = post["html"] + related_html

        if args.dry_run:
            print(f"\n📝 {post['title']}")
            for title, url in related:
                print(f"   → {title}")
        else:
            # Re-fetch to get fresh updated_at
            token = get_token()
            r = requests.get(
                f"{GHOST_URL}/ghost/api/admin/posts/{post['id']}/",
                headers={"Authorization": f"Ghost {token}"}, timeout=10)
            if r.status_code != 200:
                print(f"  ❌ Failed to fetch {post['title']}")
                continue
            fresh = r.json()["posts"][0]
            
            if update_post_html(post["id"], new_html, fresh["updated_at"], token):
                print(f"  ✅ {post['title']} — {len(related)} related links added")
                updated += 1
            else:
                print(f"  ❌ {post['title']} — update failed")
            time.sleep(0.3)  # Rate limit

    print(f"\nDone: {updated} updated, {skipped} skipped (no related found)")


if __name__ == "__main__":
    main()
