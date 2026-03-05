#!/usr/bin/env python3
"""Publish a post to Ghost CMS via Admin API.

Usage:
    python publish.py publish --title "My Post" --html "<p>Content</p>" --status published
    python publish.py publish-json --json-file article.json
    python publish.py list --limit 20 --status published
    python publish.py update --id <post_id> --status published
    python publish.py delete --id <post_id>
"""

import jwt, time, requests, json, sys, argparse, re

GHOST_URL = "https://theportugalbrief.pt"
ADMIN_KEY = "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"
MAX_RETRIES = 2
RETRY_BACKOFF = 2  # seconds


def get_token():
    kid, secret = ADMIN_KEY.split(":")
    iat = int(time.time())
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    payload = {"iat": iat, "exp": iat + 300, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)


def _request_with_retry(method, url, **kwargs):
    """Make an HTTP request with retry on transient errors."""
    kwargs.setdefault("timeout", 30)
    last_exc = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            r = method(url, **kwargs)
            if r.status_code >= 500 and attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF * (attempt + 1))
                continue
            return r
        except (requests.ConnectionError, requests.Timeout) as e:
            last_exc = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF * (attempt + 1))
    raise last_exc


def _auto_excerpt(html, max_chars=250):
    """Generate custom_excerpt from HTML if not provided."""
    if not html:
        return None
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(' ', 1)[0] + '...'
    return text if text else None


def _auto_meta_description(html, max_chars=155):
    """Generate meta_description from HTML if not provided."""
    if not html:
        return None
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(' ', 1)[0] + '...'
    return text


def _check_duplicate(title, token):
    """Check if a post with same or very similar title exists in today's posts.
    Returns post ID if duplicate found (exact match or high keyword overlap)."""
    STOP_WORDS = {"the", "a", "an", "of", "in", "to", "and", "for", "is", "as", "at",
                  "on", "by", "its", "has", "with", "--", "—", "portugal", "portuguese"}
    try:
        r = requests.get(
            f"{GHOST_URL}/ghost/api/admin/posts/?limit=20&order=published_at%20desc&fields=id,title,published_at",
            headers={"Authorization": f"Ghost {token}"}, timeout=10)
        if r.status_code == 200:
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            new_words = set(title.strip().lower().split()) - STOP_WORDS
            for p in r.json()["posts"]:
                # Exact title match
                if p["title"].strip().lower() == title.strip().lower():
                    return p["id"]
                # Keyword similarity check (only for today's posts, skip briefings)
                if (p.get("published_at", "").startswith(today) and
                    "briefing" not in title.lower() and
                    "briefing" not in p["title"].lower() and
                    "update" not in title.lower() and
                    "update" not in p["title"].lower()):
                    existing_words = set(p["title"].strip().lower().split()) - STOP_WORDS
                    overlap = new_words & existing_words
                    # If 5+ meaningful words overlap, it's likely a duplicate topic
                    if len(overlap) >= 5 and len(overlap) / max(len(new_words), 1) > 0.4:
                        return p["id"]
    except Exception:
        pass
    return None


def publish_post(title, html, tags=None, status="draft", excerpt=None,
                 feature_image=None, meta_description=None, send_email=False):
    """Publish a post. Status: draft, published, scheduled.
    If send_email=True, sends as newsletter to all members."""
    token = get_token()
    
    # Dedup check: skip if same title already exists
    existing_id = _check_duplicate(title, token)
    if existing_id:
        print(json.dumps({"ok": False, "error": "duplicate", "existing_id": existing_id,
                          "message": f"Post with title '{title}' already exists. Use update instead."}))
        return None
    
    # If sending email, add newsletter query param
    url = f"{GHOST_URL}/ghost/api/admin/posts/?source=html"
    if send_email and status == "published":
        url += "&newsletter=default-newsletter&email_segment=all"
    
    post = {
        "title": title,
        "html": html,
        "status": status,
    }
    if tags:
        post["tags"] = [{"name": t} for t in tags]
    # Auto-generate excerpt from HTML if not provided
    custom_excerpt = excerpt or _auto_excerpt(html)
    if custom_excerpt:
        post["custom_excerpt"] = custom_excerpt
    if feature_image:
        post["feature_image"] = feature_image
    # Auto-generate meta description if not provided
    meta = meta_description or _auto_meta_description(html)
    if meta:
        post["meta_description"] = meta
    # Auto-generate SEO meta_title and og fields
    site_name = "The Portugal Brief" if "theportugalbrief" in GHOST_URL or "ghost-portugal" in GHOST_URL else "Daily Finance Pulse"
    seo_title = f"{title} | {site_name}"
    if len(seo_title) > 65:
        seo_title = title[:57] + "..."
    post["meta_title"] = seo_title
    post["og_title"] = title
    if custom_excerpt:
        post["og_description"] = custom_excerpt[:300]
    
    r = _request_with_retry(requests.post, url, json={"posts": [post]},
                            headers={"Authorization": f"Ghost {token}"})
    
    if r.status_code == 201:
        p = r.json()["posts"][0]
        print(json.dumps({"ok": True, "id": p["id"], "slug": p["slug"], "url": p["url"], "status": p["status"]}))
        return p
    else:
        print(json.dumps({"ok": False, "status": r.status_code, "error": r.text[:500]}))
        return None

