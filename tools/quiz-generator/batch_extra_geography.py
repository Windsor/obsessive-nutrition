#!/usr/bin/env python3
"""
Extra Geography Quiz Batches — additional quiz sets for the channel.
Run from r2d2: python3 batch_extra_geography.py [--quiz CATEGORY] [--format FORMAT]
"""

import requests
import argparse
import json
import time

API_BASE = "http://localhost:5000"

PROFILES = {
    "youtube": 1,
    "tiktok": 2,
    "shorts": 3,
    "reels": 4,
}

QUIZ_PRESETS = {
    "island_nations": [
        {
            "name": "Can You Name These Island Nations",
            "countries": [
                {"country_name": "Madagascar", "country_code": "MDG"},
                {"country_name": "New Zealand", "country_code": "NZL"},
                {"country_name": "Cuba", "country_code": "CUB"},
                {"country_name": "Sri Lanka", "country_code": "LKA"},
                {"country_name": "Iceland", "country_code": "ISL"},
                {"country_name": "Papua New Guinea", "country_code": "PNG"},
                {"country_name": "Jamaica", "country_code": "JAM"},
                {"country_name": "Cyprus", "country_code": "CYP"},
                {"country_name": "Fiji", "country_code": "FJI"},
                {"country_name": "Trinidad and Tobago", "country_code": "TTO"},
            ]
        },
    ],
    "middle_east": [
        {
            "name": "Middle East Geography Challenge",
            "countries": [
                {"country_name": "Saudi Arabia", "country_code": "SAU"},
                {"country_name": "Iran", "country_code": "IRN"},
                {"country_name": "Iraq", "country_code": "IRQ"},
                {"country_name": "Israel", "country_code": "ISR"},
                {"country_name": "Jordan", "country_code": "JOR"},
                {"country_name": "Lebanon", "country_code": "LBN"},
                {"country_name": "Oman", "country_code": "OMN"},
                {"country_name": "Yemen", "country_code": "YEM"},
                {"country_name": "Syria", "country_code": "SYR"},
                {"country_name": "Kuwait", "country_code": "KWT"},
            ]
        },
    ],
    "central_america": [
        {
            "name": "Central America and Caribbean Quiz",
            "countries": [
                {"country_name": "Guatemala", "country_code": "GTM"},
                {"country_name": "Costa Rica", "country_code": "CRI"},
                {"country_name": "Panama", "country_code": "PAN"},
                {"country_name": "Honduras", "country_code": "HND"},
                {"country_name": "El Salvador", "country_code": "SLV"},
                {"country_name": "Nicaragua", "country_code": "NIC"},
                {"country_name": "Belize", "country_code": "BLZ"},
                {"country_name": "Haiti", "country_code": "HTI"},
                {"country_name": "Dominican Republic", "country_code": "DOM"},
                {"country_name": "Cuba", "country_code": "CUB"},
            ]
        },
    ],
    "stan_countries": [
        {
            "name": "Can You Name All The Stan Countries",
            "countries": [
                {"country_name": "Kazakhstan", "country_code": "KAZ"},
                {"country_name": "Uzbekistan", "country_code": "UZB"},
                {"country_name": "Turkmenistan", "country_code": "TKM"},
                {"country_name": "Kyrgyzstan", "country_code": "KGZ"},
                {"country_name": "Tajikistan", "country_code": "TJK"},
                {"country_name": "Afghanistan", "country_code": "AFG"},
                {"country_name": "Pakistan", "country_code": "PAK"},
            ]
        },
    ],
    "nordic_baltic": [
        {
            "name": "Nordic and Baltic Countries Quiz",
            "countries": [
                {"country_name": "Sweden", "country_code": "SWE"},
                {"country_name": "Finland", "country_code": "FIN"},
                {"country_name": "Denmark", "country_code": "DNK"},
                {"country_name": "Norway", "country_code": "NOR"},
                {"country_name": "Iceland", "country_code": "ISL"},
                {"country_name": "Estonia", "country_code": "EST"},
                {"country_name": "Latvia", "country_code": "LVA"},
                {"country_name": "Lithuania", "country_code": "LTU"},
            ]
        },
    ],
    "biggest_countries": [
        {
            "name": "Worlds 10 Biggest Countries By Area",
            "countries": [
                {"country_name": "Russia", "country_code": "RUS"},
                {"country_name": "Canada", "country_code": "CAN"},
                {"country_name": "United States of America", "country_code": "USA"},
                {"country_name": "China", "country_code": "CHN"},
                {"country_name": "Brazil", "country_code": "BRA"},
                {"country_name": "Australia", "country_code": "AUS"},
                {"country_name": "India", "country_code": "IND"},
                {"country_name": "Argentina", "country_code": "ARG"},
                {"country_name": "Kazakhstan", "country_code": "KAZ"},
                {"country_name": "Algeria", "country_code": "DZA"},
            ]
        },
    ],
    "smallest_countries": [
        {
            "name": "Can You Find These Tiny Countries",
            "countries": [
                {"country_name": "Luxembourg", "country_code": "LUX"},
                {"country_name": "Montenegro", "country_code": "MNE"},
                {"country_name": "North Macedonia", "country_code": "MKD"},
                {"country_name": "Slovenia", "country_code": "SVN"},
                {"country_name": "Eswatini", "country_code": "SWZ"},
                {"country_name": "Brunei", "country_code": "BRN"},
                {"country_name": "Djibouti", "country_code": "DJI"},
                {"country_name": "East Timor", "country_code": "TLS"},
                {"country_name": "Gambia", "country_code": "GMB"},
                {"country_name": "Lebanon", "country_code": "LBN"},
            ]
        },
    ],
}


