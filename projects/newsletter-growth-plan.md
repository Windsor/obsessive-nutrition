# Newsletter Growth Plan

*Created: 2026-02-28 | Status: Active*

## Current State
- **The Portugal Brief:** 3 members (all internal), 106 posts, Bluesky cross-posting active
- **Daily Finance Pulse:** 0 members, 23 posts, no social presence yet
- Both newsletters have great content volume but zero organic acquisition

## Immediate Actions (Needs Glenn)

### 1. Enable Portal Signup Button ⚠️ BLOCKED
Both sites have `portal_button: false`. Visitors can't easily subscribe.
- **How:** Ghost Admin → Settings → Portal → Enable floating button
- **Impact:** High — this is the #1 conversion mechanism

### 2. Configure DKIM for Email Deliverability ⚠️ BLOCKED  
PT Brief emails may be landing in spam without DKIM.
- Need DNS TXT record for DKIM signing
- SPF already set but softfail — should be `-all`
- DMARC is monitoring-only — should enforce

### 3. Stripe Integration for Paid Tier
- Ghost Admin → Settings → Membership → Connect Stripe
- Set monthly/yearly pricing
- Enable `paid_members_enabled`

## Growth Channels (Can Do Now)

### Newsletter Directories
Submit PT Brief to:
1. **Newsletter Stack** — https://newsletterstack.com (submit form)
2. **The Sample** — https://thesample.ai (cross-promotion network)
3. **Letterlist** — https://letterlist.com (curated newsletter directory)
4. **Newsletter Crew** — https://newslettercrew.com
5. **Sparktoro** — https://sparktoro.com/trending (audience intelligence)

### Reddit Cross-Posting
- r/portugal — share interesting stories (not spam, add value)
- r/expats, r/digitalnomad — for expat-focused content
- r/europeanews — broader reach
- Rule: Native content, not just links. Add context/summary.

### Social Expansion
- ✅ Bluesky active (30+ posts)
- ⏸ Twitter/X — needs API key
- ⏸ Mastodon — module ready, needs instance credentials
- ⏸ LinkedIn — needs API key
- Facebook groups (Portugal expat groups — manual posting)

### SEO (Already Strong)
- ✅ All posts have meta titles, descriptions, OG tags
- ✅ Custom excerpts on all posts
- ✅ Related posts linked
- ⏸ Google News sitemap (blocked on proxy static file)
- ⏸ IndexNow verification (same blocker)

## Content Strategy Recommendations
1. **Weekly Digest** — ✅ Cron set for Sundays 9am UTC
2. **"What to Know" series** — Monthly explainers on living in Portugal (housing, taxes, visas)
3. **Seasonal content** — Tourism guides, weather patterns, holiday info
4. **Data journalism** — Charts, infographics (housing prices, GDP, etc.)

## Tracking
- Growth dashboard: `python3 /home/windsor1337/ghost-publisher/growth-dashboard.py`
- Bluesky analytics: daily JSONL at `/home/windsor1337/backups/bluesky-analytics/`
- Run growth dashboard weekly to track progress
