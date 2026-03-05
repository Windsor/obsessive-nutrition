#!/usr/bin/env python3
"""
Post-publish verification — checks that today's posts were published successfully.
Returns exit code 0 if all expected posts exist, 1 if any are missing.
Also checks: HTML content length, feature images, and excerpt presence.
"""
import requests
import re
import time
import jwt
import sys
import json
from datetime import datetime, timezone
from config import GHOST_URL, GHOST_ADMIN_KEY
from log_config import get_logger

log = get_logger("verify")


def get_ghost_token():
    key_id, secret = GHOST_ADMIN_KEY.split(":")
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/admin/"},
        bytes.fromhex(secret),
        algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "kid": key_id},
    )


def verify_today(output_json=False):
    """Check that today's expected posts exist and are well-formed."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
    day_name = datetime.now(timezone.utc).strftime("%A")
    is_weekend = day_name in ("Saturday", "Sunday")

    expected = [
        f"Daily Pulse — {date_str}",
        f"Market Analysis — {date_str}",
    ]

    token = get_ghost_token()
    headers = {"Authorization": f"Ghost {token}"}

    try:
        r = requests.get(
            f"{GHOST_URL}/ghost/api/admin/posts/?limit=15&order=published_at%20desc&include=tags&formats=html",
            headers=headers,
            timeout=15,
        )
        r.raise_for_status()
    except Exception as e:
        log.error(f"Failed to connect to Ghost API: {e}")
        return 2

    posts = r.json()["posts"]
    today_posts = [p for p in posts if p.get("published_at", "").startswith(today)]
    today_titles = [p["title"] for p in today_posts]

    results = {"date": today, "checks": [], "issues": [], "all_ok": True}

    log.info(f"📋 Verification for {today} ({day_name})")
    log.info(f"   Found {len(today_posts)} posts published today")

    # Check required posts
    for title in expected:
        found_post = next((p for p in today_posts if p["title"] == title), None)
        if not found_post:
            log.error(f"   ❌ MISSING: {title}")
            results["checks"].append({"title": title, "status": "missing"})
            results["issues"].append(f"Missing: {title}")
            results["all_ok"] = False
            continue

        issues = []

        # Check HTML content length (should be >500 chars for real content)
        html = found_post.get("html", "")
        if len(html) < 500:
            issues.append(f"Very short content ({len(html)} chars)")

        # Check for feature image
        if not found_post.get("feature_image"):
            issues.append("No feature image")

        # Check excerpt — auto-fix if missing
        if not found_post.get("custom_excerpt"):
            # Auto-generate from HTML, fall back to title for paid/empty posts
            html_text = re.sub(r"<[^>]+>", "", found_post.get("html", ""))
            auto_excerpt = " ".join(html_text.split()).strip()
            if len(auto_excerpt) > 10:
                auto_excerpt = auto_excerpt[:247] + "..."
            else:
                # Paid/members-only posts may have empty HTML via API
                auto_excerpt = found_post.get("title", "Premium content")
            try:
                post_id = found_post["id"]
                fix_url = f"{GHOST_URL}/ghost/api/admin/posts/{post_id}/"
                fix_data = {"posts": [{"custom_excerpt": auto_excerpt, "updated_at": found_post["updated_at"]}]}
                fix_r = requests.put(fix_url, json=fix_data, headers=headers, timeout=10)
                if fix_r.status_code == 200:
                    log.info(f"      🔧 Auto-fixed missing excerpt")
                else:
                    issues.append("No excerpt (auto-fix failed)")
            except Exception:
                issues.append("No excerpt (auto-fix failed)")

        # Auto-fix missing meta fields
        meta_fixes = {}
        title = found_post.get("title", "")
        excerpt_val = found_post.get("custom_excerpt") or auto_excerpt if 'auto_excerpt' in dir() else found_post.get("custom_excerpt", "")
        if not found_post.get("meta_title") and title:
            meta_fixes["meta_title"] = f"{title} | Daily Finance Pulse"[:65]
        if not found_post.get("og_title") and title:
            meta_fixes["og_title"] = title
        if not found_post.get("og_description") and excerpt_val:
            meta_fixes["og_description"] = excerpt_val[:300]
        if meta_fixes:
            try:
                post_id = found_post["id"]
                fix_url = f"{GHOST_URL}/ghost/api/admin/posts/{post_id}/"
                meta_fixes["updated_at"] = found_post["updated_at"]
                fix_r = requests.put(fix_url, json={"posts": [meta_fixes]}, headers=headers, timeout=10)
                if fix_r.status_code == 200:
                    fixed_fields = [k for k in meta_fixes if k != "updated_at"]
                    log.info(f"      🔧 Auto-fixed meta: {', '.join(fixed_fields)}")
                else:
                    issues.append(f"Missing meta fields (auto-fix failed: {fix_r.status_code})")
            except Exception as e:
                issues.append(f"Missing meta fields (auto-fix error: {e})")

        # Check tags
        tags = [t.get("name", "") for t in found_post.get("tags", [])]
        if not tags:
            issues.append("No tags")

        # Check visibility
        vis = found_post.get("visibility", "public")

        status = "ok" if not issues else "warning"
        symbol = "✅" if not issues else "⚠️"
        log.info(f"   {symbol} {title} ({len(html)} chars, {len(tags)} tags, {vis})")
        for issue in issues:
            log.info(f"      ⚠️  {issue}")
            results["issues"].append(f"{title}: {issue}")

        results["checks"].append({
            "title": title,
            "status": status,
            "html_length": len(html),
            "has_image": bool(found_post.get("feature_image")),
            "tags": tags,
            "visibility": vis,
            "issues": issues,
        })

    # Check deep dive (optional, paid)
    # Match deep dive by prefix (title format may vary between cron runs)
    deep_post = next((p for p in today_posts if "Deep Dive" in p["title"]), None)

    if deep_post:
        vis = deep_post.get("visibility", "public")
        html_len = len(deep_post.get("html", ""))
        log.info(f"   ✅ {deep_post['title']} ({html_len} chars, {vis})")
        if vis != "paid":
            log.warning(f"      ⚠️  Expected 'paid' visibility, got '{vis}'")
            results["issues"].append(f"Deep Dive visibility is '{vis}', expected 'paid'")
        results["checks"].append({"title": deep_post["title"], "status": "ok", "visibility": vis})
    else:
        log.info(f"   ⚠️  Deep Dive (not found — optional)")

    # Weekend note
    if is_weekend:
        log.info(f"\n   ℹ️  Weekend — traditional market data reflects Friday's close")

    # Summary
    if results["issues"]:
        log.warning(f"\n⚠️  {len(results['issues'])} issue(s) found")
        results["all_ok"] = False
    else:
        log.info(f"\n✅ All required posts verified and well-formed")

    if output_json:
        print(json.dumps(results, indent=2))

    return 0 if results["all_ok"] else 1


if __name__ == "__main__":
    try:
        json_mode = "--json" in sys.argv
        sys.exit(verify_today(output_json=json_mode))
    except Exception as e:
        log.error(f"Verification crashed: {e}")
        sys.exit(2)
