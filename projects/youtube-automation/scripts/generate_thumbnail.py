#!/usr/bin/env python3
"""Generate YouTube thumbnail using GoAPI AI image generation."""

import json
import os
import sys
import time
import requests
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"

GOAPI_KEY = "28d1e993476e658cb20cccc52afefd95efb1c7195831e6793b30e6c8bcd91f63"
GOAPI_URL = "https://api.goapi.ai/api/v1/task"


def generate_thumbnail(post_data, config):
    """Generate a dramatic thumbnail image for the video."""
    title = post_data["title"]
    subreddit = post_data["subreddit"]

    # Create a thumbnail prompt based on the story
    prompt = (
        f"YouTube thumbnail style, dramatic and eye-catching, "
        f"shocked facial expression emoji style, bold text overlay area, "
        f"dark moody background, Reddit story theme about: {title[:100]}, "
        f"cinematic lighting, high contrast, 4K quality, no text"
    )

    # Use Gemini Flash for speed/cost
    payload = {
        "model": "gemini",
        "task_type": "gemini-2.5-flash-image",
        "input": {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "resolution": "1K",
        },
    }

    headers = {"x-api-key": GOAPI_KEY, "Content-Type": "application/json"}

    print("Generating thumbnail...")
    response = requests.post(GOAPI_URL, headers=headers, json=payload)
    response.raise_for_status()
    task = response.json()
    task_id = task["data"]["task_id"]

    # Poll for completion
    for _ in range(60):
        time.sleep(3)
        poll = requests.get(f"{GOAPI_URL}/{task_id}", headers=headers)
        poll.raise_for_status()
        data = poll.json()["data"]
        status = data.get("status")

        if status == "completed":
            image_url = data["output"]["image_urls"][0]
            # Download image
            output_dir = PROJECT_DIR / "output" / "thumbnails"
            output_dir.mkdir(parents=True, exist_ok=True)
            thumb_file = output_dir / f"{post_data['id']}.png"

            img_response = requests.get(image_url)
            with open(thumb_file, "wb") as f:
                f.write(img_response.content)

            print(f"Thumbnail saved: {thumb_file}")
            return str(thumb_file)
        elif status == "failed":
            print(f"Thumbnail generation failed: {data.get('error')}")
            return None

    print("Thumbnail generation timed out.")
    return None


if __name__ == "__main__":
    config_data = json.load(open(CONFIG_FILE))
    post_id = sys.argv[1] if len(sys.argv) > 1 else None

    if not post_id:
        posts_dir = PROJECT_DIR / "output" / "posts"
        post_files = sorted(posts_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not post_files:
            print("No posts found.")
            sys.exit(1)
        post_file = post_files[0]
        post_id = post_file.stem
    else:
        post_file = PROJECT_DIR / "output" / "posts" / f"{post_id}.json"

    with open(post_file) as f:
        post = json.load(f)

    generate_thumbnail(post, config_data)
