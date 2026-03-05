#!/usr/bin/env python3
"""Download free stock background videos from Pexels for video compositing."""

import json
import os
import sys
import requests
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"

# Pexels API - free, just needs an API key from pexels.com/api
# No attribution required for videos

SEARCH_QUERIES = [
    "abstract particles loop",
    "abstract light loop",
    "neon abstract background",
    "flowing water abstract",
    "night city aerial",
    "ocean waves aerial",
    "clouds timelapse",
    "northern lights",
    "rain on window",
    "fireplace close up",
    "stars timelapse night sky",
    "abstract smoke",
    "satisfying liquid",
    "deep ocean underwater",
]


def fetch_backgrounds(api_key, count_per_query=2, min_duration=30):
    """Download background videos from Pexels."""
    bg_dir = PROJECT_DIR / "assets" / "backgrounds"
    bg_dir.mkdir(parents=True, exist_ok=True)

    headers = {"Authorization": api_key}
    downloaded = 0

    for query in SEARCH_QUERIES:
        print(f"\nSearching: {query}")
        params = {
            "query": query,
            "per_page": 10,
            "orientation": "portrait",  # 9:16 for Shorts/TikTok style
            "size": "medium",
        }

        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
        )

        if resp.status_code == 429:
            print("Rate limited, stopping.")
            break

        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text[:200]}")
            continue

        videos = resp.json().get("videos", [])
        found = 0

        for video in videos:
            if found >= count_per_query:
                break

            duration = video.get("duration", 0)
            if duration < min_duration:
                continue

            # Get the HD file
            video_files = video.get("video_files", [])
            # Prefer HD portrait
            best = None
            for vf in video_files:
                w = vf.get("width", 0)
                h = vf.get("height", 0)
                if h >= 1080 and vf.get("link"):
                    if best is None or h > best.get("height", 0):
                        best = vf

            if not best:
                # Fallback to any decent quality
                for vf in video_files:
                    if vf.get("height", 0) >= 720 and vf.get("link"):
                        best = vf
                        break

            if not best:
                continue

            vid_id = video["id"]
            filename = f"pexels_{vid_id}.mp4"
            filepath = bg_dir / filename

            if filepath.exists():
                print(f"  Already have: {filename}")
                found += 1
                continue

            print(f"  Downloading: {filename} ({duration}s, {best.get('width')}x{best.get('height')})")
            dl = requests.get(best["link"], stream=True)
            with open(filepath, "wb") as f:
                for chunk in dl.iter_content(chunk_size=8192):
                    f.write(chunk)

            found += 1
            downloaded += 1

    print(f"\n✅ Downloaded {downloaded} background videos to {bg_dir}")
    existing = list(bg_dir.glob("*.mp4"))
    print(f"Total backgrounds available: {len(existing)}")


if __name__ == "__main__":
    config = json.load(open(CONFIG_FILE))
    api_key = config.get("pexels", {}).get("api_key", "")

    if not api_key:
        print("No Pexels API key found in config.")
        print("Get a free key at: https://www.pexels.com/api/")
        print("Add to config.json: {\"pexels\": {\"api_key\": \"YOUR_KEY\"}}")
        sys.exit(1)

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    fetch_backgrounds(api_key, count_per_query=count)
