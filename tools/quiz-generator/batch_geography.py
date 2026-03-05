#!/usr/bin/env python3
"""
Batch Geography Quiz Generator — creates multiple quiz videos at once.
Run from the quiz-video-generator directory on r2d2.

Usage:
    python3 batch_geography.py                    # Generate all preset quizzes
    python3 batch_geography.py --quiz easy        # Just easy quizzes
    python3 batch_geography.py --format shorts    # 9:16 format only
    python3 batch_geography.py --count 3          # First N quizzes only
"""

import requests
import argparse
import json
import time

API_BASE = "http://localhost:5000"

# Curated quiz sets for the geography channel
QUIZ_PRESETS = {
    "easy": [
        {
            "name": "Can You Name These Famous Countries?",
            "countries": [
                {"country_name": "United States of America", "country_code": "USA"},
                {"country_name": "Brazil", "country_code": "BRA"},
                {"country_name": "Australia", "country_code": "AUS"},
                {"country_name": "India", "country_code": "IND"},
                {"country_name": "Russia", "country_code": "RUS"},
                {"country_name": "China", "country_code": "CHN"},
                {"country_name": "Japan", "country_code": "JPN"},
                {"country_name": "United Kingdom", "country_code": "GBR"},
                {"country_name": "Italy", "country_code": "ITA"},
                {"country_name": "Mexico", "country_code": "MEX"},
            ]
        },
        {
            "name": "European Countries You Should Know",
            "countries": [
                {"country_name": "France", "country_code": "FRA"},
                {"country_name": "Germany", "country_code": "DEU"},
                {"country_name": "Spain", "country_code": "ESP"},
                {"country_name": "Portugal", "country_code": "PRT"},
                {"country_name": "Greece", "country_code": "GRC"},
                {"country_name": "Norway", "country_code": "NOR"},
                {"country_name": "Poland", "country_code": "POL"},
                {"country_name": "Turkey", "country_code": "TUR"},
                {"country_name": "Ireland", "country_code": "IRL"},
                {"country_name": "Switzerland", "country_code": "CHE"},
            ]
        },
    ],
    "medium": [
        {
            "name": "African Countries Challenge",
            "countries": [
                {"country_name": "South Africa", "country_code": "ZAF"},
                {"country_name": "Egypt", "country_code": "EGY"},
                {"country_name": "Nigeria", "country_code": "NGA"},
                {"country_name": "Kenya", "country_code": "KEN"},
                {"country_name": "Morocco", "country_code": "MAR"},
                {"country_name": "Ethiopia", "country_code": "ETH"},
                {"country_name": "Tanzania", "country_code": "TZA"},
                {"country_name": "Ghana", "country_code": "GHA"},
                {"country_name": "Algeria", "country_code": "DZA"},
                {"country_name": "Madagascar", "country_code": "MDG"},
            ]
        },
        {
            "name": "Asian Countries You Must Know",
            "countries": [
                {"country_name": "Thailand", "country_code": "THA"},
                {"country_name": "Vietnam", "country_code": "VNM"},
                {"country_name": "Indonesia", "country_code": "IDN"},
                {"country_name": "Philippines", "country_code": "PHL"},
                {"country_name": "South Korea", "country_code": "KOR"},
                {"country_name": "Pakistan", "country_code": "PAK"},
                {"country_name": "Myanmar", "country_code": "MMR"},
                {"country_name": "Malaysia", "country_code": "MYS"},
                {"country_name": "Mongolia", "country_code": "MNG"},
                {"country_name": "Nepal", "country_code": "NPL"},
            ]
        },
        {
            "name": "South American Geography",
            "countries": [
                {"country_name": "Argentina", "country_code": "ARG"},
                {"country_name": "Chile", "country_code": "CHL"},
                {"country_name": "Colombia", "country_code": "COL"},
                {"country_name": "Peru", "country_code": "PER"},
                {"country_name": "Venezuela", "country_code": "VEN"},
                {"country_name": "Ecuador", "country_code": "ECU"},
                {"country_name": "Bolivia", "country_code": "BOL"},
                {"country_name": "Paraguay", "country_code": "PRY"},
                {"country_name": "Uruguay", "country_code": "URY"},
                {"country_name": "Guyana", "country_code": "GUY"},
            ]
        },
    ],
    "hard": [
        {
            "name": "Can You Name These Tricky Countries?",
            "countries": [
                {"country_name": "Tajikistan", "country_code": "TJK"},
                {"country_name": "Burkina Faso", "country_code": "BFA"},
                {"country_name": "Laos", "country_code": "LAO"},
                {"country_name": "Slovenia", "country_code": "SVN"},
                {"country_name": "Eritrea", "country_code": "ERI"},
                {"country_name": "Moldova", "country_code": "MDA"},
                {"country_name": "Benin", "country_code": "BEN"},
                {"country_name": "Kyrgyzstan", "country_code": "KGZ"},
                {"country_name": "Gabon", "country_code": "GAB"},
                {"country_name": "Honduras", "country_code": "HND"},
            ]
        },
        {
            "name": "Only Geography Experts Get 10/10",
            "countries": [
                {"country_name": "Suriname", "country_code": "SUR"},
                {"country_name": "Brunei", "country_code": "BRN"},
                {"country_name": "Lesotho", "country_code": "LSO"},
                {"country_name": "Djibouti", "country_code": "DJI"},
                {"country_name": "Bhutan", "country_code": "BTN"},
                {"country_name": "Togo", "country_code": "TGO"},
                {"country_name": "Guinea-Bissau", "country_code": "GNB"},
                {"country_name": "Malawi", "country_code": "MWI"},
                {"country_name": "Turkmenistan", "country_code": "TKM"},
                {"country_name": "Albania", "country_code": "ALB"},
            ]
        },
    ],
}

