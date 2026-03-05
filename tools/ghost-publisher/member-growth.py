#!/usr/bin/env python3
"""
Member Growth Tools for Ghost newsletters.
- Welcome email automation
- Social sharing meta optimization
- Newsletter CTA injection
- Member analytics
"""

import json
import sys
import os
import hashlib
import hmac
import time
import requests
from datetime import datetime, timezone

# ── Ghost API Config ──
SITES = {
    "portugal": {
        "url": "https://theportugalbrief.pt",
        "admin_key": "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4",
        "content_key": "572ac18cd3e84202174908842b",
        "name": "The Portugal Brief",
    },
    "finance": {
        "url": "http://localhost:2370",
        "admin_key": "6998e826bb07b687f6c5a2b1:224fbf8e1b29fe60ba40410532d0f8e968c32e82b97a558db6adad1c58a72906",
        "content_key": "495686c7f28fa54a5dea9d13eb",
        "name": "Daily Finance Pulse",
    },
}


def make_token(admin_key):
    """Generate Ghost Admin API JWT token."""
    import jwt
    kid, secret = admin_key.split(":")
    iat = int(time.time())
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    payload = {"iat": iat, "exp": iat + 300, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)


def get_members(site_key="portugal"):
    """Get all members for a site."""
    site = SITES[site_key]
    token = make_token(site["admin_key"])
    headers = {"Authorization": f"Ghost {token}"}
    url = f"{site['url']}/ghost/api/admin/members/?limit=all"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("members", [])


def get_member_stats(site_key="portugal"):
    """Get member statistics."""
    members = get_members(site_key)
    site = SITES[site_key]

    stats = {
        "site": site["name"],
        "total_members": len(members),
        "free": sum(1 for m in members if not m.get("paid")),
        "paid": sum(1 for m in members if m.get("paid")),
        "recent_7d": 0,
        "recent_30d": 0,
    }

    now = datetime.now(timezone.utc)
    for m in members:
        created = datetime.fromisoformat(m["created_at"].replace("Z", "+00:00"))
        days = (now - created).days
        if days <= 7:
            stats["recent_7d"] += 1
        if days <= 30:
            stats["recent_30d"] += 1

    return stats


def optimize_post_sharing(site_key="portugal"):
    """Check and report on social sharing optimization for recent posts."""
    site = SITES[site_key]
    token = make_token(site["admin_key"])
    headers = {"Authorization": f"Ghost {token}"}

    url = f"{site['url']}/ghost/api/admin/posts/?limit=20&order=published_at%20desc&filter=status:published&formats=html"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    posts = resp.json().get("posts", [])

    issues = []
    for p in posts:
        post_issues = []
        if not p.get("og_image") and not p.get("feature_image"):
            post_issues.append("no social image")
        if not p.get("og_title") and not p.get("meta_title"):
            post_issues.append("no social title")
        if not p.get("og_description") and not p.get("meta_description"):
            post_issues.append("no social description")
        if not p.get("custom_excerpt"):
            post_issues.append("no excerpt")

        # Check title length for social (optimal: 50-60 chars)
        title = p.get("og_title") or p.get("meta_title") or p.get("title", "")
        if len(title) > 70:
            post_issues.append(f"title too long ({len(title)} chars)")

        if post_issues:
            issues.append({"title": p["title"], "slug": p["slug"], "issues": post_issues})

    return {
        "total_checked": len(posts),
        "posts_with_issues": len(issues),
        "issues": issues,
    }


