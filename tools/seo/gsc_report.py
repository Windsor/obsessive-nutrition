#!/usr/bin/env python3
"""GSC report for theportugalbrief.pt"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json, sys

CREDS_FILE = "/Users/jarvis/.openclaw/workspace/tools/seo/gsc-credentials.json"
SITE = "sc-domain:theportugalbrief.pt"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

creds = service_account.Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

end = datetime.today()
start = end - timedelta(days=28)
start_str = start.strftime("%Y-%m-%d")
end_str = end.strftime("%Y-%m-%d")

def query(dimensions, row_limit=20, filters=None):
    body = {
        "startDate": start_str,
        "endDate": end_str,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}]
    }
    if filters:
        body["dimensionFilterGroups"] = filters
    return service.searchanalytics().query(siteUrl=SITE, body=body).execute()

print(f"\n📊 The Portugal Brief — GSC Report")
print(f"Period: {start_str} → {end_str}\n")

# Overall totals
totals = query(["date"], row_limit=28)
rows = totals.get("rows", [])
total_clicks = sum(r["clicks"] for r in rows)
total_impressions = sum(r["impressions"] for r in rows)
avg_ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
avg_pos = (sum(r["position"] for r in rows) / len(rows)) if rows else 0

print(f"TOTALS (last 28 days)")
print(f"  Clicks:      {total_clicks:,}")
print(f"  Impressions: {total_impressions:,}")
print(f"  Avg CTR:     {avg_ctr:.1f}%")
print(f"  Avg Position:{avg_pos:.1f}")

# Top pages by clicks
print(f"\n🔥 TOP PAGES BY CLICKS")
pages = query(["page"], row_limit=15)
for r in pages.get("rows", []):
    url = r["keys"][0].replace("https://theportugalbrief.pt", "")
    print(f"  {r['clicks']:>4} clicks | {r['impressions']:>6} impr | pos {r['position']:.0f} | {url[:70]}")

# Top queries by clicks
print(f"\n🔍 TOP SEARCH QUERIES BY CLICKS")
queries = query(["query"], row_limit=20)
for r in queries.get("rows", []):
    print(f"  {r['clicks']:>4} clicks | {r['impressions']:>6} impr | CTR {r['ctr']*100:.1f}% | pos {r['position']:.0f} | {r['keys'][0]}")

# High impression / low click (quick wins — improve title/meta)
print(f"\n⚡ QUICK WINS (high impressions, low CTR — fix title/meta)")
all_pages = query(["page"], row_limit=50)
quick_wins = [r for r in all_pages.get("rows", []) if r["impressions"] > 50 and r["ctr"] < 0.03]
quick_wins.sort(key=lambda r: r["impressions"], reverse=True)
for r in quick_wins[:10]:
    url = r["keys"][0].replace("https://theportugalbrief.pt", "")
    print(f"  {r['impressions']:>6} impr | CTR {r['ctr']*100:.1f}% | pos {r['position']:.0f} | {url[:70]}")

# Top countries
print(f"\n🌍 TOP COUNTRIES")
countries = query(["country"], row_limit=10)
for r in countries.get("rows", []):
    print(f"  {r['clicks']:>4} clicks | {r['keys'][0]}")

# Device breakdown
print(f"\n📱 DEVICE BREAKDOWN")
devices = query(["device"], row_limit=5)
for r in devices.get("rows", []):
    print(f"  {r['clicks']:>4} clicks | {r['impressions']:>6} impr | {r['keys'][0]}")

print()
