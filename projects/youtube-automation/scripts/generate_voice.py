#!/usr/bin/env python3
"""Generate TTS narration using ElevenLabs API."""

import json
import os
import re
import sys
import requests
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"


def generate_voice(script_text, post_id, config):
    el_config = config["elevenlabs"]
    api_key = el_config["api_key"]
    voice_id = el_config["voice_id"]

    # Clean script: remove [PAUSE] markers, we'll handle timing in video
    # But keep them noted for subtitle timing
    clean_text = re.sub(r'\[PAUSE\]', '...', script_text)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": clean_text,
        "model_id": el_config.get("model_id", "eleven_multilingual_v2"),
        "voice_settings": {
            "stability": el_config.get("stability", 0.5),
            "similarity_boost": el_config.get("similarity_boost", 0.75),
        },
    }

    print(f"Generating audio for post {post_id}...")
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()

    output_dir = PROJECT_DIR / "output" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_file = output_dir / f"{post_id}.mp3"

    with open(audio_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Get audio duration using ffprobe
    import subprocess
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip()) if result.stdout.strip() else 0

    print(f"Audio generated: {audio_file} ({duration:.1f}s)")
    return str(audio_file), duration


if __name__ == "__main__":
    config_data = json.load(open(CONFIG_FILE))
    post_id = sys.argv[1] if len(sys.argv) > 1 else None

    if post_id:
        script_file = PROJECT_DIR / "output" / "scripts" / f"{post_id}.txt"
    else:
        scripts_dir = PROJECT_DIR / "output" / "scripts"
        script_files = sorted(
            [f for f in scripts_dir.glob("*.txt")],
            key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not script_files:
            print("No scripts found. Run generate_script.py first.")
            sys.exit(1)
        script_file = script_files[0]
        post_id = script_file.stem

    with open(script_file) as f:
        script_text = f.read()

    generate_voice(script_text, post_id, config_data)