def generate_cta_html(site_key="portugal"):
    """Generate CTA HTML snippets for embedding in posts."""
    site = SITES[site_key]
    name = site["name"]

    cta_inline = f"""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 12px; padding: 24px; margin: 24px 0; border: 1px solid #0f3460; text-align: center;">
    <p style="color: #e0e0e0; font-size: 16px; margin: 0 0 12px 0;">📬 Enjoying this content?</p>
    <p style="color: #a0a0b0; font-size: 14px; margin: 0 0 16px 0;">Get {name} delivered to your inbox — free, daily, no spam.</p>
    <a href="#/portal/signup" style="display: inline-block; background: #0066ff; color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 15px;">Subscribe Free →</a>
</div>
"""

    cta_footer = f"""
<hr style="border: 1px solid #1a1a2e; margin: 32px 0;">
<div style="text-align: center; padding: 16px 0;">
    <p style="color: #888; font-size: 13px;">Share this with someone who'd find it useful 👇</p>
    <p style="font-size: 13px;">
        <a href="https://twitter.com/intent/tweet?url={{{{url}}}}&text={{{{title}}}}" style="color: #1da1f2; text-decoration: none;">Twitter</a> · 
        <a href="https://www.linkedin.com/sharing/share-offsite/?url={{{{url}}}}" style="color: #0077b5; text-decoration: none;">LinkedIn</a> · 
        <a href="mailto:?subject={{{{title}}}}&body={{{{url}}}}" style="color: #ea4335; text-decoration: none;">Email</a>
    </p>
</div>
"""
    return {"inline_cta": cta_inline.strip(), "footer_cta": cta_footer.strip()}


def inject_cta_to_recent_posts(site_key="portugal", dry_run=True):
    """Add CTA to recent posts that don't have one."""
    site = SITES[site_key]
    token = make_token(site["admin_key"])
    headers = {"Authorization": f"Ghost {token}", "Content-Type": "application/json"}

    url = f"{site['url']}/ghost/api/admin/posts/?limit=all&order=published_at%20desc&filter=status:published&formats=html"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    posts = resp.json().get("posts", [])

    cta = generate_cta_html(site_key)
    cta_marker = "portal/signup"  # Check if CTA already exists
    updated = 0

    for p in posts:
        html = p.get("html", "")
        if cta_marker in html:
            continue  # Already has CTA

        # Skip very short posts (briefings)
        if len(html) < 500:
            continue

        new_html = html + "\n" + cta["inline_cta"]
        if dry_run:
            print(f"  Would add CTA to: {p['title']}")
            updated += 1
            continue

        update_url = f"{site['url']}/ghost/api/admin/posts/{p['id']}/"
        payload = {
            "posts": [{
                "html": new_html,
                "updated_at": p["updated_at"],
            }]
        }
        try:
            r = requests.put(update_url, headers=headers, json=payload)
            r.raise_for_status()
            updated += 1
            print(f"  ✅ Added CTA to: {p['title']}")
        except Exception as e:
            print(f"  ❌ Failed on {p['title']}: {e}")

    return {"updated": updated, "total": len(posts), "dry_run": dry_run}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Member growth tools")
    parser.add_argument("action", choices=["stats", "audit", "cta-preview", "cta-inject"])
    parser.add_argument("--site", default="portugal", choices=["portugal", "finance"])
    parser.add_argument("--apply", action="store_true", help="Actually apply changes (not dry run)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.action == "stats":
        result = get_member_stats(args.site)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n📊 {result['site']} Member Stats")
            print(f"  Total: {result['total_members']}")
            print(f"  Free: {result['free']} | Paid: {result['paid']}")
            print(f"  New (7d): {result['recent_7d']} | New (30d): {result['recent_30d']}")

    elif args.action == "audit":
        result = optimize_post_sharing(args.site)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n🔍 Social Sharing Audit — {SITES[args.site]['name']}")
            print(f"  Checked: {result['total_checked']} posts")
            print(f"  With issues: {result['posts_with_issues']}")
            for issue in result["issues"]:
                print(f"  ⚠️  {issue['title']}: {', '.join(issue['issues'])}")

    elif args.action == "cta-preview":
        cta = generate_cta_html(args.site)
        print("\n--- Inline CTA ---")
        print(cta["inline_cta"])
        print("\n--- Footer CTA ---")
        print(cta["footer_cta"])

    elif args.action == "cta-inject":
        result = inject_cta_to_recent_posts(args.site, dry_run=not args.apply)
        print(f"\n{'🔍 DRY RUN' if not args.apply else '✅ APPLIED'}: {result['updated']}/{result['total']} posts")
