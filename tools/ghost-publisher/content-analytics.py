#!/usr/bin/env python3
"""
Content Analytics Dashboard — Ghost CMS
Tracks publishing patterns, content health, and member engagement.
Outputs JSON or human-readable reports.
"""

import argparse
import json
import sys
import jwt
import time
import requests
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# ── Ghost API Config ──
SITES = {
    "ptbrief": {
        "url": "http://localhost:2368",
        "admin_url": "https://theportugalbrief.pt",
        "content_key": "572ac18cd3e84202174908842b",
        "admin_key": "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4",
        "name": "The Portugal Brief",
    },
    "finance": {
        "url": "http://localhost:2370",
        "content_key": "495686c7f28fa54a5dea9d13eb",
        "admin_key": "6998e826bb07b687f6c5a2b1:224fbf8e1b29fe60ba40410532d0f8e968c32e82b97a558db6adad1c58a72906",
        "name": "Daily Finance Pulse",
    },
}


def get_admin_token(admin_key):
    kid, secret = admin_key.split(":")
    iat = int(time.time())
    payload = {"iat": iat, "exp": iat + 300, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers={"kid": kid})


def fetch_all_posts(site_cfg, include="tags,authors"):
    """Fetch all published posts from a Ghost site."""
    posts = []
    page = 1
    while True:
        url = f"{site_cfg['url']}/ghost/api/content/posts/"
        params = {
            "key": site_cfg["content_key"],
            "limit": 100,
            "page": page,
            "include": include,
            "fields": "id,title,slug,published_at,updated_at,custom_excerpt,meta_title,og_title,og_description,feature_image,reading_time",
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        batch = data.get("posts", [])
        if not batch:
            break
        posts.extend(batch)
        meta = data.get("meta", {}).get("pagination", {})
        if page >= meta.get("pages", 1):
            break
        page += 1
    return posts


def fetch_members(site_cfg):
    """Fetch all members via Admin API."""
    token = get_admin_token(site_cfg["admin_key"])
    headers = {"Authorization": f"Ghost {token}"}
    members = []
    page = 1
    while True:
        base_url = site_cfg.get("admin_url", site_cfg["url"])
        url = f"{base_url}/ghost/api/admin/members/"
        params = {"limit": 100, "page": page}
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        batch = data.get("members", [])
        if not batch:
            break
        members.extend(batch)
        meta = data.get("meta", {}).get("pagination", {})
        if page >= meta.get("pages", 1):
            break
        page += 1
    return members


def analyze_site(site_key, site_cfg):
    """Run comprehensive analytics on a site."""
    posts = fetch_all_posts(site_cfg)
    members = fetch_members(site_cfg)

    now = datetime.utcnow()
    report = {
        "site": site_cfg["name"],
        "generated_at": now.isoformat() + "Z",
        "total_posts": len(posts),
        "total_members": len(members),
    }

    # ── Publishing frequency ──
    dates = []
    for p in posts:
        if p.get("published_at"):
            dt = datetime.fromisoformat(p["published_at"].replace("Z", "+00:00"))
            dates.append(dt)
    dates.sort()

    if dates:
        days_active = max(1, (dates[-1] - dates[0]).days)
        report["first_post"] = dates[0].strftime("%Y-%m-%d")
        report["last_post"] = dates[-1].strftime("%Y-%m-%d")
        report["days_active"] = days_active
        report["avg_posts_per_day"] = round(len(posts) / days_active, 1)

        # Posts per day-of-week
        dow_counts = Counter()
        for d in dates:
            dow_counts[d.strftime("%A")] += 1
        report["posts_by_day_of_week"] = dict(dow_counts.most_common())

        # Posts per hour
        hour_counts = Counter()
        for d in dates:
            hour_counts[d.hour] += 1
        report["posts_by_hour"] = {f"{h:02d}:00": hour_counts.get(h, 0) for h in range(24)}

        # Weekly trend (last 4 weeks)
        weekly = defaultdict(int)
        for d in dates:
            week_start = d - timedelta(days=d.weekday())
            weekly[week_start.strftime("%Y-%m-%d")] += 1
        sorted_weeks = sorted(weekly.items(), key=lambda x: x[0])[-4:]
        report["weekly_trend"] = dict(sorted_weeks)

    # ── Content health ──
    health = {"good": 0, "issues": []}
    for p in posts:
        issues = []
        if not p.get("feature_image"):
            issues.append("missing_image")
        if not p.get("custom_excerpt"):
            issues.append("missing_excerpt")
        if not p.get("meta_title"):
            issues.append("missing_meta_title")
        if not p.get("og_title"):
            issues.append("missing_og_title")
        if not p.get("og_description"):
            issues.append("missing_og_description")
        if issues:
            health["issues"].append({"title": p["title"][:60], "slug": p["slug"], "problems": issues})
        else:
            health["good"] += 1

    report["content_health"] = {
        "healthy_posts": health["good"],
        "posts_with_issues": len(health["issues"]),
        "issues": health["issues"][:10],  # Top 10 only
    }

    # ── Tag distribution ──
    tag_counts = Counter()
    for p in posts:
        for tag in p.get("tags", []):
            tag_counts[tag["name"]] += 1
    report["top_tags"] = dict(tag_counts.most_common(15))

    # ── Member analytics ──
    member_info = {
        "total": len(members),
        "free": sum(1 for m in members if m.get("status") == "free"),
        "paid": sum(1 for m in members if m.get("status") == "paid"),
    }

    # Growth over time
    member_dates = []
    for m in members:
        if m.get("created_at"):
            dt = datetime.fromisoformat(m["created_at"].replace("Z", "+00:00"))
            member_dates.append(dt)
    member_dates.sort()

    if member_dates:
        member_info["first_signup"] = member_dates[0].strftime("%Y-%m-%d")
        member_info["last_signup"] = member_dates[-1].strftime("%Y-%m-%d")
        # Last 7 days
        week_ago = now - timedelta(days=7)
        member_info["signups_last_7d"] = sum(1 for d in member_dates if d.replace(tzinfo=None) > week_ago)
        # Last 30 days
        month_ago = now - timedelta(days=30)
        member_info["signups_last_30d"] = sum(1 for d in member_dates if d.replace(tzinfo=None) > month_ago)

    report["members"] = member_info

    # ── Reading time distribution ──
    reading_times = [p.get("reading_time", 0) for p in posts if p.get("reading_time")]
    if reading_times:
        report["reading_time"] = {
            "avg_minutes": round(sum(reading_times) / len(reading_times), 1),
            "min_minutes": min(reading_times),
            "max_minutes": max(reading_times),
        }

    return report


def print_report(report):
    """Pretty-print a site report."""
    print(f"\n{'='*60}")
    print(f"📊 {report['site']} — Content Analytics")
    print(f"{'='*60}")
    print(f"Generated: {report['generated_at']}")
    print(f"\n📝 Publishing:")
    print(f"  Total posts: {report['total_posts']}")
    print(f"  Active since: {report.get('first_post', 'N/A')} ({report.get('days_active', 0)} days)")
    print(f"  Avg posts/day: {report.get('avg_posts_per_day', 0)}")

    if "weekly_trend" in report:
        print(f"\n📈 Weekly Trend (last 4 weeks):")
        for week, count in report["weekly_trend"].items():
            bar = "█" * count
            print(f"  {week}: {bar} ({count})")

    ch = report.get("content_health", {})
    print(f"\n✅ Content Health:")
    print(f"  Healthy: {ch.get('healthy_posts', 0)}")
    print(f"  With issues: {ch.get('posts_with_issues', 0)}")
    if ch.get("issues"):
        for issue in ch["issues"][:5]:
            print(f"  ⚠️  {issue['title']}: {', '.join(issue['problems'])}")

    m = report.get("members", {})
    print(f"\n👥 Members:")
    print(f"  Total: {m.get('total', 0)} (free: {m.get('free', 0)}, paid: {m.get('paid', 0)})")
    print(f"  Last 7d signups: {m.get('signups_last_7d', 0)}")
    print(f"  Last 30d signups: {m.get('signups_last_30d', 0)}")

    if "reading_time" in report:
        rt = report["reading_time"]
        print(f"\n📖 Reading Time: avg {rt['avg_minutes']}min (range: {rt['min_minutes']}-{rt['max_minutes']}min)")

    if "top_tags" in report:
        print(f"\n🏷️  Top Tags:")
        for tag, count in list(report["top_tags"].items())[:8]:
            print(f"  {tag}: {count}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Ghost Content Analytics")
    parser.add_argument("--site", choices=["ptbrief", "finance", "all"], default="all")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    sites_to_check = list(SITES.keys()) if args.site == "all" else [args.site]
    reports = []

    for site_key in sites_to_check:
        try:
            report = analyze_site(site_key, SITES[site_key])
            reports.append(report)
        except Exception as e:
            print(f"Error analyzing {site_key}: {e}", file=sys.stderr)

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        for r in reports:
            print_report(r)


if __name__ == "__main__":
    main()
