#!/usr/bin/env python3
"""
Finance Video V2 — Full Pipeline
Orchestrates: data collection → script → voice → render → output
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.expanduser("~/finance-video-generator/output-v2")


def collect_data():
    """Collect market data using existing finance publisher pipeline."""
    sys.path.insert(0, os.path.expanduser("~/finance-publisher"))
    try:
        from data_pipeline import collect_all_data
        print("Collecting market data...")
        data = collect_all_data()
        return data
    except ImportError:
        # Fallback: try the workspace copy
        sys.path.insert(0, os.path.join(TOOL_DIR, "..", "finance-publisher"))
        from data_pipeline import collect_all_data
        data = collect_all_data()
        return data


def run_pipeline(profile="landscape", skip_voice=False, data_path=None):
    """Run the full video generation pipeline."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Step 1: Collect data
    if data_path:
        with open(data_path) as f:
            market_data = json.load(f)
        if "market" in market_data:
            market_data = market_data["market"]
    else:
        market_data = collect_data()

    data_file = os.path.join(OUTPUT_DIR, f"data-{date_str}.json")
    with open(data_file, "w") as f:
        json.dump(market_data, f, indent=2)
    print(f"Data saved: {data_file}")

    # Step 2: Generate script
    print("\n--- GENERATING SCRIPT ---")
    script_file = os.path.join(OUTPUT_DIR, f"script-{date_str}.json")
    result = subprocess.run([
        sys.executable, os.path.join(TOOL_DIR, "generate_script.py"),
        "--data", data_file,
        "--output", script_file,
    ], capture_output=True, text=True, timeout=120)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Script error: {result.stderr}")
        # Continue without script — use default timing
        script_file = None

    # Step 3: Generate voice
    audio_manifest = None
    if not skip_voice and script_file and os.path.exists(script_file):
        print("\n--- GENERATING VOICE ---")
        audio_dir = os.path.join(OUTPUT_DIR, f"audio-{date_str}")
        result = subprocess.run([
            sys.executable, os.path.join(TOOL_DIR, "generate_voice.py"),
            "--script", script_file,
            "--output-dir", audio_dir,
        ], capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.returncode == 0:
            manifest_path = os.path.join(audio_dir, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path) as f:
                    audio_manifest = json.load(f)

    # Step 4: Render video
    print("\n--- RENDERING VIDEO ---")
    output_path = os.path.join(OUTPUT_DIR, f"market-recap-v2-{date_str}-{profile}.mp4")

    # Save audio manifest for renderer
    manifest_file = None
    if audio_manifest:
        manifest_file = os.path.join(OUTPUT_DIR, f"audio-manifest-{date_str}.json")
        with open(manifest_file, "w") as f:
            json.dump(audio_manifest, f, indent=2)

    cmd = [
        sys.executable, os.path.join(TOOL_DIR, "render_video.py"),
        "--data", data_file,
        "--profile", profile,
        "--output", output_path,
    ]
    if manifest_file:
        cmd.extend(["--audio-manifest", manifest_file])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Render error: {result.stderr}")
        return None

    print(f"\n✅ Video ready: {output_path}")
    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Finance Video V2 Pipeline")
    parser.add_argument("--profile", choices=["shorts", "landscape"], default="landscape")
    parser.add_argument("--skip-voice", action="store_true", help="Skip TTS generation")
    parser.add_argument("--data", help="Pre-collected market data JSON")
    args = parser.parse_args()

    result = run_pipeline(
        profile=args.profile,
        skip_voice=args.skip_voice,
        data_path=args.data,
    )

    if result:
        print(f"\nOutput: {result}")
        size = os.path.getsize(result)
        print(f"Size: {size / (1024*1024):.1f}MB")
    else:
        print("\nPipeline failed!")
        sys.exit(1)
