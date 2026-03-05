#!/usr/bin/env python3
"""Generate a weekly digest post for The Portugal Brief.

Fetches the past week's most important articles (by tag diversity and recency),
creates a curated roundup, and optionally publishes it.

Usage:
    python weekly-digest.py --preview          # Preview digest
    python weekly-digest.py --publish          # Publish as draft
    python weekly-digest.py --publish --send   # Publish and send as newsletter
"""

import jwt, time, requests, json, sys, argparse, re
from datetime import datetime, timezone, timedelta
from collections import Counter

GHOST_URL = "https://theportugalbrief.pt"
ADMIN_KEY = "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"

# Tags to skip (briefings are summaries, not standalone stories)
SKIP_TAGS = {"Daily Briefing", "Afternoon Update", "Markets Briefing"}
# Priority tags — stories with these get boosted
PRIORITY_TAGS = {"Politics", "Economy", "Housing", "Health", "Defense"}


def get_token():
    kid, secret = ADMIN_KEY.split(":")
    iat = int(time.time())
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    payload = {"iat": iat, "exp": iat + 300, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)


def fetch_week_posts(token, days=7):
    """Fetch published posts from the past N days."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    posts = []
    page = 1
    while True:
        r = requests.get(
            f"{GHOST_URL}/ghost/api/admin/posts/?limit=50&page={page}"
            f"&filter=status:published%2Bpublished_at:>'{since}'"
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


def score_post(post):
    """Score a post for digest inclusion. Higher = more important."""
    tags = {t["name"] for t in post.get("tags", [])}
    
    # Skip briefings
    if tags & SKIP_TAGS:
        return -1
    
    score = 0
    # Priority tag boost
    score += len(tags & PRIORITY_TAGS) * 10
    
    # Longer articles score higher (deeper reporting)
    html_len = len(post.get("html", ""))
    if html_len > 5000:
        score += 15
    elif html_len > 3000:
        score += 10
    elif html_len > 1500:
        score += 5
    
    # Social tag = was cross-posted, indicates importance
    if "social" in tags:
        score += 5
    
    # Recency bonus (newer posts get slight boost)
    published = post.get("published_at", "")
    if published:
        age_hours = (datetime.now(timezone.utc) - datetime.fromisoformat(published.replace("Z", "+00:00"))).total_seconds() / 3600
        if age_hours < 48:
            score += 3
    
    return score


def select_digest_stories(posts, max_stories=10):
    """Select the best stories for the digest, ensuring topic diversity."""
    scored = [(score_post(p), p) for p in posts]
    scored = [(s, p) for s, p in scored if s >= 0]
    scored.sort(key=lambda x: -x[0])
    
    selected = []
    seen_topics = []
    
    for score, post in scored:
        # Simple dedup: skip if title words heavily overlap with already selected
        title_words = set(post["title"].lower().split())
        if any(len(title_words & seen) > 4 for seen in seen_topics):
            continue
        
        selected.append(post)
        seen_topics.append(title_words)
        
        if len(selected) >= max_stories:
            break
    
    return selected


def extract_lead(html, max_chars=200):
    """Extract the lead paragraph from HTML."""
    text = re.sub(r'<[^>]+>', ' ', html or "")
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(' ', 1)[0] + '...'
    return text


def build_digest_html(stories, week_start, week_end):
    """Build the weekly digest HTML."""
    items = []
    for post in stories:
        lead = extract_lead(post.get("html", ""))
        url = post["url"]
        title = post["title"]
        items.append(f"""<h3><a href="{url}">{title}</a></h3>
<p>{lead}</p>""")
    
    stories_html = "\n\n".join(items)
    
    return f"""<p><em>The week's most important Portugal stories, curated from our daily coverage.</em></p>

<p>This week in Portugal: the stories that mattered most, from politics and the economy to housing, health, and culture. If you missed anything, start here.</p>

{stories_html}

<hr>
<p><em>That's the week. For daily coverage, <a href="https://theportugalbrief.pt/#/portal/signup">subscribe free</a> and never miss a story.</em></p>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--send", action="store_true", help="Send as newsletter")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--max-stories", type=int, default=10)
    args = parser.parse_args()

    token = get_token()
    posts = fetch_week_posts(token, args.days)
    print(f"Found {len(posts)} posts from past {args.days} days")

    stories = select_digest_stories(posts, args.max_stories)
    print(f"Selected {len(stories)} stories for digest")

    now = datetime.now(timezone.utc)
    week_end = now.strftime("%B %d")
    week_start = (now - timedelta(days=args.days)).strftime("%B %d")
    title = f"Weekly Digest — {week_start} to {week_end}, {now.year}"

    digest_html = build_digest_html(stories, week_start, week_end)

    if args.preview or not args.publish:
        print(f"\n{'='*60}")
        print(f"Title: {title}")
        print(f"{'='*60}")
        for i, s in enumerate(stories, 1):
            tags = ", ".join(t["name"] for t in s.get("tags", []) if t["name"] not in SKIP_TAGS)
            print(f"  {i}. {s['title']} [{tags}]")
        print(f"{'='*60}")

    if args.publish:
        from publish import publish_post
        result = publish_post(
            title=title,
            html=digest_html,
            tags=["Weekly Digest"],
            status="published" if args.send else "draft",
            feature_image="https://images.unsplash.com/photo-1504711434969-e33886168d9c?w=1200",
            send_email=args.send,
        )
        if result:
            print(f"\n✅ Digest published: {result.get('url', 'OK')}")
        else:
            print("\n❌ Publish failed")


if __name__ == "__main__":
    main()
