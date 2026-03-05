#!/usr/bin/env python3
"""Ping search engines with sitemap URLs after publishing.

Usage:
    python sitemap-ping.py [--site ptbrief|finance|both]

Pings Google and Bing with the sitemap URLs to accelerate indexing.
Run after publishing new content or on a schedule.
"""

import requests, sys, argparse, json
from datetime import datetime, timezone

SITES = {
    "ptbrief": {
        "name": "The Portugal Brief",
        "sitemap": "https://theportugalbrief.pt/sitemap.xml",
        "sitemaps": [
            "https://theportugalbrief.pt/sitemap.xml",
            "https://theportugalbrief.pt/sitemap-posts.xml",
            "https://theportugalbrief.pt/sitemap-pages.xml",
            "https://theportugalbrief.pt/sitemap-tags.xml",
            "https://theportugalbrief.pt/sitemap-authors.xml",
        ]
    },
    "finance": {
        "name": "Daily Finance Pulse",
        "sitemap": "http://192.168.68.139:2370/sitemap.xml",
        "sitemaps": [
            "http://192.168.68.139:2370/sitemap.xml",
        ]
    }
}


def ping_google(sitemap_url):
    """Ping Google with sitemap URL."""
    url = f"https://www.google.com/ping?sitemap={sitemap_url}"
    try:
        r = requests.get(url, timeout=10)
        return {"engine": "google", "sitemap": sitemap_url, "status": r.status_code, "ok": r.status_code == 200}
    except Exception as e:
        return {"engine": "google", "sitemap": sitemap_url, "ok": False, "error": str(e)}


def ping_bing(sitemap_url):
    """Ping Bing with sitemap URL."""
    url = f"https://www.bing.com/ping?sitemap={sitemap_url}"
    try:
        r = requests.get(url, timeout=10)
        return {"engine": "bing", "sitemap": sitemap_url, "status": r.status_code, "ok": r.status_code == 200}
    except Exception as e:
        return {"engine": "bing", "sitemap": sitemap_url, "ok": False, "error": str(e)}


def ping_indexnow(url, key="auto"):
    """Ping IndexNow (Bing/Yandex) for faster indexing of specific URLs."""
    # IndexNow requires a key file hosted on the site — skip for now
    pass


def main():
    parser = argparse.ArgumentParser(description="Ping search engines with sitemaps")
    parser.add_argument("--site", choices=["ptbrief", "finance", "both"], default="both")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    sites = ["ptbrief", "finance"] if args.site == "both" else [args.site]
    results = []

    for site_key in sites:
        site = SITES[site_key]
        # Only ping main sitemap (sub-sitemaps are auto-discovered)
        main_sitemap = site["sitemap"]
        
        # Only ping Google for public sites
        if main_sitemap.startswith("https://"):
            results.append(ping_google(main_sitemap))
            results.append(ping_bing(main_sitemap))
        else:
            results.append({"engine": "skip", "sitemap": main_sitemap, 
                          "ok": True, "note": "Local site — skipping search engine ping"})

    if args.json:
        print(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "results": results}))
    else:
        for r in results:
            status = "✅" if r.get("ok") else "❌"
            engine = r.get("engine", "?")
            print(f"  {status} {engine}: {r.get('sitemap', '?')} — {r.get('status', r.get('note', r.get('error', '?')))}")

    return all(r.get("ok") for r in results)


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
