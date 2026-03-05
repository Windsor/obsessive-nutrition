#!/usr/bin/env python3
"""Full pipeline: fetch → script → voice → video → thumbnail → upload."""

import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"

from fetch_reddit import fetch_posts
from generate_script import generate_script
from generate_voice import generate_voice
from compose_video import compose_video
from generate_thumbnail import generate_thumbnail
from upload_youtube import upload_video


def run_pipeline(config, upload=False, schedule_hours=None):
    print("=" * 60)
    print("🎬 YouTube Automation Pipeline")
    print("=" * 60)

    # Step 1: Fetch Reddit post
    print("\n📥 Step 1: Fetching Reddit post...")
    posts = fetch_posts(config, count=1)
    if not posts:
        print("❌ No suitable posts found.")
        return None

    post = posts[0]
    post_id = post["id"]
    print(f"✅ Got: {post['title'][:60]}...")

    # Step 2: Generate script
    print(f"\n✍️ Step 2: Generating narration script...")
    script = generate_script(post, config)
    print(f"✅ Script ready ({len(script.split())} words)")

    # Step 3: Generate voice
    print(f"\n🎙️ Step 3: Generating voice narration...")
    audio_path, duration = generate_voice(script, post_id, config)
    print(f"✅ Audio ready ({duration:.0f}s)")

    # Step 4: Compose video
    print(f"\n🎬 Step 4: Compositing video...")
    video_path = compose_video(post_id, config)
    print(f"✅ Video ready")

    # Step 5: Generate thumbnail
    print(f"\n🖼️ Step 5: Generating thumbnail...")
    thumb = generate_thumbnail(post, config)
    if thumb:
        print(f"✅ Thumbnail ready")
    else:
        print(f"⚠️ Thumbnail failed, continuing without")

    # Step 6: Upload (if enabled)
    if upload:
        print(f"\n📤 Step 6: Uploading to YouTube...")
        video_id = upload_video(post_id, config, schedule_hours)
        print(f"✅ Published: https://youtube.com/watch?v={video_id}")
    else:
        print(f"\n⏸️ Step 6: Upload skipped (run with --upload to publish)")
        video_id = None

    print("\n" + "=" * 60)
    print(f"✅ Pipeline complete for post {post_id}")
    print("=" * 60)

    return {
        "post_id": post_id,
        "title": post["title"],
        "video_path": video_path,
        "video_id": video_id,
    }


if __name__ == "__main__":
    config = json.load(open(CONFIG_FILE))
    do_upload = "--upload" in sys.argv
    schedule = None
    for arg in sys.argv:
        if arg.startswith("--schedule="):
            schedule = int(arg.split("=")[1])

    run_pipeline(config, upload=do_upload, schedule_hours=schedule)