def create_quiz(name, countries):
    r = requests.post(f"{API_BASE}/api/quizzes/geography-from-json",
                      json={"name": name, "countries": countries},
                      headers={"Content-Type": "application/json"})
    r.raise_for_status()
    return r.json()["quiz_id"]


def generate_video(quiz_id, profile_id):
    r = requests.post(f"{API_BASE}/api/generate/{quiz_id}",
                      json={"profile_id": profile_id},
                      headers={"Content-Type": "application/json"},
                      timeout=600)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Extra Geography Quiz Batches")
    categories = list(QUIZ_PRESETS.keys()) + ["all"]
    parser.add_argument("--quiz", choices=categories, default="all")
    parser.add_argument("--format", choices=["youtube", "shorts", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.quiz == "all":
        quizzes = []
        for cat_quizzes in QUIZ_PRESETS.values():
            quizzes.extend(cat_quizzes)
    else:
        quizzes = QUIZ_PRESETS[args.quiz]

    if args.format == "all":
        profile_ids = [1, 3]
    else:
        profile_ids = [PROFILES[args.format]]

    total = len(quizzes) * len(profile_ids)
    print(f"📊 Extra Batch: {len(quizzes)} quizzes × {len(profile_ids)} formats = {total} videos")
    print("=" * 60)

    for i, quiz_data in enumerate(quizzes):
        name = quiz_data["name"]
        countries = quiz_data["countries"]
        print(f"\n[{i+1}/{len(quizzes)}] {name} ({len(countries)} countries)")

        if args.dry_run:
            print(f"  🔵 DRY RUN — skipping")
            continue

        quiz_id = create_quiz(name, countries)
        print(f"  ✅ Created quiz #{quiz_id}")

        for pid in profile_ids:
            fmt = "YouTube" if pid == 1 else "Shorts"
            print(f"  🎬 Generating {fmt}...", flush=True)
            try:
                result = generate_video(quiz_id, pid)
                videos = result.get("videos", [])
                print(f"  ✅ {fmt}: {len(videos)} video(s)")
            except Exception as e:
                print(f"  ❌ {fmt} failed: {e}")

    print(f"\n{'='*60}")
    print("🏁 Batch complete!")


if __name__ == "__main__":
    main()