def update_post(post_id, html=None, title=None, status=None, tags=None, meta_description=None):
    """Update an existing post."""
    token = get_token()
    headers = {"Authorization": f"Ghost {token}"}
    
    # First get the current post for updated_at
    r = _request_with_retry(requests.get,
                            f"{GHOST_URL}/ghost/api/admin/posts/{post_id}/",
                            headers=headers, timeout=10)
    if r.status_code != 200:
        print(json.dumps({"ok": False, "error": f"Could not fetch post ({r.status_code})"}))
        return None
    current = r.json()["posts"][0]
    
    post = {"updated_at": current["updated_at"]}
    if html: post["html"] = html
    if title: post["title"] = title
    if status: post["status"] = status
    if tags: post["tags"] = [{"name": t} for t in tags]
    if meta_description: post["meta_description"] = meta_description
    
    r = _request_with_retry(requests.put,
                            f"{GHOST_URL}/ghost/api/admin/posts/{post_id}/",
                            json={"posts": [post]}, headers=headers)
    if r.status_code == 200:
        p = r.json()["posts"][0]
        print(json.dumps({"ok": True, "id": p["id"], "slug": p["slug"], "status": p["status"]}))
        return p
    else:
        print(json.dumps({"ok": False, "status": r.status_code, "error": r.text[:500]}))
        return None

def publish_from_json(json_path):
    """Publish from a JSON file: {"title": "...", "html": "...", "tags": [...], "status": "draft"}"""
    with open(json_path) as f:
        data = json.load(f)
    return publish_post(
        title=data["title"],
        html=data["html"],
        tags=data.get("tags"),
        status=data.get("status", "draft"),
        excerpt=data.get("excerpt"),
        feature_image=data.get("feature_image"),
        meta_description=data.get("meta_description"),
        send_email=data.get("send_email", False),
    )

def list_posts(limit=10, status="all"):
    token = get_token()
    url = f"{GHOST_URL}/ghost/api/admin/posts/?limit={limit}&filter=status:{status}&formats=html"
    r = requests.get(url, headers={"Authorization": f"Ghost {token}"}, timeout=10)
    if r.status_code == 200:
        for p in r.json()["posts"]:
            html_len = len(p.get("html") or "")
            print(f"[{p['status']}] {p['title']} (id:{p['id']}, html:{html_len} chars)")
    return r.json() if r.status_code == 200 else None

def delete_post(post_id):
    token = get_token()
    r = _request_with_retry(requests.delete,
                            f"{GHOST_URL}/ghost/api/admin/posts/{post_id}/",
                            headers={"Authorization": f"Ghost {token}"}, timeout=10)
    print(json.dumps({"ok": r.status_code == 204, "status": r.status_code}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["publish", "publish-json", "update", "list", "delete"])
    parser.add_argument("--title", default="")
    parser.add_argument("--html", default="")
    parser.add_argument("--html-file", help="Read HTML from a file")
    parser.add_argument("--json-file", help="Publish from a JSON file")
    parser.add_argument("--tags", nargs="*")
    parser.add_argument("--status", default="draft")
    parser.add_argument("--excerpt")
    parser.add_argument("--id", help="Post ID for update/delete")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--stdin", action="store_true", help="Read HTML from stdin")
    args = parser.parse_args()
    
    if args.action == "publish":
        html = args.html
        if args.html_file:
            with open(args.html_file) as f:
                html = f.read()
        elif args.stdin:
            html = sys.stdin.read()
        publish_post(args.title, html, args.tags, args.status, args.excerpt)
    elif args.action == "publish-json":
        publish_from_json(args.json_file or args.html_file)
    elif args.action == "update":
        html = args.html or None
        if args.html_file:
            with open(args.html_file) as f:
                html = f.read()
        elif args.stdin:
            html = sys.stdin.read()
        update_post(args.id, html=html, title=args.title or None, status=args.status if args.status != "draft" else None)
    elif args.action == "list":
        list_posts(args.limit, args.status)
    elif args.action == "delete":
        delete_post(args.id)
