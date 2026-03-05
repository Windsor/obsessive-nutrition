#!/usr/bin/env python3
"""
Finance Video V2 — Script Generator
Takes market data and generates a narrated video script with timed segments.
"""

import json
import os
import sys
import subprocess

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"


def generate_script(market_data, style="savvy_finance"):
    """Generate a 2-3 minute narration script from market data."""

    prompt = f"""You are a professional finance YouTube scriptwriter. Write a 2-3 minute narration script 
for a daily market recap video in the style of "Savvy Finance" — authoritative, clear, analytical, 
with dramatic pauses and emphasis points.

MARKET DATA:
{json.dumps(market_data, indent=2)}

RULES:
1. Open with a dramatic hook line (1-2 sentences that grab attention)
2. Cover: crypto (BTC, ETH, SOL), major indices (S&P 500, Nasdaq, Dow), key commodities (Gold, Oil), and any notable forex moves
3. Include brief macro analysis — connect the dots between moves
4. End with a forward-looking statement
5. Use natural speech patterns — contractions, rhetorical questions, emphasis words
6. Include [PAUSE] markers for dramatic pauses
7. Mark emphasis with *word* for kinetic typography cues
8. Keep total word count between 350-500 words (about 2-3 minutes spoken)

OUTPUT FORMAT — Return valid JSON:
{{
  "hook": "Opening dramatic line",
  "segments": [
    {{
      "id": "hook",
      "text": "The narration text for this segment",
      "overlay_text": "SHORT BOLD TEXT FOR SCREEN",
      "duration_hint": 8,
      "visual_cue": "description of what should be on screen"
    }},
    {{
      "id": "crypto",
      "text": "...",
      "overlay_text": "CRYPTO MARKETS",
      "duration_hint": 25,
      "visual_cue": "..."
    }}
  ],
  "total_word_count": 400
}}

Segments should be: hook, crypto, indices, commodities_forex, analysis, outlook
"""

    # Use Anthropic API directly
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # Try to read from config
        config_paths = [
            os.path.expanduser("~/.openclaw/config.yaml"),
            os.path.expanduser("~/.anthropic/api_key"),
        ]
        for p in config_paths:
            if os.path.exists(p):
                with open(p) as f:
                    content = f.read()
                    if "ANTHROPIC_API_KEY" in content or "sk-ant-" in content:
                        for line in content.split("\n"):
                            if "sk-ant-" in line:
                                api_key = line.strip().split(":")[-1].strip().strip('"').strip("'")
                                break

    result = subprocess.run([
        "curl", "-s", "https://api.anthropic.com/v1/messages",
        "-H", f"x-api-key: {api_key}",
        "-H", "anthropic-version: 2023-06-01",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": ANTHROPIC_MODEL,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        })
    ], capture_output=True, text=True, timeout=60)

    response = json.loads(result.stdout)
    text = response["content"][0]["text"]

    # Extract JSON from response
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Market data JSON file")
    parser.add_argument("--output", default="/tmp/finance-script.json")
    args = parser.parse_args()

    with open(args.data) as f:
        data = json.load(f)

    script = generate_script(data)
    with open(args.output, "w") as f:
        json.dump(script, f, indent=2)

    print(f"Script generated: {args.output}")
    print(f"Segments: {len(script['segments'])}")
    print(f"Words: {script.get('total_word_count', 'N/A')}")
