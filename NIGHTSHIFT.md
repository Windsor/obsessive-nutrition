# NIGHTSHIFT.md — Autonomous Overnight Work

*Runs 11pm–7am Lisbon time. Work through tasks in priority order. Log everything to memory/YYYY-MM-DD.md.*

## Rules
- Max autonomy — don't message Glenn unless something is truly urgent
- Commit and push changes where repos exist
- Update Project Tracker with all progress
- Log completed work in daily memory file
- If a task is blocked, skip it and move to the next
- Review and update MEMORY.md at end of shift

## Block 1 — 11pm (2026-03-05→Mar 6) ✅ COMPLETE
- ✅ Health check: all services active, disk 88%, RAM 8.9GB free — r2d2 stable
- ✅ PT Brief: 3 articles published (Portuguese Citizenship 2026, Silver Coast guide, Starting a Business in Portugal)
- ✅ All 3 auto-posted to Bluesky via social-poster webhook
- ✅ PT Brief total: ~236 published posts
- ✅ Obsessive Nutrition: ashwagandha.html (~2,900 words — KSM-66 vs Sensoril, cortisol RCTs, thyroid warning, dosing table)
- ✅ Obsessive Nutrition: berberine.html (~3,100 words — AMPK mechanism, metformin head-to-head table, bioavailability problem, CYP3A4 interactions, Ozempic myth debunked)
- ✅ Blog index updated (19 articles), sitemap updated (27 URLs)
- ✅ Committed + pushed: commit ca8caae → Windsor/obsessive-nutrition
- ✅ Offsite backup: ghost_portugal 2.2MB → workspace/backups/r2d2/2026-03-06-block1/
- ✅ Project Tracker: tasks #367–369

## Priority Queue

### High Priority

1. **r2d2 server recovery** ✅ RESOLVED
2. **Obsessive Nutrition website** ✅ LARGELY COMPLETE — READY TO DEPLOY
   - Block 1 Mar 3: Site structure, 9 blog articles, books page, about, index
   - Block 2 Mar 4: Missing curcumin article, book landing pages (sardines + olive-oil), sitemap.xml
   - Block 1 Mar 5: fermented-foods.html (10th article), CNAME file, DEPLOY.md, commit b9f20be
   - Block 2 Mar 5: vitamin-d.html + magnesium.html (11th + 12th articles), commit 7110947
   - Git repo: Windsor/obsessive-nutrition — fully navigable, all links resolve, 12 blog articles
   - **Domain registered** ✅ obsessivenutrition.com (Cloudflare, expires 2029)
   - **Glenn needs to:** Enable GitHub Pages (Settings → Pages → /website) + add DNS records in Cloudflare
   - Full instructions: `projects/obsessive-nutrition/DEPLOY.md`
   - Remaining after deploy: email list setup

2. **Social poster expansion** ✅ MOSTLY DONE
   - ✅ Dynamic hashtags, Bluesky profile, posts tagged, analytics tracker
   - ✅ Bluesky image card generator (Pillow 1200x630, deployed Mar 2 night shift)
   - ✅ Bluesky growth automation (15 follows + 20 likes/night, cron at 11pm)
   - ✅ Reddit cross-posting module deployed (needs credentials from Glenn)
   - Mastodon/Twitter/LinkedIn — blocked on Glenn credentials

3. **Finance publisher resilience**
   - FRED API key still needed (blocked on Glenn)
   - Stripe integration for paid tier (blocked on Glenn)

4. **Member growth strategy**
   - ✅ Content performance analyzer, social coverage 100%, Bluesky growth automation
   - ✅ Growth dashboard, newsletter growth plan document
   - ✅ 4 deep-feature articles published tonight (bank accounts, housing, startups, IRS)
   - ✅ 17 evergreen guides scheduled (2/week through April 23)
   - Google News submission (blocked on static file serving / Google Search Console)
   - Stripe for paid tier (blocked on Glenn)
   - Reddit r/portugal cross-posting (ready — needs credentials)

