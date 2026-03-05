#!/usr/bin/env python3
"""
GoAPI Midjourney Image Generator
Usage:
  python3 generate.py "your prompt here" [--ar 10:16] [--mode fast|relax] [--out output.jpg]
  python3 generate.py --status TASK_ID
  python3 generate.py --upscale TASK_ID --index 1|2|3|4 [--out cover.jpg]
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

API_KEY = os.environ.get("GOAPI_KEY", "28d1e993476e658cb20cccc52afefd95efb1c7195831e6793b30e6c8bcd91f63")
API_BASE = "https://api.goapi.ai/api/v1/task"


def api_request(method, url, data=None):
    """Use curl to avoid Cloudflare 403 on urllib."""
    cmd = ["curl", "-s", "-X", method, url,
           "-H", f"x-api-key: {API_KEY}",
           "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"curl error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)


def imagine(prompt, aspect_ratio="10:16", process_mode="fast"):
    payload = {
        "model": "midjourney",
        "task_type": "imagine",
        "input": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "process_mode": process_mode,
            "skip_prompt_check": False,
        },
    }
    resp = api_request("POST", API_BASE, payload)
    if resp.get("code") != 200:
        print(f"Error: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)
    task_id = resp["data"]["task_id"]
    print(f"Task submitted: {task_id}")
    return task_id


def fetch_task(task_id):
    url = f"{API_BASE}/{task_id}"
    return api_request("GET", url)


def wait_for_task(task_id, poll_interval=5, timeout=300):
    elapsed = 0
    while elapsed < timeout:
        resp = fetch_task(task_id)
        data = resp.get("data", {})
        status = data.get("status", "unknown")
        progress = data.get("output", {}).get("progress", 0)
        print(f"  Status: {status} | Progress: {progress}%")

        if status == "completed":
            return data
        elif status == "failed":
            print(f"Task failed: {data.get('error', {})}", file=sys.stderr)
            sys.exit(1)

        time.sleep(poll_interval)
        elapsed += poll_interval

    print("Timeout waiting for task", file=sys.stderr)
    sys.exit(1)


def upscale(task_id, index):
    payload = {
        "model": "midjourney",
        "task_type": "upscale",
        "input": {
            "origin_task_id": task_id,
            "index": str(index),
        },
    }
    resp = api_request("POST", API_BASE, payload)
    if resp.get("code") != 200:
        print(f"Error: {json.dumps(resp, indent=2)}", file=sys.stderr)
        sys.exit(1)
    up_task_id = resp["data"]["task_id"]
    print(f"Upscale submitted: {up_task_id}")
    return up_task_id


def download_image(url, output_path):
    subprocess.run(["curl", "-s", "-o", output_path, url], check=True)
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="GoAPI Midjourney Generator")
    parser.add_argument("prompt", nargs="?", help="Image prompt")
    parser.add_argument("--ar", default="10:16", help="Aspect ratio (default: 10:16 for book covers)")
    parser.add_argument("--mode", default="fast", choices=["fast", "relax", "turbo"], help="Processing mode")
    parser.add_argument("--out", default=None, help="Output filename")
    parser.add_argument("--status", metavar="TASK_ID", help="Check status of a task")
    parser.add_argument("--upscale", metavar="TASK_ID", help="Upscale from a completed task")
    parser.add_argument("--index", type=int, choices=[1, 2, 3, 4], help="Which image to upscale (1-4)")
    parser.add_argument("--no-wait", action="store_true", help="Submit and exit without waiting")
    args = parser.parse_args()

    if args.status:
        resp = fetch_task(args.status)
        data = resp.get("data", {})
        print(json.dumps(data, indent=2))
        return

    if args.upscale:
        if not args.index:
            print("--index required for upscale", file=sys.stderr)
            sys.exit(1)
        up_id = upscale(args.upscale, args.index)
        data = wait_for_task(up_id)
        image_url = data.get("output", {}).get("image_url", "")
        print(f"\nUpscaled image URL: {image_url}")
        if args.out:
            download_image(image_url, args.out)
        return

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    task_id = imagine(args.prompt, args.ar, args.mode)

    if args.no_wait:
        print(f"Use --status {task_id} to check progress")
        return

    data = wait_for_task(task_id)
    output = data.get("output", {})
    image_url = output.get("image_url", "")
    image_urls = output.get("image_urls", []) or []
    actions = output.get("actions", [])

    print(f"\nGrid image: {image_url}")
    if image_urls:
        for i, url in enumerate(image_urls, 1):
            print(f"  Image {i}: {url}")
    print(f"\nTask ID (for upscale): {task_id}")
    print(f"Available actions: {actions}")

    if args.out:
        download_image(image_url, args.out)


if __name__ == "__main__":
    main()
