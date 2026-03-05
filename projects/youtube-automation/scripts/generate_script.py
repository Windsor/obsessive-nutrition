#!/usr/bin/env python3
"""Generate YouTube narration script from Reddit post.

Two modes:
  1. Via OpenClaw/Saturday (default) — writes prompt to a request file, 
     Saturday processes it and writes the script.
  2. Via Anthropic API (if api_key in config) — direct Claude call.

For automated pipeline, use mode 1: the cron job creates the request,
Saturday picks it up during heartbeat and generates the script.
"""

import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"

SYSTEM_PROMPT = """You are a professional YouTube script writer for a Reddit Stories channel.

Your job: Take a Reddit post and rewrite it as an engaging, dramatic narration script.

Rules:
- Start with a strong hook (first 5 seconds must grab attention)
- Write in first person as if YOU are the person telling the story
- Add dramatic pauses with [PAUSE] markers
- Keep the core story intact but make it flow better for audio
- Add a brief intro like "This story was posted on Reddit's [subreddit] and it blew up..."
- End with a question to drive engagement: "What would you have done? Let me know in the comments."
- Target 8-12 minutes of narration (roughly 1200-1800 words)
- Use natural, conversational language — NOT robotic or formal
- Break into paragraphs for natural breathing points
- DO NOT include any visual directions, only the spoken narration text

Output ONLY the narration script text. No headers, no labels, no markdown."""


def generate_script_api(post_data, config):
    """Direct API call to Claude."""
    api_key = config["anthropic"]["api_key"]

    prompt = f"""Rewrite this Reddit post as a YouTube narration script.

Subreddit: r/{post_data['subreddit']}
Title: {post_data['title']}
Score: {post_data['score']} upvotes, {post_data['num_comments']} comments

Original post:
{post_data['text']}"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


def generate_script_request(post_data):
    """Create a script request for Saturday to process."""
    requests_dir = PROJECT_DIR / "output" / "script_requests"
    requests_dir.mkdir(parents=True, exist_ok=True)

    request = {
        "post_id": post_data["id"],
        "subreddit": post_data["subreddit"],
        "title": post_data["title"],
        "text": post_data["text"],
        "score": post_data["score"],
        "num_comments": post_data["num_comments"],
        "requested_at": datetime.utcnow().isoformat(),
        "status": "pending",
    }

    req_file = requests_dir / f"{post_data['id']}.json"
    with open(req_file, "w") as f:
        json.dump(request, f, indent=2)

    print(f"Script request created: {req_file}")
    print("Saturday will process this during next heartbeat or on-demand.")
    return str(req_file)


def save_script(script_text, post_data):
    """Save generated script and metadata."""
    output_dir = PROJECT_DIR / "output" / "scripts"
    output_dir.mkdir(parents=True, exist_ok=True)

    script_file = output_dir / f"{post_data['id']}.txt"
    with open(script_file, "w") as f:
        f.write(script_text)

    meta = {
        "post_id": post_data["id"],
        "title": post_data["title"],
        "subreddit": post_data["subreddit"],
        "word_count": len(script_text.split()),
        "estimated_minutes": len(script_text.split()) / 150,
    }
    meta_file = output_dir / f"{post_data['id']}_meta.json"
    with open(meta_file, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Script saved: {len(script_text.split())} words (~{meta['estimated_minutes']:.1f} min)")
    return script_text


if __name__ == "__main__":
    config_data = json.load(open(CONFIG_FILE))
    post_id = sys.argv[1] if len(sys.argv) > 1 else None
    use_api = "--api" in sys.argv

    if post_id:
        post_file = PROJECT_DIR / "output" / "posts" / f"{post_id}.json"
    else:
        posts_dir = PROJECT_DIR / "output" / "posts"
        post_files = sorted(posts_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not post_files:
            print("No posts found. Run fetch_reddit.py first.")
            sys.exit(1)
        post_file = post_files[0]

    with open(post_file) as f:
        post = json.load(f)

    if use_api and config_data.get("anthropic", {}).get("api_key"):
        script = generate_script_api(post, config_data)
        save_script(script, post)
    else:
        generate_script_request(post)