5. **Email deliverability** — CRITICAL for growth
   - theportugalbrief.pt missing DKIM (needs Glenn to set up in Brevo)
   - SPF softfail, DMARC monitoring-only
   - Without DKIM, newsletters may land in spam

6. **Infrastructure cleanup**
   - Docker image cleanup (bookaroo 24GB, camp_champ 5.5GB) — needs Glenn approval
   - GitHub push for finance-clip-pipeline — needs repo creation

### Blocked / Needs Glenn
- Docker image cleanup (needs approval)
- GitHub push for finance-clip-pipeline (needs repo)
- Finance video: auto-upload to YouTube/TikTok (needs API keys)
- FRED API key registration
- IndexNow verification file (needs Docker proxy static file serving)
- Social poster: Mastodon/Twitter/LinkedIn API keys
- Ghost site settings (cover_image, og_image) — needs Owner-level API
- Portal signup button — needs Owner API
- DKIM setup in Brevo dashboard

## Block 3 — 3am (2026-03-05) ✅ COMPLETE
- ✅ Health check: all services active, disk 88%, RAM 9.2GB free — r2d2 stable
- ✅ PT Brief: 5 articles published total this block (AIMA, Private Healthcare, Remote Work Tax/IFICI, Porto vs Lisbon, Recibos Verdes self-employed guide)
- ✅ All 5 auto-posted to Bluesky (confirmed in journalctl)
- ✅ PT Brief total: 217 published posts
- ✅ Obsessive Nutrition: zinc.html (forms comparison table, copper antagonism, immunity/testosterone — ~2,600 words)
- ✅ Obsessive Nutrition: creatine.html (500+ trial summary, myth-busting, cognitive benefits — ~3,000 words)
- ✅ Obsessive Nutrition: vitamin-b12.html (who's at risk, forms, spirulina myth, dosing guide — ~2,400 words)
- ✅ Blog index updated (15 articles), sitemap updated (23 URLs)
- ✅ Committed + pushed: commits 9f1311a + 02a46ea → Windsor/obsessive-nutrition
- ✅ Offsite backup: ghost_portugal 2.1MB → workspace/backups/r2d2/2026-03-05-block3/
- ✅ Project Tracker: tasks #360–363

## Block 2 — 1am (2026-03-05) ✅ COMPLETE
- ✅ Health check: all 5 services active, disk 88%, RAM 9.2GB free — r2d2 stable
- ✅ PT Brief: 3 articles published (banking, learning Portuguese, transport/cars)
- ✅ All 3 auto-posted to Bluesky (confirmed in journalctl)
- ✅ PT Brief total: 208 published posts
- ✅ Obsessive Nutrition: vitamin-d.html written (blood level table, D3 vs D2, sunlight limits, K2, dosing — 2,500 words)
- ✅ Obsessive Nutrition: magnesium.html written (all forms compared with absorption %, sleep/anxiety, food sources — 2,400 words)
- ✅ Blog index updated (12 articles), sitemap updated (20 URLs)
- ✅ Committed + pushed: commit 7110947 → Windsor/obsessive-nutrition
- ✅ Offsite backup: ghost_portugal 2.0MB → workspace/backups/r2d2/2026-03-05-block2/
- ✅ Project Tracker: tasks #358–359

## Block 1 — 11pm (2026-03-04→Mar 5) ✅ COMPLETE
- ✅ Health check: all 5 services active, disk 88%, RAM 9.1GB free — r2d2 stable
- ✅ PT Brief: 3 articles published (Minho Region, Moving with Pets, Retiring in Portugal)
- ✅ All 3 auto-posted to Bluesky (social tag included)
- ✅ PT Brief total: ~203 published posts
- ✅ Discovered: obsessivenutrition.com REGISTERED by Glenn (Cloudflare, Mar 4 2026)
- ✅ Obsessive Nutrition: fermented-foods.html article written (Stanford RCT, kefir/kimchi/sauerkraut)
- ✅ Obsessive Nutrition: CNAME file added for GitHub Pages
- ✅ Obsessive Nutrition: DEPLOY.md created with full GitHub Pages + Netlify + nginx instructions
- ✅ Blog index + sitemap updated (now 10 articles, 16 URLs)
- ✅ Committed + pushed: commit b9f20be → Windsor/obsessive-nutrition
- ✅ Offsite backup: ghost_portugal 2.0MB, project_tracker 24K → workspace/backups/r2d2/2026-03-05-block1/
- ✅ Project Tracker: tasks #353–355

## Block 4 — 5am (2026-03-05) ✅ COMPLETE (Final)
- ✅ Health check: all services active, disk 88%, RAM 9.2GB free — r2d2 stable
- ✅ PT Brief: 2 articles published — International Schools in Portugal 2026 + Portuguese Tax for Expats 2026 (IRS brackets, IFICI, NHR, CGT, DTAs)
- ✅ Both auto-posted to Bluesky via social-poster webhook
- ✅ PT Brief total: 219 published posts (end of night shift)
- ✅ Obsessive Nutrition: collagen.html (~2,800 words — hydrolysed vs UC-II, joints/skin/bone/gut evidence, forms comparison, vitamin C cofactor)
- ✅ Obsessive Nutrition: probiotics.html (~3,200 words — strain-specific evidence, LGG + S.boulardii + B.infantis 35624 + VSL#3, AAD/IBS/immunity/gut-brain axis)
- ✅ Blog index updated (17 articles), sitemap updated (25 URLs)
- ✅ Committed + pushed: commit 835a43a → Windsor/obsessive-nutrition
- ✅ Final offsite backup: ghost_portugal 2.1MB, project_tracker 25KB → workspace/backups/r2d2/2026-03-05-block4/
- ✅ Project Tracker: 3 tasks created (projects #10 and #12)
- ✅ MEMORY.md reviewed and updated
- Night shift total (Mar 4/5): Blocks 1–4, 10 PT Brief articles published (219 total), 8 new Obsessive Nutrition articles (17 total), 4 commits pushed

## Block 4 — 5am (2026-03-04) ✅ COMPLETE (Final)
- ✅ Health check: all 5 services active, disk 88%, RAM 5.1GB free — r2d2 stable
- ✅ Duplicate article cleanup: 55 articles deleted (Block 3 cron re-fired 12+ times, Block 2 re-fired 4+ times)
- ✅ PT Brief post count: 190 published (clean, no duplicates)
- ✅ Rate limit guard added to publish.py: max 6 articles/hour via /tmp/ghost_publish_count.txt
- ✅ Final offsite backup: ghost_portugal 1.8MB, ghost_finance 640K, project_tracker 24K → workspace/backups/r2d2/2026-03-04-final/
- ✅ MEMORY.md reviewed and updated
- ✅ Project Tracker: tasks #351–352
- Night shift total (Mar 3/4): Blocks 1–4, ~18 PT Brief articles published (clean), Obsessive Nutrition site completed, rate-limit guard deployed

## Block 3 — 3am (2026-03-04) ✅ COMPLETE
- ✅ Health check: r2d2 healthy, all 5 services active, disk 88%, RAM 5.2GB free
- ✅ PT Brief: IFICI/NHR explainer published (~1,500 words) — who qualifies, vs old NHR, retiree impact
- ✅ PT Brief: Healthcare in Portugal for Expats — SNS, private costs, insurance guide
- ✅ PT Brief: Moving to Alentejo — property prices, cost of living, practicalities
- ✅ All 3 Bluesky-posted manually via ~/social-poster/bluesky_post.py
- ✅ Fixed: publish.py + braga-weekly.py now auto-include "social" tag → future articles auto-post to Bluesky
- ⚠️ NOTED: Block 2 cron fired multiple times → ~10 duplicate posts (Lisbon Tech x5, Expat Population x5) — Task #350 for Glenn
- ✅ Offsite backup confirmed (0310 timestamp)
- ✅ MEMORY.md updated (post count, social tag lesson, content list)
- ✅ Project Tracker: tasks #349-350
- PT Brief total: 208 published posts (incl ~10 duplicates Glenn should delete)

## Block 2 — 1am (2026-03-04) ✅ COMPLETE
- ✅ Health check: r2d2 healthy, all 5 services active, disk 88%, RAM 9.3GB free
- ✅ Obsessive Nutrition: curcumin-bioavailability.html article written (missing, referenced everywhere)
- ✅ Obsessive Nutrition: books/sardines.html full landing page built
- ✅ Obsessive Nutrition: books/olive-oil.html full landing page built
- ✅ Obsessive Nutrition: sitemap.xml added (15 URLs) — site fully navigable, committed + pushed to git
- ✅ PT Brief: 3 articles published (Golden Visa 2026, Cost of Living 2026, Rental Market 2026)
- ✅ All 3 PT Brief articles auto-posted to Bluesky (confirmed)
- ✅ Offsite backup: ghost_portugal 2.1MB, ghost_finance 640K, project_tracker 4K
- ✅ Project Tracker: tasks #343-348 created/updated

## Block 1 — 11pm (2026-03-03→Mar 4) ✅ COMPLETE
- ✅ Health check: r2d2 healthy, all 5 services active, disk 88%, RAM 9GB free, PT Brief 172 published
- ✅ PT Brief: 4 articles published (rental prices, min wage, energy impact, tech sector 2026)
- ✅ Obsessive Nutrition website: full static site built (index, books, about, blog, 2 articles, CSS, JS, README)
- ✅ Project Tracker: Project #12 (Obsessive Nutrition) created, tasks #327-335
- ✅ Offsite backup pulled to Mac mini (ghost_portugal + project_tracker)

## Block 1 — 11pm (2026-03-02→Mar 3) ✅ COMPLETE
- ✅ Health check: r2d2 healthy, all 5 services active, disk 88%, RAM 7.8GB free
- ✅ Bluesky image card generator: card_generator.py (Pillow, 1200x630, branded cards)
- ✅ Social poster upgraded: image cards embedded in every Bluesky post (confirmed working — 4 blob uploads)
- ✅ Bluesky growth automation: bluesky-growth.py, 15 new follows + 20 likes tonight, cron 11pm daily
- ✅ 4 feature articles published live on PT Brief (bank accounts, housing crisis, startups, IRS reform 2026)
- ✅ All 4 auto-posted to Bluesky WITH image cards — confirmed in journalctl
- ✅ Finance newsletter: technical_signals.py — RSI, SMA20, SMA50, trend signals for 7 key tickers
- ✅ analysis_generator.py upgraded: includes technical snapshot section in every daily + deep dive
- ✅ Offsite backup pulled to Mac mini (ghost_portugal 1.5MB, project_tracker 21KB)
- ✅ Project Tracker: tasks #316-319

## Block 4 — 5am (2026-03-03) ✅ COMPLETE (Final)
- ✅ Health check: r2d2 healthy, all 5 services active, disk 88%, RAM 6.2GB free
- ✅ PT Brief: 154 published posts confirmed (pagination API)
- ✅ PT Brief: SNS Healthcare Reforms 2026 article published (~1,000 words, Bluesky auto-post)
- ✅ PT Brief: Spring 2026 Property Market article published (~1,200 words, Bluesky auto-post)
- ✅ Final offsite backup pulled to Mac mini (ghost_portugal + project_tracker 5:04 AM)
- ✅ MEMORY.md reviewed and updated (PT Brief count, Block 4 deliverables)
- ✅ Night shift wrap-up: 4 blocks, ~50 deliverables, 2 tech modules, 9 articles published
- ✅ Project Tracker: tasks #324-326

## Block 4 — 5am (2026-03-02) ✅ COMPLETE (Final)
- ✅ Health check: r2d2 healthy, all 5 services active, 100 drafts on Ghost PT
- ✅ Final offsite backup pulled to Mac mini
- ✅ MEMORY.md reviewed and updated (guides 6→17, outage status, Reddit module)
- ✅ Night shift wrap-up: 4 blocks, ~45 deliverables, 17 guides (~55K words), 29 tracker tasks

## Block 3 — 3am (2026-03-03) ✅ COMPLETE
- ✅ Health check: r2d2 healthy, all 5 services active, disk 88%, RAM 6.7GB free
- ✅ PT Brief: ECB rate cut article published (~900 words, SEO meta, JSON-LD, Bluesky)
- ✅ PT Brief: Seguro inauguration analysis published (~1,100 words, Bluesky)
- ✅ PT Brief: Portugal tourism 31.8M record + sustainability debate (~1,200 words, Bluesky)
- ✅ Finance newsletter: sector_analysis.py (11 SPDR ETFs, 1d/5d/1m, risk-on/off, breadth %)
- ✅ analysis_generator.py: sector data wired into Claude prompt + Section 8 added
- ✅ MEMORY.md updated (guide status, social poster tools, finance newsletter)
- ✅ Daily log: memory/2026-03-03.md
- ✅ Project Tracker: tasks #320-323

## Block 3 — 3am (2026-03-02)
- ✅ Health check: r2d2 healthy, all 5 services active
- ✅ 3 new guides: Algarve (~4K words), Education (~3.8K), Salary/Wages (~3.5K)
- ✅ SEO metadata on ALL 16 draft guides (meta titles, descriptions, excerpts, tags)
- ✅ FAQ structured data (JSON-LD) on 7 top guides for Google rich snippets
- ✅ Guides index page updated (17 guides, 5 categories)
- ✅ Cross-linking: 3 new guides with Related Guides sections
- ✅ Guide publishing scheduler (2/week, Mon+Thu, 8 weeks) — ready for approval
- ✅ Social content calendar: 48 posts for 16 guide launches (Mar-Apr)
- ✅ Offsite backup pulled to Mac mini
- ✅ Project Tracker: tasks #307-315

## Block 2 — 1am (2026-03-02)
- ✅ Health check: r2d2 healthy, Ghost Admin API now accessible from Mac Mini
- ✅ 7 new evergreen guides written & published as drafts (NHR Tax, Healthcare, Retiring, Real Estate, Taxes, Residency, Portugal vs Spain)
- ✅ 2 neighborhood guides written & published (Lisbon, Porto)
- ✅ Internal cross-linking: 7 guides with "Related Guides" sections
- ✅ Guides index page (/guides/) created as Ghost page
- ✅ Batch publish script for future guides
- ✅ Project Tracker: tasks #295-306
- Total: 14 evergreen guides now covering all HIGH + most MEDIUM content gaps

## Block 1 — 11pm (2026-03-01→Mar 2)
- ✅ Health check: r2d2 all 5 services healthy, disk 88%, RAM 9.6GB
- ✅ Reddit cross-posting module: deployed to r2d2, praw installed, app.py patched
- ✅ Golden Visa guide published to Ghost (draft)
- ✅ Cost of Living Portugal 2026 guide written (~3,500 words) + published (draft)
- ✅ Digital Nomad Visa D8 2026 guide written (~3,500 words) + published (draft)
- ✅ Buying Property in Portugal 2026 guide written (~3,800 words) + published (draft)
- ✅ Offsite backup pulled to Mac mini
- ✅ Reusable publish-guide.py created on r2d2
- ✅ Project Tracker: tasks #287-294

## Block 1 — 11pm (2026-02-28→Mar 1) ✅ COMPLETE
- ✅ Health check: r2d2 DOWN (since ~6:25 PM Feb 28), HA + local services OK
- ✅ HA Proxy v2: streaming support, /health endpoint, upstream check, better errors
- ✅ Samsung Frame: fixed dynamic forecast days, switched to yfinance for market data
- ✅ BTC Monitor + Frame Dashboard: reloaded LaunchAgents
- ✅ r2d2 Watcher: new tool, checks every 5min, alerts on recovery
- ✅ Reddit cross-posting module for social poster (ready to deploy)
- ✅ Newsletter directory research (10 directories identified)
- ✅ Local health check tool (all LaunchAgents + services)
- ✅ NIGHTSHIFT.md trimmed 305→80 lines, memory archived

## Block 2 — 1am (Mar 1) ✅ COMPLETE
- ✅ r2d2 recovery scripts: recovery.sh + deploy-pending.sh
- ✅ PT Brief logos: 3 versions generated (v2 & v3 scored 7/10)
- ✅ News RSS aggregator: independent Portugal news fetching (5 sources)
- ✅ Samsung Frame: RSS cache fallback when Ghost is down
- ✅ SEO keyword research tool: 100 keywords from Google autocomplete
- ✅ Content gap analysis: 19 uncovered high-value topics identified
- ✅ Evergreen guides plan: 18 articles prioritized with templates
- ✅ MEMORY.md updated

## Block 3 — 3am (Mar 1) ✅ COMPLETE
- ✅ RSS aggregator expanded: 8 feeds (added Expatica, The Local, expat Google News)
- ✅ Golden Visa 2026 guide: ~3,000 words, fully researched, ready to publish
- ✅ D7 Visa 2026 guide: ~2,800 words, income requirements, full process
- ✅ Editorial calendar generator: 4-week schedule with 48 content items
- ✅ Ghost guide publisher: batch publish markdown guides as drafts
- ✅ Subscriber onboarding email sequence: 5-email welcome series
- ✅ Newsletter style guide: voice, formatting, SEO, tag taxonomy
- ✅ Competitor analysis tool: RSS-based topic coverage analysis

## Block 4 — 5am (Mar 1) ✅ COMPLETE (Final)
- ✅ r2d2 still down (~11 hours) — all server tasks blocked
- ✅ Recovery checklist consolidated: `tools/r2d2-watcher/recovery-checklist.md`
- ✅ MEMORY.md reviewed and updated (new tools, content assets, outage status)
- ✅ Night shift wrap-up: 4 blocks, ~30 deliverables
- ✅ All progress logged to memory/2026-03-01.md

## Recent Night Shift History

### Feb 27-28 (26 tasks, #261-286)
- Social poster: dynamic hashtags, Bluesky profile/network, analytics tracker
- Process supervisor vs systemd conflict fix
- Weekly digest cron, newsletter config, growth dashboard
- JSON-LD structured data on 129 posts, OG meta optimization (155 fixes)
- 4 SEO audit tools, content audit 100% healthy
- Docker volume cleanup (137MB freed)

### Feb 26-27 (11 tasks, #250-260)
- Systemd migration (PT/QG/SP), health check v2/v3
- Process supervisor with auto-restart
- Email deliverability audit, content calendar
- Weekly report generator, services dashboard, live health API

### Feb 25-26 (11+ tasks)
- Finance Video V2 major upgrade (glassmorphism, sparklines, gauge)
- Subscribe CTAs in 98 posts, social sharing audit
- SEO: meta tags on all 85 posts, cross-promotion

## Completed (archived — see memory/2026-02-*.md for details)
- Finance/Crypto Newsletter (Ghost, data pipeline, daily cron)
- Quiz Video Generator (104+ videos, intros/outros)
- Portugal Brief (106+ posts, full SEO, social distribution)
- Infrastructure (backups, monitoring, health checks, supervisor)
- All SEO tools, content audit tools, growth tools
