#!/usr/bin/env python3
"""
Portugal News RSS Aggregator
Fetches English-language Portugal news from multiple RSS sources.
Works independently of r2d2 — can be used as backup data source for 
Samsung Frame dashboard, or as research tool for newsletter content.
"""

import json
import xml.etree.ElementTree as ET
import urllib.request
import re
from datetime import datetime, timedelta
from pathlib import Path
from html import unescape

SCRIPT_DIR = Path(__file__).parent
CACHE_FILE = SCRIPT_DIR / "cache.json"

# RSS feeds with English Portugal news
FEEDS = [
    # Tier 1 — Dedicated English Portugal news
    {
        "name": "Portugal Resident",
        "url": "https://www.portugalresident.com/feed/",
        "lang": "en",
        "priority": 1,
    },
    {
        "name": "The Portugal News",
        "url": "https://www.theportugalnews.com/rss",
        "lang": "en",
        "priority": 1,
    },
    {
        "name": "Expatica Portugal",
        "url": "https://www.expatica.com/pt/feed/",
        "lang": "en",
        "priority": 1,
        "optional": True,  # 500 errors sometimes
    },
    # Tier 2 — Regional / topical
    {
        "name": "Schengen Visa Info - Portugal",
        "url": "https://www.schengenvisainfo.com/news/tag/portugal/feed/",
        "lang": "en",
        "priority": 2,
        "optional": True,
    },
    {
        "name": "The Local - Portugal",
        "url": "https://feeds.thelocal.com/rss/pt",
        "lang": "en",
        "priority": 2,
        "optional": True,
    },
    # Tier 3 — Aggregated / broader
    {
        "name": "Google News - Portugal",
        "url": "https://news.google.com/rss/search?q=Portugal+when:1d&hl=en&gl=PT&ceid=PT:en",
        "lang": "en",
        "priority": 3,
    },
    {
        "name": "Google News - Portugal Expat",
        "url": "https://news.google.com/rss/search?q=Portugal+expat+OR+visa+OR+residency+when:7d&hl=en&gl=PT&ceid=PT:en",
        "lang": "en",
        "priority": 3,
    },
]

# Keywords that indicate Portugal relevance
PORTUGAL_KEYWORDS = [
    "portugal", "lisbon", "lisboa", "porto", "algarve", "braga", "faro",
    "madeira", "azores", "portuguese", "golden visa", "nhr", "d7 visa",
    "tap air", "benfica", "sporting", "galp", "edp", "energias",
]


def fetch_feed(feed_info, timeout=15):
    """Fetch and parse a single RSS feed."""
    try:
        req = urllib.request.Request(
            feed_info["url"],
            headers={"User-Agent": "ThePortugalBrief/1.0 (news aggregator)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml_data = resp.read().decode("utf-8", errors="replace")
        
        root = ET.fromstring(xml_data)
        items = []
        
        # Handle both RSS 2.0 and Atom
        for item in root.iter("item"):
            title = _get_text(item, "title")
            link = _get_text(item, "link")
            desc = _get_text(item, "description")
            pub_date = _get_text(item, "pubDate")
            
            if title and link:
                items.append({
                    "title": _clean_html(title),
                    "url": link.strip(),
                    "description": _clean_html(desc)[:300] if desc else "",
                    "published": pub_date or "",
                    "source": feed_info["name"],
                    "priority": feed_info["priority"],
                })
        
        # Atom entries
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
            title = _get_text(entry, "{http://www.w3.org/2005/Atom}title")
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.get("href", "") if link_el is not None else ""
            summary = _get_text(entry, "{http://www.w3.org/2005/Atom}summary")
            updated = _get_text(entry, "{http://www.w3.org/2005/Atom}updated")
            
            if title and link:
                items.append({
                    "title": _clean_html(title),
                    "url": link.strip(),
                    "description": _clean_html(summary)[:300] if summary else "",
                    "published": updated or "",
                    "source": feed_info["name"],
                    "priority": feed_info["priority"],
                })
        
        return items
    except Exception as e:
        print(f"  ⚠️ {feed_info['name']}: {e}")
        return []


def _get_text(element, tag):
    el = element.find(tag)
    return el.text if el is not None and el.text else None


def _clean_html(text):
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_portugal_relevant(item):
    """Check if an item is actually about Portugal."""
    text = f"{item['title']} {item['description']}".lower()
    return any(kw in text for kw in PORTUGAL_KEYWORDS)


def deduplicate(items):
    """Remove duplicate stories based on title similarity."""
    seen_titles = set()
    unique = []
    for item in items:
        # Normalize title for comparison
        norm = re.sub(r"[^a-z0-9]", "", item["title"].lower())[:50]
        if norm not in seen_titles:
            seen_titles.add(norm)
            unique.append(item)
    return unique


def aggregate(max_items=20, filter_relevant=True):
    """Fetch all feeds and return aggregated, deduplicated news."""
    all_items = []
    
    for feed in FEEDS:
        print(f"  Fetching {feed['name']}...")
        items = fetch_feed(feed)
        print(f"    → {len(items)} items")
        all_items.extend(items)
    
    if filter_relevant:
        # For Google News feeds, filter to Portugal-relevant only
        filtered = []
        for item in all_items:
            if item["source"].startswith("Google News"):
                if is_portugal_relevant(item):
                    filtered.append(item)
            else:
                filtered.append(item)
        all_items = filtered
    
    # Deduplicate
    all_items = deduplicate(all_items)
    
    # Sort: priority first, then by source diversity
    all_items.sort(key=lambda x: x["priority"])
    
    return all_items[:max_items]


def save_cache(items):
    """Cache results locally."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    cache = {
        "fetched_at": datetime.now().isoformat(),
        "count": len(items),
        "items": items,
    }
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"\nCached {len(items)} items to {CACHE_FILE}")


def load_cache():
    """Load cached results."""
    if not CACHE_FILE.exists():
        return None
    with open(CACHE_FILE) as f:
        return json.load(f)


def main():
    print(f"=== Portugal News Aggregator — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    items = aggregate()
    save_cache(items)
    
    print(f"\n{'='*60}")
    for i, item in enumerate(items, 1):
        print(f"\n{i}. [{item['source']}] {item['title']}")
        if item["description"]:
            print(f"   {item['description'][:120]}...")
        print(f"   {item['url']}")


if __name__ == "__main__":
    main()