# Profile IDs
PROFILES = {
    "youtube": 1,      # 16:9
    "tiktok": 2,       # 9:16
    "shorts": 3,       # 9:16
    "reels": 4,        # 9:16
}


def create_quiz(name, countries):
    """Create a quiz via API."""
    r = requests.post(f"{API_BASE}/api/quizzes/geography-from-json",
                      json={"name": name, "countries": countries},
                      headers={"Content-Type": "application/json"})
    r.raise_for_status()
    return r.json()["quiz_id"]


def generate_video(quiz_id, profile_id):
    """Generate video for quiz with given profile."""
    r = requests.post(f"{API_BASE}/api/generate/{quiz_id}/profile/{profile_id}",
                      json={},
                      headers={"Content-Type": "application/json"},
                      timeout=600)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Batch Geography Quiz Generator")
    parser.add_argument("--quiz", choices=["easy", "medium", "hard", "all"], default="all")
    parser.add_argument("--format", choices=["youtube", "shorts", "tiktok", "reels", "all"], default="all")
    parser.add_argument("--count", type=int, help="Max quizzes to generate")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Select quizzes
    if args.quiz == "all":
        quizzes = []
        for diff_quizzes in QUIZ_PRESETS.values():
            quizzes.extend(diff_quizzes)
    else:
        quizzes = QUIZ_PRESETS[args.quiz]

    if args.count:
        quizzes = quizzes[:args.count]

    # Select profiles
    if args.format == "all":
        profile_ids = [1, 3]  # YouTube + Shorts
    else:
        profile_ids = [PROFILES[args.format]]

    print(f"📊 Batch Generator: {len(quizzes)} quizzes × {len(profile_ids)} formats = {len(quizzes) * len(profile_ids)} videos")
    print("=" * 60)

    results = []
    for i, quiz_data in enumerate(quizzes):
        name = quiz_data["name"]
        countries = quiz_data["countries"]
        print(f"\n[{i+1}/{len(quizzes)}] {name} ({len(countries)} countries)")

        if args.dry_run:
            print(f"  → Would create quiz and generate {len(profile_ids)} videos")
            continue

        quiz_id = create_quiz(name, countries)
        print(f"  → Quiz created: #{quiz_id}")

        for pid in profile_ids:
            profile_name = [k for k, v in PROFILES.items() if v == pid][0]
            print(f"  → Generating {profile_name} video...")
            try:
                result = generate_video(quiz_id, pid)
                for v in result.get("videos", []):
                    print(f"    ✅ {v['filename']} ({v['duration']:.0f}s, {v['file_size']/1024:.0f}KB)")
                    results.append(v)
            except Exception as e:
                print(f"    ❌ Failed: {e}")

        time.sleep(2)  # Brief pause between quizzes

    print(f"\n{'=' * 60}")
    print(f"✅ Generated {len(results)} videos total")
    for v in results:
        print(f"  • {v['filename']}")


if __name__ == "__main__":
    main()
