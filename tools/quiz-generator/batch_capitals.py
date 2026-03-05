#!/usr/bin/env python3
"""
Batch Capital Cities Quiz Generator.
Run from the quiz-video-generator directory on r2d2.

Usage:
    python3 batch_capitals.py                    # Generate all
    python3 batch_capitals.py --quiz easy        # Just easy
    python3 batch_capitals.py --format shorts    # 9:16 only
    python3 batch_capitals.py --dry-run          # Preview
"""

import sys
import os
import argparse
import time

# Add parent dir so we can import the generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.capital_city_generator import CapitalCityGenerator, CAPITALS_DB

QUIZ_PRESETS = {
    "easy": [
        {
            "name": "Guess The Capital - Easy",
            "countries": [
                {"country_name": "France", "country_code": "FRA", "capital": "Paris"},
                {"country_name": "Japan", "country_code": "JPN", "capital": "Tokyo"},
                {"country_name": "Brazil", "country_code": "BRA", "capital": "Brasília"},
                {"country_name": "Australia", "country_code": "AUS", "capital": "Canberra"},
                {"country_name": "Egypt", "country_code": "EGY", "capital": "Cairo"},
                {"country_name": "Mexico", "country_code": "MEX", "capital": "Mexico City"},
                {"country_name": "Germany", "country_code": "DEU", "capital": "Berlin"},
                {"country_name": "India", "country_code": "IND", "capital": "New Delhi"},
                {"country_name": "Russia", "country_code": "RUS", "capital": "Moscow"},
                {"country_name": "Canada", "country_code": "CAN", "capital": "Ottawa"},
            ]
        },
        {
            "name": "European Capitals Quiz",
            "countries": [
                {"country_name": "Spain", "country_code": "ESP", "capital": "Madrid"},
                {"country_name": "Portugal", "country_code": "PRT", "capital": "Lisbon"},
                {"country_name": "Italy", "country_code": "ITA", "capital": "Rome"},
                {"country_name": "Greece", "country_code": "GRC", "capital": "Athens"},
                {"country_name": "Poland", "country_code": "POL", "capital": "Warsaw"},
                {"country_name": "Norway", "country_code": "NOR", "capital": "Oslo"},
                {"country_name": "Czech Republic", "country_code": "CZE", "capital": "Prague"},
                {"country_name": "Austria", "country_code": "AUT", "capital": "Vienna"},
                {"country_name": "Sweden", "country_code": "SWE", "capital": "Stockholm"},
                {"country_name": "Ireland", "country_code": "IRL", "capital": "Dublin"},
            ]
        },
    ],
    "medium": [
        {
            "name": "African Capitals Challenge",
            "countries": [
                {"country_name": "South Africa", "country_code": "ZAF", "capital": "Pretoria"},
                {"country_name": "Nigeria", "country_code": "NGA", "capital": "Abuja"},
                {"country_name": "Kenya", "country_code": "KEN", "capital": "Nairobi"},
                {"country_name": "Morocco", "country_code": "MAR", "capital": "Rabat"},
                {"country_name": "Ethiopia", "country_code": "ETH", "capital": "Addis Ababa"},
                {"country_name": "Tanzania", "country_code": "TZA", "capital": "Dodoma"},
                {"country_name": "Ghana", "country_code": "GHA", "capital": "Accra"},
                {"country_name": "Algeria", "country_code": "DZA", "capital": "Algiers"},
                {"country_name": "Senegal", "country_code": "SEN", "capital": "Dakar"},
                {"country_name": "Madagascar", "country_code": "MDG", "capital": "Antananarivo"},
            ]
        },
        {
            "name": "Asian Capitals You Should Know",
            "countries": [
                {"country_name": "Thailand", "country_code": "THA", "capital": "Bangkok"},
                {"country_name": "Vietnam", "country_code": "VNM", "capital": "Hanoi"},
                {"country_name": "Indonesia", "country_code": "IDN", "capital": "Jakarta"},
                {"country_name": "South Korea", "country_code": "KOR", "capital": "Seoul"},
                {"country_name": "Pakistan", "country_code": "PAK", "capital": "Islamabad"},
                {"country_name": "Philippines", "country_code": "PHL", "capital": "Manila"},
                {"country_name": "Malaysia", "country_code": "MYS", "capital": "Kuala Lumpur"},
                {"country_name": "Mongolia", "country_code": "MNG", "capital": "Ulaanbaatar"},
                {"country_name": "Nepal", "country_code": "NPL", "capital": "Kathmandu"},
                {"country_name": "Cambodia", "country_code": "KHM", "capital": "Phnom Penh"},
            ]
        },
        {
            "name": "Americas Capitals Quiz",
            "countries": [
                {"country_name": "Argentina", "country_code": "ARG", "capital": "Buenos Aires"},
                {"country_name": "Colombia", "country_code": "COL", "capital": "Bogotá"},
                {"country_name": "Peru", "country_code": "PER", "capital": "Lima"},
                {"country_name": "Chile", "country_code": "CHL", "capital": "Santiago"},
                {"country_name": "Cuba", "country_code": "CUB", "capital": "Havana"},
                {"country_name": "Venezuela", "country_code": "VEN", "capital": "Caracas"},
                {"country_name": "Ecuador", "country_code": "ECU", "capital": "Quito"},
                {"country_name": "Guatemala", "country_code": "GTM", "capital": "Guatemala City"},
                {"country_name": "Uruguay", "country_code": "URY", "capital": "Montevideo"},
                {"country_name": "Panama", "country_code": "PAN", "capital": "Panama City"},
            ]
        },
    ],
    "hard": [
        {
            "name": "Tricky Capitals Most People Get Wrong",
            "countries": [
                {"country_name": "Turkey", "country_code": "TUR", "capital": "Ankara"},
                {"country_name": "Myanmar", "country_code": "MMR", "capital": "Naypyidaw"},
                {"country_name": "Australia", "country_code": "AUS", "capital": "Canberra"},
                {"country_name": "Brazil", "country_code": "BRA", "capital": "Brasília"},
                {"country_name": "South Africa", "country_code": "ZAF", "capital": "Pretoria"},
                {"country_name": "Switzerland", "country_code": "CHE", "capital": "Bern"},
                {"country_name": "Canada", "country_code": "CAN", "capital": "Ottawa"},
                {"country_name": "Nigeria", "country_code": "NGA", "capital": "Abuja"},
                {"country_name": "Ivory Coast", "country_code": "CIV", "capital": "Yamoussoukro"},
                {"country_name": "Kazakhstan", "country_code": "KAZ", "capital": "Astana"},
            ]
        },
        {
            "name": "Only Experts Know These Capitals",
            "countries": [
                {"country_name": "Burkina Faso", "country_code": "BFA", "capital": "Ouagadougou"},
                {"country_name": "Tajikistan", "country_code": "TJK", "capital": "Dushanbe"},
                {"country_name": "Bhutan", "country_code": "BTN", "capital": "Thimphu"},
                {"country_name": "Moldova", "country_code": "MDA", "capital": "Chișinău"},
                {"country_name": "Eritrea", "country_code": "ERI", "capital": "Asmara"},
                {"country_name": "Laos", "country_code": "LAO", "capital": "Vientiane"},
                {"country_name": "Malawi", "country_code": "MWI", "capital": "Lilongwe"},
                {"country_name": "Suriname", "country_code": "SUR", "capital": "Paramaribo"},
                {"country_name": "Kyrgyzstan", "country_code": "KGZ", "capital": "Bishkek"},
                {"country_name": "Djibouti", "country_code": "DJI", "capital": "Djibouti"},
            ]
        },
    ],
}


