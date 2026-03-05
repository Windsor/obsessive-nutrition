#!/usr/bin/env python3
"""Compose final video: background gameplay + audio narration + subtitles."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_DIR / "config" / "config.json"


def get_audio_duration(audio_path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def generate_subtitles(script_text, audio_duration, post_id):
    """Generate SRT subtitles from script text, roughly timed to audio duration."""
    output_dir = PROJECT_DIR / "output" / "subtitles"
    output_dir.mkdir(parents=True, exist_ok=True)
    srt_file = output_dir / f"{post_id}.srt"

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', script_text.replace('[PAUSE]', ''))
    sentences = [s.strip() for s in sentences if s.strip()]

    # Estimate timing: distribute duration across sentences by word count
    total_words = sum(len(s.split()) for s in sentences)
    if total_words == 0:
        return str(srt_file)

    current_time = 0.0
    srt_entries = []

    for i, sentence in enumerate(sentences):
        word_count = len(sentence.split())
        duration = (word_count / total_words) * audio_duration

        # Break long sentences into chunks of ~8 words for readability
        words = sentence.split()
        chunks = []
        for j in range(0, len(words), 8):
            chunks.append(' '.join(words[j:j+8]))

        chunk_duration = duration / len(chunks)

        for chunk in chunks:
            start = current_time
            end = current_time + chunk_duration
            srt_entries.append({
                "index": len(srt_entries) + 1,
                "start": start,
                "end": end,
                "text": chunk,
            })
            current_time = end

    # Write SRT
    with open(srt_file, "w") as f:
        for entry in srt_entries:
            f.write(f"{entry['index']}\n")
            f.write(f"{format_time(entry['start'])} --> {format_time(entry['end'])}\n")
            f.write(f"{entry['text']}\n\n")

    print(f"Subtitles generated: {len(srt_entries)} entries")
    return str(srt_file)


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def compose_video(post_id, config):
    vid_config = config["video"]
    audio_file = PROJECT_DIR / "output" / "audio" / f"{post_id}.mp3"
    script_file = PROJECT_DIR / "output" / "scripts" / f"{post_id}.txt"

    if not audio_file.exists():
        print(f"Audio not found: {audio_file}")
        sys.exit(1)

    audio_duration = get_audio_duration(str(audio_file))

    # Read script for subtitles
    with open(script_file) as f:
        script_text = f.read()

    srt_file = generate_subtitles(script_text, audio_duration, post_id)

    # Find background video
    bg_dir = PROJECT_DIR / vid_config["background_dir"]
    bg_videos = list(bg_dir.glob("*.mp4")) + list(bg_dir.glob("*.mkv"))
    if not bg_videos:
        print(f"No background videos found in {bg_dir}")
        print("Add gameplay footage (Minecraft parkour, GTA, Subway Surfers) to assets/backgrounds/")
        sys.exit(1)

    bg_video = bg_videos[0]  # Use first available

    # Output
    output_dir = PROJECT_DIR / "output" / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{post_id}.mp4"

    font_path = vid_config.get("font_path", "/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    font_size = vid_config.get("font_size", 48)

    # FFmpeg command:
    # 1. Loop background video to match audio duration
    # 2. Overlay audio narration
    # 3. Burn in subtitles
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(bg_video),
        "-i", str(audio_file),
        "-vf", (
            f"scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"subtitles={srt_file}:force_style="
            f"'FontName=Arial,FontSize={font_size},PrimaryColour=&H00FFFFFF,"
            f"OutlineColour=&H00000000,Outline=2,Shadow=1,"
            f"Alignment=2,MarginV=80'"
        ),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_file),
    ]

    print(f"Compositing video ({audio_duration:.0f}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-500:]}")
        sys.exit(1)

    file_size = output_file.stat().st_size / (1024 * 1024)
    print(f"Video created: {output_file} ({file_size:.1f} MB)")
    return str(output_file)


if __name__ == "__main__":
    config_data = json.load(open(CONFIG_FILE))
    post_id = sys.argv[1] if len(sys.argv) > 1 else None

    if not post_id:
        audio_dir = PROJECT_DIR / "output" / "audio"
        audio_files = sorted(audio_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not audio_files:
            print("No audio found. Run generate_voice.py first.")
            sys.exit(1)
        post_id = audio_files[0].stem

    compose_video(post_id, config_data)
