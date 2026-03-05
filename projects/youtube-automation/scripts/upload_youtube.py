#!/usr/bin/env python3
"""Upload video to YouTube via Data API v3."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_service(config):
    yt_config = config["youtube"]
    creds = None
    token_file = PROJECT_DIR / yt_config["token_file"]
    secrets_file = PROJECT_DIR / yt_config["client_secrets_file"]

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_file), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video(post_id, config, schedule_hours=None):
    video_file = PROJECT_DIR / "output" / "videos" / f"{post_id}.mp4"
    thumb_file = PROJECT_DIR / "output" / "thumbnails" / f"{post_id}.png"
    meta_file = PROJECT_DIR / "output" / "scripts" / f"{post_id}_meta.json"

    if not video_file.exists():
        print(f"Video not found: {video_file}")
        sys.exit(1)

    # Load metadata
    with open(meta_file) as f:
        meta = json.load(f)

    # Build title and description
    title = meta["title"]
    if len(title) > 90:
        title = title[:87] + "..."

    subreddit = meta["subreddit"]
    description = (
        f"📖 Reddit Story from r/{subreddit}\n\n"
        f"This story blew up on Reddit and we had to share it.\n"
        f"What would YOU have done? Let us know in the comments!\n\n"
        f"🔔 Subscribe for daily Reddit stories!\n\n"
        f"#reddit #redditstories #aita #storytime #{subreddit.lower()}\n\n"
        f"⚠️ All stories are sourced from public Reddit posts. "
        f"Names and details may be changed for privacy."
    )

    tags = [
        "reddit", "reddit stories", "aita", "storytime",
        subreddit.lower(), "reddit update", "best reddit stories",
        "reddit top posts", "reddit compilation",
    ]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "24",  # Entertainment
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    # Schedule if requested
    if schedule_hours:
        publish_at = datetime.utcnow() + timedelta(hours=schedule_hours)
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_at.isoformat() + "Z"

    youtube = get_youtube_service(config)

    print(f"Uploading: {title}")
    media = MediaFileUpload(str(video_file), mimetype="video/mp4", resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"✅ Uploaded: https://youtube.com/watch?v={video_id}")

    # Set thumbnail if available
    if thumb_file.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumb_file), mimetype="image/png"),
            ).execute()
            print("Thumbnail set.")
        except Exception as e:
            print(f"Thumbnail upload failed (may need verified account): {e}")

    return video_id


if __name__ == "__main__":
    config_data = json.load(open(CONFIG_FILE))
    post_id = sys.argv[1] if len(sys.argv) > 1 else None

    if not post_id:
        videos_dir = PROJECT_DIR / "output" / "videos"
        video_files = sorted(videos_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not video_files:
            print("No videos found.")
            sys.exit(1)
        post_id = video_files[0].stem

    upload_video(post_id, config_data)
