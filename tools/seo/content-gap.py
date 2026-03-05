#!/usr/bin/env python3
"""
Content Gap Analysis — finds keywords we should cover but haven't.
Compares keyword research against existing Ghost articles.
Works with RSS cache when r2d2 is down.
"""

import json
import re
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
KEYWORD_FILE = SCRIPT_DIR / "keyword-report.json"
NEWS_CACHE = Path(__file__).parent.parent / "news-aggregator" / "cache.json"
OUTPUT_FILE = SCRIPT_DIR / "content-gaps.md"

# High-value evergreen topics for expat audience
EVERGREEN_TOPICS = {
    "golden visa": {"priority": "high", "category": "immigration", "refresh": "monthly"},
    "d7 visa": {"priority": "high", "category": "immigration", "refresh": "monthly"},
    "nhr tax": {"priority": "high", "category": "tax", "refresh": "quarterly"},
    "cost of living": {"priority": "high", "category": "lifestyle", "refresh": "quarterly"},
    "healthcare": {"priority": "high", "category": "lifestyle", "refresh": "semi-annual"},
    "real estate": {"priority": "high", "category": "property", "refresh": "monthly"},
    "housing market": {"priority": "high", "category": "property", "refresh": "monthly"},
    "digital nomad": {"priority": "medium", "category": "immigration", "refresh": "quarterly"},
    "education": {"priority": "medium", "category": "lifestyle", "refresh": "semi-annual"},
    "portugal vs spain": {"priority": "medium", "category": "comparison", "refresh": "quarterly"},
    "lisbon neighborhoods": {"priority": "medium", "category": "guides", "refresh": "semi-annual"},
    "porto neighborhoods": {"priority": "medium", "category": "guides", "refresh": "semi-annual"},
    "algarve guide": {"priority": "medium", "category": "guides", "refresh": "semi-annual"},
    "portugal taxes": {"priority": "high", "category": "tax", "refresh": "annual"},
    "retiring in portugal": {"priority": "high", "category": "lifestyle", "refresh": "quarterly"},
    "buying property": {"priority": "high", "category": "property", "refresh": "quarterly"},
    "bank account": {"priority": "medium", "category": "guides", "refresh": "annual"},
    "residency permit": {"priority": "high", "category": "immigration", "refresh": "quarterly"},
    "portugal salary": {"priority": "medium", "category": "economy", "refresh": "quarterly"},
    "portugal minimum wage": {"priority": "medium", "category": "economy", "refresh": "annual"},
}


def load_keywords():
    if not KEYWORD_FILE.exists():
        print("Run keyword-research.py first")
        return {}
    with open(KEYWORD_FILE) as f:
        return json.load(f)


def load_existing_titles():
    """Load existing article titles from RSS cache."""
    titles = []
    if NEWS_CACHE.exists():
        with open(NEWS_CACHE) as f:
            cache = json.load(f)
        titles.extend(item["title"] for item in cache.get("items", []))
    return titles


def analyze_gaps():
    keywords = load_keywords()
    existing = load_existing_titles()
    existing_text = " ".join(existing).lower()
    
    all_kws = set()
    for seed_kws in keywords.get("by_seed", {}).values():
        for item in seed_kws:
            all_kws.add(item["keyword"])
    
    # Check evergreen topics
    gaps = []
    covered = []
    
    for topic, meta in EVERGREEN_TOPICS.items():
        topic_words = topic.lower().split()
        is_covered = all(w in existing_text for w in topic_words)
        
        if is_covered:
            covered.append(topic)
        else:
            gaps.append({
                "topic": topic,
                "priority": meta["priority"],
                "category": meta["category"],
                "refresh": meta["refresh"],
                "related_keywords": [kw for kw in all_kws if topic.split()[0] in kw.lower()],
            })
    
    # Sort gaps by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    gaps.sort(key=lambda x: priority_order.get(x["priority"], 2))
    
    # Generate report
    report = [f"# Content Gap Analysis — {datetime.now().strftime('%Y-%m-%d')}\n"]
    report.append(f"**Analyzed:** {len(all_kws)} keywords, {len(existing)} existing articles\n")
    
    report.append(f"\n## 🔴 Content Gaps ({len(gaps)} topics not covered)\n")
    for gap in gaps:
        report.append(f"### {gap['topic'].title()} [{gap['priority'].upper()}]")
        report.append(f"- Category: {gap['category']}")
        report.append(f"- Suggested refresh: {gap['refresh']}")
        if gap['related_keywords']:
            report.append(f"- Target keywords: {', '.join(gap['related_keywords'][:5])}")
        report.append("")
    
    report.append(f"\n## ✅ Already Covered ({len(covered)} topics)\n")
    for topic in covered:
        report.append(f"- {topic.title()}")
    
    report.append(f"\n## 📊 Keyword Intent Distribution\n")
    for intent, kws in sorted(keywords.get("by_intent", {}).items()):
        report.append(f"- **{intent}:** {len(kws)} keywords")
    
    report.append(f"\n## 💡 Article Ideas\n")
    # Generate article ideas from gaps
    ideas = []
    for gap in gaps[:10]:
        if gap["category"] == "immigration":
            ideas.append(f"Complete Guide to {gap['topic'].title()} in Portugal ({datetime.now().year})")
        elif gap["category"] == "property":
            ideas.append(f"Portugal {gap['topic'].title()}: What Expats Need to Know in {datetime.now().year}")
        elif gap["category"] == "tax":
            ideas.append(f"Understanding {gap['topic'].title()} in Portugal: A Practical Guide")
        elif gap["category"] == "comparison":
            ideas.append(f"Living in {gap['topic'].title()}: An Honest Comparison")
        else:
            ideas.append(f"{gap['topic'].title()} in Portugal: Everything You Need to Know")
    
    for i, idea in enumerate(ideas, 1):
        report.append(f"{i}. {idea}")
    
    output = "\n".join(report)
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    
    print(output)
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    analyze_gaps()