def generate_directly(quiz_data, formats):
    """Generate video directly using CapitalCityGenerator (no API needed)."""
    results = []
    for fmt in formats:
        if fmt == 'youtube':
            vfmt, slug = '16:9', 'youtube'
        else:
            vfmt, slug = '9:16', 'youtube_shorts'

        profile = {
            'aspect_ratio': vfmt,
            'name': slug,
            'countdown_seconds': 8,
            'question_display_seconds': 1.0,
            'answer_display_seconds': 3.0,
        }

        gen = CapitalCityGenerator(profile=profile)
        quiz_slug = quiz_data["name"].lower().replace(' ', '_').replace("'", "").replace('"', '')[:35]
        output_filename = f"{quiz_slug}_{slug}.mp4"

        questions = quiz_data["countries"]
        video_path, duration = gen.generate_video(
            questions, quiz_data["name"], output_filename,
            countdown_seconds=8, answer_display_seconds=3.0,
        )
        file_size = os.path.getsize(video_path)
        print(f"    ✅ {output_filename} ({duration:.0f}s, {file_size/1024:.0f}KB)")
        results.append({
            'filename': output_filename,
            'duration': duration,
            'file_size': file_size,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Batch Capital Cities Quiz Generator")
    parser.add_argument("--quiz", choices=["easy", "medium", "hard", "all"], default="all")
    parser.add_argument("--format", choices=["youtube", "shorts", "all"], default="all")
    parser.add_argument("--count", type=int, help="Max quizzes to generate")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.quiz == "all":
        quizzes = []
        for diff_quizzes in QUIZ_PRESETS.values():
            quizzes.extend(diff_quizzes)
    else:
        quizzes = QUIZ_PRESETS[args.quiz]

    if args.count:
        quizzes = quizzes[:args.count]

    formats = ['youtube', 'shorts'] if args.format == 'all' else [args.format]

    print(f"🏛️  Capital Cities Batch: {len(quizzes)} quizzes × {len(formats)} formats = {len(quizzes) * len(formats)} videos")
    print("=" * 60)

    all_results = []
    for i, quiz_data in enumerate(quizzes):
        name = quiz_data["name"]
        print(f"\n[{i+1}/{len(quizzes)}] {name} ({len(quiz_data['countries'])} countries)")

        if args.dry_run:
            for c in quiz_data["countries"]:
                print(f"  • {c['country_name']} → {c['capital']}")
            continue

        results = generate_directly(quiz_data, formats)
        all_results.extend(results)
        time.sleep(1)

    print(f"\n{'=' * 60}")
    print(f"✅ Generated {len(all_results)} capital city quiz videos")
    for r in all_results:
        print(f"  • {r['filename']}")


if __name__ == "__main__":
    main()
