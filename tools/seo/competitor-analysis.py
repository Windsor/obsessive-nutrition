#!/usr/bin/env python3
"""
Competitor Content Analyzer for The Portugal Brief.
Analyzes competitor newsletters/sites to identify content gaps and opportunities.
"""

import json
import re
import xml.etree.ElementTree as ET
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_FILE = SCRIPT_DIR / "competitor-report.json"

COMPETITORS = [
    {
        "name": "Portugal Resident",
        "url": "https://www.portugalresident.com",
        "feed": "https://www.portugalresident.com/feed/",
        "type": "news",
    },
    {
        "name": "The Portugal News",
        "url": "https://www.theportugalnews.com",
        "feed": "https://www.theportugalnews.com/rss",
        "type": "news",
    },
    {
        "name": "Get Golden Visa",
        "url": "https://getgoldenvisa.com",
        "feed": None,
        "type": "guide",
        "pages": [
            "https://getgoldenvisa.com/portugal-golden-visa-program",
            "https://getgoldenvisa.com/portugal-d7-visa",
            "https://getgoldenvisa.com/portugal-digital-nomad-visa",
        ],
    },
]

# Topics we want to cover well
TARGET_TOPICS = [
    "golden visa", "d7 visa", "digital nomad visa", "nhr tax", "residency",
    "cost of living", "property", "real estate", "healthcare", "education",
    "citizenship", "retirement", "banking", "housing", "rent",
    "lisbon", "porto", "algarve", "braga", "madeira",
    "economy", "inflation", "minimum wage", "tax",
    "immigration", "aima", "sef", "passport",
]


def fetch_feed(url, timeout=15):
    """Fetch RSS feed and extract article titles and categories."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "ThePortugalBrief/1.0 (competitor analysis)"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml_data = resp.read().decode("utf-8", errors="replace")
        
        root = ET.fromstring(xml_data)
        articles = []
        
        for item in root.iter("item"):
            title_el = item.find("title")
            categories = [c.text for c in item.findall("category") if c.text]
            title = title_el.text if title_el is not None and title_el.text else ""
            
            articles.append({
                "title": title,
                "categories": categories,
            })
        
        return articles
    except Exception as e:
        print(f"  ⚠️ Error fetching {url}: {e}")
        return []


def analyze_topics(articles):
    """Analyze topic distribution in articles."""
    topic_counts = Counter()
    
    for article in articles:
        text = article["title"].lower()
        for cat in article.get("categories", []):
            text += " " + cat.lower()
        
        for topic in TARGET_TOPICS:
            if topic in text:
                topic_counts[topic] += 1
    
    return dict(topic_counts.most_common())


def find_gaps(our_topics, competitor_topics):
    """Find topics competitors cover that we don't (or cover less)."""
    gaps = []
    for topic, count in competitor_topics.items():
        our_count = our_topics.get(topic, 0)
        if count > our_count:
            gaps.append({
                "topic": topic,
                "competitor_count": count,
                "our_count": our_count,
                "gap": count - our_count,
            })
    
    gaps.sort(key=lambda x: x["gap"], reverse=True)
    return gaps


def main():
    print(f"=== Competitor Analysis — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    all_competitor_topics = Counter()
    results = {}
    
    for comp in COMPETITORS:
        print(f"Analyzing: {comp['name']}...")
        
        if comp.get("feed"):
            articles = fetch_feed(comp["feed"])
            print(f"  → {len(articles)} articles from feed")
            
            topics = analyze_topics(articles)
            print(f"  → Topics found: {len(topics)}")
            
            for topic, count in topics.items():
                all_competitor_topics[topic] += count
            
            results[comp["name"]] = {
                "article_count": len(articles),
                "topics": topics,
                "top_categories": Counter(
                    cat for a in articles for cat in a.get("categories", [])
                ).most_common(15),
            }
        else:
            results[comp["name"]] = {"type": comp["type"], "note": "No RSS feed, manual analysis needed"}
    
    # Print summary
    print(f"\n{'='*60}")
    print("COMPETITOR TOPIC COVERAGE (from RSS feeds)")
    print(f"{'='*60}\n")
    
    for topic, count in all_competitor_topics.most_common(20):
        bar = "█" * min(count, 40)
        print(f"  {topic:20s} {count:3d} {bar}")
    
    # Category analysis
    print(f"\n{'='*60}")
    print("TOP CATEGORIES BY COMPETITOR")
    print(f"{'='*60}\n")
    
    for name, data in results.items():
        if "top_categories" in data:
            print(f"\n{name}:")
            for cat, count in data["top_categories"][:10]:
                print(f"  {count:3d} — {cat}")
    
    # Save report
    report = {
        "generated": datetime.now().isoformat(),
        "competitors": results,
        "combined_topics": dict(all_competitor_topics.most_common()),
    }
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
