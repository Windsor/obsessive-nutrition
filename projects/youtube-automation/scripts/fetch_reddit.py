#!/usr/bin/env python3
"""Fetch top Reddit posts from target subreddits."""

import json
import os
import sys
import praw
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"
USED_POSTS_FILE = PROJECT_DIR / "config" / "used_posts.json"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_used_posts():
    if USED_POSTS_FILE.exists():
        with open(USED_POSTS_FILE) as f:
            return set(json.load(f))
    return set()


def save_used_posts(used):
    with open(USED_POSTS_FILE, "w") as f:
        json.dump(list(used), f)


def fetch_posts(config, count=1):
    reddit = praw.Reddit(
        client_id=config["reddit"]["client_id"],
        client_secret=config["reddit"]["client_secret"],
        user_agent=config["reddit"]["user_agent"],
    )

    used = load_used_posts()
    min_len = config.get("min_post_length", 500)
    max_len = config.get("max_post_length", 10000)
    posts = []

    for sub_name in config["subreddits"]:
        if len(posts) >= count:
            break
        subreddit = reddit.subreddit(sub_name)

        for post in subreddit.hot(limit=50):
            if post.id in used:
                continue
            if post.is_self and min_len <= len(post.selftext) <= max_len:
                # Check engagement
                if post.score < 500:
                    continue
                posts.append({
                    "id": post.id,
                    "subreddit": sub_name,
                    "title": post.title,
                    "text": post.selftext,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "fetched_at": datetime.utcnow().isoformat(),
                })
                used.add(post.id)
                if len(posts) >= count:
                    break

    save_used_posts(used)

    # Save fetched posts
    output_dir = PROJECT_DIR / "output" / "posts"
    output_dir.mkdir(parents=True, exist_ok=True)

    for post in posts:
        filename = f"{post['id']}.json"
        with open(output_dir / filename, "w") as f:
            json.dump(post, f, indent=2)
        print(f"Fetched: r/{post['subreddit']} - {post['title'][:60]}...")

    return posts


if __name__ == "__main__":
    config = load_config()
    count = int(sys.argv[1]) if len(sys.argv) > 1 else config.get("posts_per_run", 1)
    posts = fetch_posts(config, count)
    if not posts:
        print("No new posts found matching criteria.")
        sys.exit(1)
    print(f"\nFetched {len(posts)} posts.")
