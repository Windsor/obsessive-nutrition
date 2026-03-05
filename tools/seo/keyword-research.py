#!/usr/bin/env python3
"""
SEO Keyword Research Tool for The Portugal Brief
Analyzes Google autocomplete suggestions and related searches
to find content opportunities for Portugal-focused articles.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
OUTPUT_FILE = OUTPUT_DIR / "keyword-report.json"

# Seed keywords — topics we cover
SEED_KEYWORDS = [
    "portugal expat",
    "living in portugal",
    "portugal news",
    "portugal real estate",
    "portugal golden visa",
    "portugal d7 visa",
    "portugal nhr tax",
    "portugal housing market",
    "portugal economy",
    "moving to portugal",
    "portugal cost of living",
    "portugal digital nomad",
    "retire in portugal",
    "portugal vs spain",
    "portugal property",
    "lisbon expat",
    "algarve expat",
    "porto expat",
    "portugal healthcare",
    "portugal education",
]


def google_autocomplete(query, lang="en", country="pt"):
    """Fetch Google autocomplete suggestions."""
    try:
        params = urllib.parse.urlencode({
            "q": query,
            "client": "firefox",
            "hl": lang,
            "gl": country,
        })
        url = f"https://suggestqueries.google.com/complete/search?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data[1] if len(data) > 1 else []
    except Exception as e:
        return []


def expand_keyword(seed):
    """Expand a seed keyword with alphabet modifiers."""
    suggestions = set()
    
    # Direct autocomplete
    for s in google_autocomplete(seed):
        suggestions.add(s)
    
    # Alphabet expansion (seed + a, seed + b, etc.)
    for letter in "abcdefghijklmnopqrstuvwxyz":
        for s in google_autocomplete(f"{seed} {letter}"):
            suggestions.add(s)
    
    return sorted(suggestions)


def categorize_intent(keyword):
    """Categorize search intent."""
    kw = keyword.lower()
    if any(w in kw for w in ["how to", "guide", "what is", "tips", "best way"]):
        return "informational"
    if any(w in kw for w in ["buy", "cost", "price", "cheap", "agency", "company"]):
        return "transactional"
    if any(w in kw for w in ["vs", "compare", "review", "pros cons", "worth"]):
        return "comparison"
    if any(w in kw for w in ["news", "update", "latest", "2026", "2025"]):
        return "news"
    return "informational"


def run_research(seeds=None, expand=False):
    """Run keyword research on seed keywords."""
    seeds = seeds or SEED_KEYWORDS[:10]  # Limit to avoid rate limiting
    
    print(f"=== SEO Keyword Research — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    results = {}
    all_keywords = set()
    
    for seed in seeds:
        print(f"Researching: {seed}")
        suggestions = google_autocomplete(seed)
        
        if expand:
            # Full alphabet expansion (slower, more thorough)
            suggestions = expand_keyword(seed)
        
        categorized = []
        for s in suggestions:
            intent = categorize_intent(s)
            categorized.append({"keyword": s, "intent": intent})
            all_keywords.add(s)
        
        results[seed] = categorized
        print(f"  → {len(categorized)} suggestions")
    
    # Group by intent
    intent_groups = {}
    for kw in all_keywords:
        intent = categorize_intent(kw)
        intent_groups.setdefault(intent, []).append(kw)
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_keywords": len(all_keywords),
        "by_seed": results,
        "by_intent": {k: sorted(v) for k, v in intent_groups.items()},
        "content_opportunities": _find_opportunities(all_keywords),
    }
    
    # Save report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Total unique keywords: {len(all_keywords)}")
    for intent, kws in sorted(intent_groups.items()):
        print(f"  {intent}: {len(kws)}")
    
    print(f"\n📝 Content Opportunities:")
    for opp in report["content_opportunities"][:15]:
        print(f"  • {opp}")
    
    print(f"\nFull report saved to {OUTPUT_FILE}")
    return report


def _find_opportunities(keywords):
    """Identify high-value content opportunities from keywords."""
    opportunities = []
    
    # Question-based keywords (great for articles)
    questions = [kw for kw in keywords if any(
        kw.lower().startswith(w) for w in ["how", "what", "why", "when", "where", "can", "do", "is"]
    )]
    opportunities.extend(sorted(questions)[:10])
    
    # Comparison keywords (great for guides)
    comparisons = [kw for kw in keywords if "vs" in kw.lower() or "compare" in kw.lower()]
    opportunities.extend(sorted(comparisons)[:5])
    
    # Cost/price keywords (great for practical guides)
    cost_kws = [kw for kw in keywords if any(w in kw.lower() for w in ["cost", "price", "cheap", "expensive", "budget"])]
    opportunities.extend(sorted(cost_kws)[:5])
    
    return list(dict.fromkeys(opportunities))  # Deduplicate while preserving order


if __name__ == "__main__":
    import sys
    expand = "--expand" in sys.argv
    run_research(expand=expand)
