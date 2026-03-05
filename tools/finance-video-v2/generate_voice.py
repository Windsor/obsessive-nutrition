#!/usr/bin/env python3
"""
Finance Video V2 — Voice Generator
Uses OpenAI TTS (via openclaw's configured provider) for narration.
Falls back to shell `openclaw` or direct API if available.
"""

import json
import os
import subprocess
import time
import glob


def generate_segment_audio_via_openai(text, output_path):
    """Generate TTS via OpenAI API directly."""
    api_key = os.environ.get("OPENAI_API_KEY", "")

    # Clean text
    clean = text.replace("[PAUSE]", "...").replace("*", "")

    cmd = [
        "curl", "-s",
        "https://api.openai.com/v1/audio/speech",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": "tts-1-hd",
            "input": clean,
            "voice": "onyx",
            "response_format": "mp3",
            "speed": 0.95,
        }),
        "-o", output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return _check_audio_result(output_path)


def generate_segment_audio_via_script(text, output_path):
    """Generate TTS using a helper script that calls the TTS provider."""
    clean = text.replace("[PAUSE]", "...").replace("*", "")

    # Write text to temp file
    text_file = output_path + ".txt"
    with open(text_file, "w") as f:
        f.write(clean)

    # Use Python openai library if available
    script = f'''
import sys
try:
    from openai import OpenAI
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="onyx",
        input="""{clean.replace('"', '\\"')}""",
        speed=0.95,
    )
    response.stream_to_file("{output_path}")
    print("OK")
except Exception as e:
    print(f"ERROR: {{e}}", file=sys.stderr)
    sys.exit(1)
'''

    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=60
    )

    if os.path.exists(text_file):
        os.remove(text_file)

    if result.returncode == 0 and os.path.exists(output_path):
        return _check_audio_result(output_path)

    print(f"  Script TTS failed: {result.stderr.strip()}")
    return None


def _check_audio_result(output_path):
    """Verify audio file and get duration."""
    if not os.path.exists(output_path):
        return None

    size = os.path.getsize(output_path)
    if size < 500:
        # Might be an error JSON
        try:
            with open(output_path, "r") as f:
                err = json.load(f)
            print(f"  TTS returned error: {err}")
            os.remove(output_path)
            return None
        except:
            pass

    # Get duration
    dur_cmd = [
        "ffprobe", "-v", "quiet", "-show_entries",
        "format=duration", "-of", "csv=p=0", output_path
    ]
    dur_result = subprocess.run(dur_cmd, capture_output=True, text=True)
    duration = float(dur_result.stdout.strip()) if dur_result.stdout.strip() else 0

    print(f"  Generated: {output_path} ({size/1024:.1f}KB, {duration:.1f}s)")
    return {"path": output_path, "duration": duration, "size": size}


def generate_all_audio(script, output_dir="/tmp/finance-audio"):
    """Generate audio for all script segments."""
    os.makedirs(output_dir, exist_ok=True)

    segments = script.get("segments", [])
    audio_segments = []

    for i, seg in enumerate(segments):
        text = seg["text"]
        output_path = os.path.join(output_dir, f"seg_{i:02d}_{seg['id']}.mp3")
        print(f"Generating voice for segment {i}: {seg['id']} ({len(text)} chars)...")

        # Try OpenAI direct first, then script method
        result = generate_segment_audio_via_script(text, output_path)

        if result:
            audio_segments.append({
                **seg,
                "audio_path": result["path"],
                "audio_duration": result["duration"],
            })
            time.sleep(0.3)
        else:
            print(f"  FAILED: segment {i} — using duration hint")
            audio_segments.append({
                **seg,
                "audio_path": None,
                "audio_duration": seg.get("duration_hint", 10),
            })

    # Concatenate all audio with small gaps between segments
    concat_list = os.path.join(output_dir, "concat.txt")
    silence_path = os.path.join(output_dir, "silence.mp3")

    # Generate 0.5s silence for gaps
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        "anullsrc=r=44100:cl=mono", "-t", "0.5",
        "-c:a", "libmp3lame", silence_path,
    ], capture_output=True)

    with open(concat_list, "w") as f:
        for j, seg in enumerate(audio_segments):
            if seg["audio_path"] and os.path.exists(seg["audio_path"]):
                f.write(f"file '{seg['audio_path']}'\n")
                if j < len(audio_segments) - 1:
                    f.write(f"file '{silence_path}'\n")

    full_audio = os.path.join(output_dir, "full_narration.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c:a", "libmp3lame", "-b:a", "192k",
        full_audio,
    ], capture_output=True)

    # Get total duration
    dur_cmd = [
        "ffprobe", "-v", "quiet", "-show_entries",
        "format=duration", "-of", "csv=p=0", full_audio
    ]
    dur_result = subprocess.run(dur_cmd, capture_output=True, text=True)
    total_duration = float(dur_result.stdout.strip()) if dur_result.stdout.strip() else 0

    print(f"\nFull narration: {full_audio} ({total_duration:.1f}s)")

    return {
        "segments": audio_segments,
        "full_audio": full_audio,
        "total_duration": total_duration,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, help="Script JSON file")
    parser.add_argument("--output-dir", default="/tmp/finance-audio")
    args = parser.parse_args()

    with open(args.script) as f:
        script = json.load(f)

    result = generate_all_audio(script, args.output_dir)

    manifest_path = os.path.join(args.output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Manifest: {manifest_path}")
