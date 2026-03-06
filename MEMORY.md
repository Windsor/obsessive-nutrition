# MEMORY.md - Long-Term Memory

*Curated memories, lessons, and context that matter.*

---

## Origin

- **Born:** 2026-02-06
- **Named by:** Glenn
- **Predecessor:** Friday (lost to config issues)
- **Why "Saturday":** Continues the day-naming tradition. Weekend energy — relaxed but gets things done.

## Glenn

- **GitHub username:** Windsor
- Software engineer, writer, investor
- Building multiple revenue streams via automation
- Values: efficiency, systems that work without hand-holding
- Wants me to be resourceful and proactive, not constantly asking permission

## Active Projects

### Escalate (Adult Party Game)
- Single HTML file at `projects/escalate/index.html`
- Vanilla JS, mobile-first, no framework — easy to share
- Features: 83 cards, 5 levels, dice, timer, voting, gender/orientation matching, stripping mechanic

### Adult Services Directory (Portugal)
- `projects/adult-directory/` — Flask backend + static frontend
- 36 real businesses, Leaflet map, Claude-powered "Add Listing" via URL parsing
- Server runs on port 8000 with ANTHROPIC_API_KEY env var
- Known issue: JS-rendered sites (WordPress/Divi) can't be scraped statically

### Obsessive Nutrition (Health Book Series)
- KDP self-publishing series — science-first deep dives into superfoods and health topics
- Two books already written: Sardines, Olive Oil
- Planned: salmon, blueberries, turmeric, garlic, dark chocolate, eggs, walnuts, fermented foods, green tea, bone broth + organ/system books (Liver, Skin, Gut, Brain, Heart, Hormones)
- Easily 20-30 books total
- **Website:** obsessivenutrition.com ✅ CHOSEN by Glenn (confirmed Mar 3) — blog + book landing pages + email list
- **Series name:** "The Obsessive's Guide to [Food]" or "Obsessive Nutrition: [Food]"
- **Monetization:** KDP royalties + blog SEO → Amazon sales + affiliate links
- **Status:** Website BUILT + domain registered (obsessivenutrition.com, Cloudflare, Mar 4 2026). 17 blog articles live in git. Awaiting GitHub Pages enable by Glenn. DEPLOY.md has full instructions. Project Tracker #12.
- **Competitor gap:** Nobody doing full single-food deep dives, science-first for health obsessives
- **Website contents (17 blog articles as of Mar 5 5am):** omega-3, fake olive oil, curcumin bioavailability, salmon, blueberries, turmeric, garlic, dark chocolate, eggs, fermented foods, vitamin D, magnesium, zinc, creatine, vitamin B12, collagen, probiotics. Plus books (sardines, olive oil landing pages), about page. 25 sitemap URLs. Latest commit: 835a43a.

## Writing Projects

### Cruel Obsession (Erotica Novella)
- Dark romance set in Lisbon — billionaire Aleksandr Volkov + art curator Sofia Marques
- Full text in .docx, metadata at `projects/cruel-obsession/cruel-obsession.md`
- Genre analysis of 3 comp titles at `projects/cruel-obsession/genre-analysis.md`

### Douro Dynasty (Romance Series)
- 4-book dark romance series set in Douro Valley wine country + Porto
- Book 1 (CRUSH) complete: 25 chapters, ~53k words at `projects/douro-dynasty/book1.md`
- Series: Crush → Ferment → Decant → Blend
- Series bible at `projects/douro-dynasty/series-bible.md`

### ENCANTADA (Monster Romance Series — "A Moura's Claim")
- 7-book monster romance series rooted in Portuguese mythology
- American heroines, Mouro Encantado heroes (shapeshifting serpent beings)
- Book 1: Maya Chen (marine biologist, Boston) + Tristão (serpent lord, 287yo)
- Setting: Minho, Portugal. Hidden kingdom "Sob a Pedra" beneath dolmens/castles
- Series bible: `projects/monster-romance/series-bible.md`
- Genre analysis (4 comp titles): `projects/monster-romance/genre-analysis.md`
- Book 1 writing in progress — ch11-30 done, ch1-10 being rewritten
- Style: First person present tense, dual POV, humor + explicit + literary quality

### The Fifth Floor (Literary Erotica Series)
- 5-book series set in a secret society in Lisbon's Alfama district
- Anne Rice Sleeping Beauty level explicitness, literary prose
- Book 1 (THE SALON) complete: ~64k words, Vivienne (art restorer) + Mariana (photographer), F/F
- Series bible: `projects/erotica-series/series-bible.md`
- 5 floors = 5 books: Salon, Garden, Labyrinth, Chamber, Void
- Marketing package NOT yet created for this series

## Project Tracker
- **URL:** http://192.168.68.139:3001
- **Stack:** Flask + PostgreSQL (`project_tracker` DB) on Ubuntu server r2d2
- **Port:** 3001, systemd service `project-tracker`
- **Features:** Big Picture board, Kanban view, per-project boards, artifact system (upload/preview/download), analytics dashboard (search, activity feed, velocity chart, priority/category breakdowns)
- **New APIs:** /api/activity, /api/search, /api/stats/detailed
- **IMPORTANT:** Always keep this board updated — every project, task, and artifact we create goes here
- **API:** POST /api/projects, /api/projects/{id}/tasks, /api/artifacts/register, /api/artifacts/upload
- **Artifacts dir:** ~/project-tracker/artifacts/project-{id}/ on server
- **GitHub:** Not yet pushed (only adult-directory has a repo). Git initialized on r2d2, needs `gh auth login`.

### Portugal News Newsletter (The Portugal Brief)
- Ghost v6.19.1 at `/var/www/portugal-news` on r2d2 (port 2368)
- **Live at:** https://theportugalbrief.pt (via Cloudflare)
- Systemd service: `ghost-portugal`, DB: `ghost_portugal`
- Admin API requires `?source=html` for content (Ghost v6 Lexical editor quirk)
- Publish script: `tools/ghost-publisher/publish.py` (use `publish-json` with JSON files)
- UFW ports: 2368, 2369 open
- Daily content: Morning (7am) + Afternoon (2pm) cron jobs
  - 6-10 feature articles/day, general briefing, markets/biz/tech briefing
  - No emojis, professional tone, "What This Means for Expats" sections
  - **Articles now publish live** (not drafts) — Glenn trusts AI quality
- **Image Library:** 38 verified Unsplash URLs at `projects/portugal-news/image-library.md`
- **Social Poster:** r2d2:5555 (webhook from Ghost, "social" tag required)
  - **IMPORTANT:** Posts MUST have the "social" tag (slug: social) to auto-post. Without it, webhook fires but skips. Night shift articles must add "social" tag explicitly when publishing, or use bluesky_post.py manually.
  - Bluesky active + image cards (1200x630 branded, Pillow), Mastodon module ready (needs credentials from Glenn)
  - Bluesky growth automation: `ghost-publisher/bluesky-growth.py` — 15 follows + 20 likes/night at 11pm
  - Manual Bluesky post script: `~/social-poster/bluesky_post.py` — call `post_to_bluesky(text, url, image_url, title, excerpt, tags)` with text pre-formatted (not None)
  - Retry logic with exponential backoff, stats/health endpoint
  - Twitter & LinkedIn waiting on API keys
- **Published articles:** 219 published as of Mar 5 5am (Block 4 final). Rate limit guard in publish.py prevents duplicate publishing. Night shifts regularly publish 3–6 articles per block.
- **SEO:** Meta descriptions on all posts, tag pages have descriptions + meta.
- **Redirects:** `/subscribe`, `/newsletter`, `/signup` → portal; `/politics`, `/economy`, etc. → tag pages; `/feed`, `/rss.xml` → `/rss/`
- **Navigation:** Home | Politics | Economy | Guides | Braga | About (Glenn needs to add Braga manually in Ghost Admin → Settings → Navigation)
- **About page:** Live at /about/ with full content + SEO meta
- **Recent content topics covered** (to avoid duplication): ECB rate cut (Mar 3), Seguro inauguration (Mar 3), Portugal tourism record (Mar 3), SNS healthcare reforms 2026 (Mar 3), spring property market 2026 (Mar 3), Braga Brief Week 1 (Mar 3), rental prices drop Feb 2026 (Mar 4), minimum wage €920 (Mar 4), energy prices Middle East impact (Mar 4), Portugal tech sector 2026 (Mar 4), Algarve water crisis 2026 (Mar 4), Portuguese schools for expats (Mar 4), Portugal-Angola 2026 (Mar 4), Golden Visa 2026 (Mar 4), Cost of Living 2026 (Mar 4), Rental Market 2026 (Mar 4), Crypto tax Portugal 2026 (Mar 4), Portuguese citizenship 2026 (Mar 4), Digital Nomad D8 visa 2026 (Mar 4), Driving licence conversion (Mar 4), Portugal expat population (Mar 4), Lisbon tech ecosystem 2026 (Mar 4), IFICI/NHR replacement (Mar 4 Block 3), Healthcare SNS for expats (Mar 4 Block 3), Moving to Alentejo (Mar 4 Block 3), Banking in Portugal for expats (Mar 4), Internet & mobile Portugal 2026 (Mar 4), Living in Setubal (Mar 4), Living in Minho Region (Mar 5), Moving to Portugal with pets (Mar 5), Retiring in Portugal 2026 (Mar 5), Opening bank account expat 2026 (Mar 5), Learning Portuguese expat guide (Mar 5), Getting around Portugal transport (Mar 5), AIMA immigration agency explained (Mar 5), Private healthcare costs Portugal 2026 (Mar 5), Working remotely from Portugal tax/IFICI (Mar 5), Porto vs Lisbon comparison (Mar 5), Recibos Verdes self-employed guide (Mar 5), International schools in Portugal 2026 (Mar 5), Portuguese tax for expats IRS/IFICI/NHR (Mar 5)
- **Braga Brief:** Weekly roundup launched Mar 3, 2026. Tag: /tag/braga/, cron ID: 81353e60 (Fridays 8am Lisbon). Script: ~/ghost-publisher/braga-weekly.py on r2d2.
- **Backups:** Daily at 3am UTC (Ghost DB, Project Tracker DB, Quiz Generator DB, Social Poster config), 7-day retention
- **Health monitoring:** Every 30 min checks Ghost, Project Tracker, Quiz Generator, Social Poster
- **Analytics script:** `tools/ghost-publisher/analytics.py` — members, posts, tags, engagement overview
- **Content templates:** `projects/portugal-news/content-templates.md` — 6 article types with style guide
- **Email (transactional):** Brevo SMTP (free, 300/day) — smtp-relay.brevo.com:587, login a2bdcb001@smtp-brevo.com. Used for signup/login emails only. DKIM already configured ✅ (confirmed Mar 3).
- **Email (newsletters):** Mailgun — used for newsletter sends (not Brevo).
- **Weekly Digest:** `tools/ghost-publisher/weekly-digest.py` — auto-compiles week's articles into themed roundup. Cron every Sunday 10am (ID: 608c01be).
- **Evergreen guides (17 total):** All HIGH + MEDIUM content gaps covered. Published as drafts on Ghost:
  - Golden Visa, D7 Visa, Digital Nomad D8, Cost of Living, Buying Property, NHR Tax, Healthcare, Retiring, Real Estate, Taxes, Residency, Portugal vs Spain, Lisbon Neighborhoods, Porto Neighborhoods, Algarve, Education, Salaries & Minimum Wage
  - All 16 draft guides have full SEO metadata (meta_title, meta_description, custom_excerpt, tags)
  - 7 top guides have FAQ structured data (JSON-LD) for Google rich snippets
  - Internal cross-linking with Related Guides sections
  - Guides index page at /guides/ (5 categories, all 17 guides)
  - **Publishing scheduler ACTIVE:** Guides are scheduled in Ghost (status=scheduled), going live 2/week Mon+Thu through April 23
  - Social content calendar: 48 posts mapped to 16 guide launches
  - Reusable guide publisher on r2d2: `~/ghost-publisher/publish-guide.py`
- **Content strategy docs:** editorial calendar (Mar 2-29), onboarding email sequence (5 emails), style guide, evergreen guides plan (18 topics)
- **SEO research:** 100 keywords mapped, 19 content gaps NOW ALL COVERED, competitor analysis done
- **Logo options:** 3 versions at `projects/portugal-news/logo-v{1,2,3}.png` (v2 & v3 best, 7/10)
- Pending: Stripe payments
- **Google Search Console:** Verified ✅, sitemap submitted ✅ (Mar 3, 2026). theportugalbrief.pt/sitemap.xml submitted — all 154 posts queued for indexing.
- Project Tracker: Project #10

### Daily Finance Pulse (Financial Newsletter) — ⛔ SCRAPPED Mar 4, 2026
Glenn decided to focus on The Portugal Brief and Obsessive Nutrition. Ghost service stopped + disabled on r2d2. All 3 finance crons removed. Scripts remain at ~/finance-publisher/ on r2d2 but nothing is running.

<!-- archived below -->
### Daily Finance Pulse (ARCHIVED)
- Ghost v6.19.2 at `/var/www/finance-newsletter` on r2d2 (port 2370)
- Systemd service: `ghost-finance`, DB: `ghost_finance`
- Admin: admin@financepulse.local / FinancePulse2026!
- Admin API Key: `6998e826bb07b687f6c5a2b1:224fbf8e1b29fe60ba40410532d0f8e968c32e82b97a558db6adad1c58a72906`
- Content API Key: `495686c7f28fa54a5dea9d13eb`
- **3-tier content:** Free data pulse, free AI analysis, paid deep dive (Ghost paywall)
- Data sources: CoinGecko (crypto+DeFi TVL+BTC dominance), yfinance (equities/forex/commodities/bonds/VIX/MOVE), Alternative.me (Fear & Greed), DefiLlama
- Expanded coverage: 8 cryptos, 10 indices, 5 forex, 6 commodities, 4 bond yields
- Scripts on r2d2: `~/finance-publisher/` (config.py, data_pipeline.py, template.py, publish.py, macro_data.py, analysis_generator.py, log_config.py, verify_publish.py, technical_signals.py, sector_analysis.py)
- **Technical signals:** RSI-14, SMA20/50, trend for 7 key tickers (SPY, QQQ, BTC, ETH, GLD, TLT, VIX) — wired into daily analysis prompt
- **Sector rotation:** 11 SPDR sector ETFs (1d/5d/1m perf), risk-on/off signal, breadth % — wired into daily analysis prompt. Newsletter now has Section 8: Sector Rotation.
- **Cron jobs:**
  - 7:00 AM — Full edition: data pulse + AI analysis (ID: aedee133)
  - 7:20 AM — AI-curated video with YouTube expert clips (ID: 4a20c77d)
  - 7:30 AM — Premium deep dive, paid/paywalled (ID: b7833e01)
- **Video pipeline v3 (Clip-based):** `~/finance-clip-pipeline/` on r2d2
  - YouTube search → AI picks 2-3 best clips → downloads 15-25s segments (fair use)
  - Adds lower-third commentary overlays, commentary cards between clips
  - **TTS voiceover** on commentary cards (edge-tts, en-US-AndrewNeural voice)
  - **Background ambient music** (ffmpeg-synthesized pad, mixed under voice)
  - Quality scoring for YouTube clips (premium channels, view count, title analysis)
  - Outputs: shorts (9:16), landscape (16:9), square (1:1)
  - Uses yt-dlp + Pillow + ffmpeg + edge-tts
  - Sent daily to Glenn via WhatsApp
  - Git tracked on r2d2 (not yet pushed to GitHub — needs repo creation)
- **Video pipeline v2 (Report cards):** `~/finance-video-generator/` on r2d2
  - Pillow frames + ffmpeg, structured slides (title/narrative/experts/movers/outlook)
  - Fallback if clip pipeline can't find good YouTube content
- **Video pipeline V2 (Savvy Finance style):** `tools/finance-video-v2/` (local)
  - Pillow-based renderer with dark neon aesthetic, kinetic typography
  - Glassmorphism cards, animated particles, Fear & Greed gauge, crypto logos
  - Scrolling ticker strip, scene transitions, highlighted numbers
  - Radial glow background + vignette for depth
  - Visual quality: ~8/10 (Feb 26 assessment). Sparklines, anti-aliased gauge, glassmorphism title card all done. Next: stock B-roll, smoother animations
  - Crypto logos at `assets/logos/` (BTC/ETH/SOL/XRP/ADA/DOGE, 2000x2000 RGBA)
  - Uses OpenClaw TTS tool (not GoAPI — that endpoint hangs)
  - Full render: ~4200 frames, ~5 min render time, outputs landscape (19MB) + shorts (12MB)
  - Frame dir: `~/finance-video-generator/output-v2/frames` (NOT /tmp — gets cleaned mid-render)
  - Audio manifest: 6 segments (~140s total), generated via OpenClaw `tts` tool
  - Market data: `~/finance-video-generator/output-v2/data-YYYY-MM-DD.json`
- **IMPORTANT:** `update_ghost_post()` was missing meta_title/og_title — fixed Feb 25. Watch for regressions.
- Project Tracker: Project #11
- Domain/name TBD — Glenn will decide later
- Blocked: Stripe integration, auto-upload YouTube/TikTok
- **FRED API Key:** `268369bb86b2f31880b0101e895f6db6` — for macro economic data (interest rates, inflation, employment, GDP, etc.)

### Quiz Video Generator
- Flask app at r2d2:5000
- Quiz types: flag guess, geography map, emoji guess, logo guess, silhouette, zoom, blur, scene, eye, odd one out, sound, before/after, visual guess
- Geography map quiz v2: dark navy palette, multiple choice (A/B/C/D) with smart regional distractors, timer with seconds, answer reveal highlighting
- Profile system for different aspect ratios (16:9, 9:16, 1:1)
- Batch generation: `batch_geography.py` — 7 preset quizzes (easy/medium/hard), multi-format
- Capital Cities quiz type: `capital_city_generator.py` — amber accent, 147 capitals, regional distractors
- `batch_capitals.py` — 7 quiz sets (easy/medium/hard), 14 videos generated
- Total video inventory: 104 videos (54 geography + 14 capitals + older quiz types)
- Branded intro/outro system: 8 Remotion clips (geography green + capitals amber, 16:9 + 9:16)
- Concatenation: `add_intros.sh` (single) + `batch_add_intros.sh` (geo) + `batch_add_intros_capitals.sh` (caps)
- **All 79 videos branded** (2026-02-22): 65 geography + 14 capitals, output in `videos_final/`
- Videos at `/home/windsor1337/quiz-video-generator/videos/`, intros at `~/quiz-intros/`
- Project Tracker: Project #9

## Infrastructure (r2d2)
- **Backups:** `/home/windsor1337/backup.sh` — cron at 3am UTC daily, 7-day retention
- **Offsite backups:** Downloaded to Mac mini `workspace/backups/r2d2/` (manual, do periodically)
- **Health checks:** `/home/windsor1337/health-check.sh` v2 — cron every 30 min, checks HTTP + systemd + disk + memory + backup freshness
- **Log rotation:** `/home/windsor1337/logrotate.conf` — weekly, 4 copies, compressed. Cron Sundays midnight.
- **Cleanup scripts:** `~/finance-clip-pipeline/cleanup.py` — removes old clips/output/cache >3 days, cron daily 6am
- **Services:** Ghost (systemd), Project Tracker (port 3001), Quiz Generator (port 5000), Social Poster (gunicorn, port 5555, hardened with restart limits)
- **Process supervisor:** `/home/windsor1337/process-supervisor.sh` — cron every 5 min, checks all 5 services by HTTP, auto-restarts if down. Accepts any HTTP response (200-599) as alive.
- **Services dashboard:** http://192.168.68.139:3001/services — dark-mode auto-refreshing UI showing all service statuses
- **Live health API:** GET http://192.168.68.139:3001/api/health — real-time service/disk/memory checks
- **Weekly report:** `tools/weekly-report.py` on r2d2 — aggregates content output, members, social, system health
- **Growth dashboard:** `ghost-publisher/growth-dashboard.py` on r2d2 — member counts, growth rates, recommendations. Cron Mondays 8am UTC.
- **Weekly digest:** `tools/ghost-publisher/weekly-digest.py` — auto-publishes top 10 stories Sundays 9am UTC
- **Content calendar:** `tools/content-calendar.py` on r2d2 — publishing patterns, gaps, averages
- **Email deliverability:** Brevo DKIM already set up (confirmed by Glenn). DMARC: monitoring-only (fine for now).
- **Mailgun setup checklist:** Dashboard → Sending → Domains → theportugalbrief.pt. Need green checkmarks on: (1) DKIM TXT record, (2) SPF — add `include:mailgun.org` to existing SPF TXT record in Cloudflare, (3) optional tracking CNAME. If domain isn't added yet, add it first. Mailgun blocks sending until DNS verified.
- **JSON-LD structured data:** All 129 posts have NewsArticle schema in codeinjection_head. Auto-generated by both publishers for future posts. Improves Google rich results eligibility.
- **OG meta limits enforced:** og:title ≤70 chars, og:description ≤200 chars. All posts fixed, publishers enforce going forward.
- **SEO audit tools:** content-freshness.py, social-preview-validator.py, link-checker.py on r2d2
- **Content audit:** `tools/ghost-publisher/content-audit.py` — checks images, excerpts, meta, tags across all Ghost posts
- **Disk:** 84.5–90% (fluctuates). Potential savings: bookaroo (24GB), camp_champ (5.5GB) Docker images — need Glenn's approval.
- **SEO meta tags:** All posts on both sites have meta_title, og_title, og_description, meta_description, custom_excerpt. Auto-set by publish scripts for future posts.
- **Cross-promotion:** Finance newsletter footer links to PT Brief.
- **SEO audit:** `projects/seo-growth-audit.md` — comprehensive list of remaining SEO items needing Glenn (cover image, social accounts, code injection, Google Search Console).
- **Tag hygiene:** All tags now have descriptions (25 added Feb 24-25). Consolidated duplicate tags: daily-briefing→Daily Briefing, markets-briefing→Markets Briefing, Defence→Defense, Tech→Technology, Briefing→context-appropriate. Watch for slug-style tags from cron prompts.
- **Dedup enhanced:** publish.py now catches topic-similar articles (keyword overlap), not just exact title matches. Deleted 4 duplicate articles from Feb 20-23.
- **verify_publish.py auto-fixes:** Missing excerpts are now auto-generated from HTML content during verification. Also auto-fixes meta_title, og_title, og_description. For paid/members-only posts with empty HTML, falls back to title as excerpt.

## Communication Channels
- **WhatsApp:** Primary channel
- **Slack:** Bot configured, Glenn's user ID `U0241LR32F4`, DM channel `D0AG01W7LJE`

## Night Shift
- Cron job runs 4 blocks: 11pm, 1am, 3am, 5am
- NIGHTSHIFT.md has the task queue
- Log all work to memory/YYYY-MM-DD.md
- Don't message Glenn unless urgent

## r2d2 Server Outages
- **Feb 28, ~6:25 PM:** Server went down (~11 hours). Recovered by Mar 1 evening.
- **Recovery tools:** `tools/r2d2-watcher/recovery.sh`, `deploy-pending.sh`. r2d2-watcher LaunchAgent checks every 5 min.
- **Reddit cross-posting module deployed** (Mar 1 night shift) — needs Reddit API credentials from Glenn to activate.

## Local Tools (Mac Mini)
- **News aggregator:** `tools/news-aggregator/portugal_rss.py` — 8 RSS feeds (Portugal Resident, The Portugal News, Google News, Expatica, The Local, Algarve Daily News). Works independently of r2d2. Samsung Frame uses cache as fallback.
- **HA Proxy v2:** `tools/ha-proxy/` — streaming support, /health endpoint, upstream checks.
- **Local health check:** `tools/local-health-check.py` — checks all LaunchAgents + HTTP services.
- **SEO tools:** `tools/seo/` — keyword-research.py (Google autocomplete), content-gap.py (topic coverage gaps), competitor-analysis.py (RSS competitor tracking)
- **Editorial calendar:** `tools/editorial-calendar/generate.py` — generates N-week content schedules
- **Ghost guide publisher:** `tools/ghost-publisher/publish_guide.py` — markdown-to-Ghost draft publisher
- **r2d2 recovery:** `tools/r2d2-watcher/recovery.sh` + `deploy-pending.sh` + `recovery-checklist.md`

## Memory Management
- Daily files kept for ~7 days, older ones archived to `memory/archive/`
- Week summaries created during archival (e.g., `2026-02-week1.md`)
- MEMORY.md reviewed and updated during night shifts

## Cron Monitoring
- `tools/cron-monitor/monitor.py` — checks Ghost posts today + service health
- Use `cron list` to verify publish jobs ran (check lastStatus field)

## Lessons Learned (Critical)

- **NIGHT SHIFT IS MANDATORY.** Glenn expects autonomous overnight work EVERY night. Don't sit idle polling. Check `memory/night-shift-queue.md` for tasks, and if empty, find improvements to make. Log work in daily memory files.
- **WRITE PLANS TO FILES, NOT CHAT.** Any plans discussed in conversation MUST be written to `memory/night-shift-queue.md` or HEARTBEAT.md before the session ends. Chat gets compacted — files survive. Glenn has been burned by this multiple times.
- **Don't make Glenn repeat himself.** If he tells you something important, capture it permanently in MEMORY.md, HEARTBEAT.md, or AGENTS.md. Not just daily notes.

## Lessons Learned (Technical)

- **NEVER `git init` without checking first.** Always run `git remote -v` and `git log` before touching a repo. The night shift wiped the project-tracker remote and history by blindly re-initializing.
- **GitHub repos already exist:** Windsor/project-tracker (private), Windsor/adult-directory-portugal (private). R2D2 SSH key is registered on GitHub. Don't ask Glenn about this again.
- **Yahoo Finance v7 API returns 401 now** — use `yfinance` library instead of direct API calls.
- **CoinGecko free tier** rate limits at ~30 req/min — always add retry logic with exponential backoff. File-based cache added (`cache.py`) with stale-data fallback for resilience.
- **Quiz names with slashes** (e.g., "10/10") cause FFmpeg path errors — sanitize names.
- **Ghost deduplication** — publish scripts should check for existing posts by title before creating new ones.
- **VERIFY BACKUPS ACTUALLY CONTAIN DATA.** The backup script was "succeeding" for days with 20-byte empty .gz files. Always check actual file sizes (>100 bytes), not just `-s` (non-empty). MySQL needs explicit user/password, PostgreSQL needs `sudo -u postgres`.
- **Kill orphan processes before systemd restart.** Manual `nohup gunicorn` processes survive and hold ports, causing systemd restart loops (social-poster had 7,726 failed restarts).
- **ffmpeg concat xfade drops audio.** The xfade filter only maps video stream — use simple concat when audio (TTS) is present. Normalization step also overwrites audio with `anullsrc` if not careful — probe first.
- **edge-tts is free and excellent.** Microsoft Neural TTS, no API key needed. `pip install edge-tts`. Best voices: en-US-AndrewNeural (warm/confident), en-US-AriaNeural (news). Installed on r2d2 at `~/.local/bin/edge-tts`.
- **Ghost webhook for social-poster** IS configured and working. Posts with "social" tag will auto-post to Bluesky. Confirmed Feb 22.
- **Systemd hardening:** Use `StartLimitIntervalSec`/`StartLimitBurst` + `ExecStartPre` port cleanup to prevent crash loops. Applied to social-poster after 7,726-restart incident.
- **Ghost excerpts** aren't auto-generated — must be set explicitly via API. Content audit script handles this in bulk.
- **Ghost newsletter sending requires `email_segment: "all"`** in the post payload. Without it, posts publish silently with no email sent. Always include this in any PT Brief publish script. publish.py default is now `send_email=True`. Night shift scripts must include `"email_segment": "all"` in their payloads directly.
- **Night shift cron re-fire problem (Mar 4):** Block 2 and Block 3 isolated cron sessions fired multiple times (12+ re-fires in Block 3), creating 55 duplicate articles. Root cause: AI agent in isolated session kept running rounds of publishing. Fix: rate-limit guard in publish.py (max 6/hour via /tmp/ghost_publish_count.txt). Also: night shift prompts should explicitly say "publish EXACTLY 3 articles then stop."
- **publish.py rate limit guard:** max 6 articles/hour, tracked via /tmp/ghost_publish_count.txt on r2d2. Raises RuntimeError on breach. Added Mar 4 Block 4.
- **Ghost Admin API needs `&formats=html`** to return HTML content in responses. Without it, `html` field is null/empty. Content API returns HTML by default but Admin API does not.
- **Duplicate articles across AM/PM editions** were a real problem. Fixed with: dedup check in publish.py, todays_titles.py helper, and afternoon cron running title check first.
- **Image library should be in a file, not hardcoded in cron prompts.** Moved to `projects/portugal-news/image-library.md` (56 images). Cron prompts now reference the file. Updates propagate automatically.
- **r2d2 Ghost services are system-scope systemd** (`sudo systemctl`). Project Tracker, Quiz Generator, and Social Poster are **NOT systemd units at all** — they're standalone processes (python3/gunicorn). Check with `ps aux | grep` or port checks (`ss -tlnp`), not `systemctl --user`. Content-analytics.py `is-active` checks give false negatives.
- **Logrotate on r2d2** needs a user-level config + cron (no root logrotate.d access).
- **Finance publisher logging was broken.** Scripts used `print()` but logging was set up — log files were 0 bytes. Created shared `log_config.py` and patched all 4 scripts. Now logs to `~/finance-publisher/logs/publish-YYYY-MM-DD.log`.
- **Ghost Portugal Admin API** only works via public URL (`theportugalbrief.pt`), not `localhost:2368`. Ghost validates request URL against its configured `url` setting.
- **Ghost Admin API blocked by Cloudflare from Mac Mini.** All API calls from Mac Mini get 403. Must publish via r2d2 (SCP file, then run `python3 ~/ghost-publisher/publish-guide.py /tmp/file.md`). Same API calls work from r2d2.
- **Ghost Admin JWT tokens expire.** When getting 403/InvalidToken errors from Mac mini, the token isn't the issue — Ghost Admin API is blocked by Cloudflare at the Mac Mini level entirely. Use Content API (public) for reads, publish via r2d2 for writes.
- **Git repos: obsessive-nutrition website** is a separate git repo at `projects/obsessive-nutrition/website/` (Windsor/obsessive-nutrition). The workspace root (`/Users/jarvis/.openclaw/workspace`) is a different repo. Don't confuse them. Always `cd` to the website dir before git commands for ON content.
- **Collagen key nuance:** Hydrolysed collagen peptides (10g/day for joints) ≠ UC-II undenatured Type II collagen (40mg/day, works via oral tolerance — immune mechanism). These are completely different products with different mechanisms. Vitamin C is a required cofactor for both. This is a genuinely confusing area where bad supplement advice is common.
- **Probiotics key nuance:** Strain specificity is everything — "10 billion CFU of Lactobacillus acidophilus" is meaningless without the strain ID (e.g., NCFM). Products without strain identifiers are marketing, not medicine. Best-evidenced strains: S.boulardii CNCM I-745 + L.rhamnosus GG for AAD; B.infantis 35624 for IBS; VSL#3 for UC maintenance.
- **Portugal crypto tax advantage:** Crypto held >365 days is tax-exempt in Portugal as of 2026. This is a genuine and significant advantage vs most EU countries. Worth noting in relevant PT Brief articles.
- **Reusable guide publisher on r2d2:** `~/ghost-publisher/publish-guide.py` — accepts markdown files with metadata headers, publishes as draft or `--live`.
- **Don't use /tmp for long-running frame renders.** macOS cleans /tmp periodically — a 5+ minute render can have its frame dir wiped mid-write. Use `~/` paths instead.
- **Video render OOM prevention:** Save frames as JPG (quality=92) not PNG, and clear frame lists after each save batch. 4200 frames at 1920x1080 is ~25GB of uncompressed bitmaps.
- **Weekend market data:** yfinance returns last trading day's data on weekends. Added weekend awareness to analysis prompts so Claude frames it as weekly recap instead of "today's moves."

## Technical Notes

- Python 3.9 (`/usr/bin/python3`) vs 3.14 (`/opt/homebrew/bin/python3`)
- Pip requires `--break-system-packages`
- Brave Search API key configured at `tools.web.search.apiKey` — needs gateway restart
- Anthropic model name: `claude-sonnet-4-20250514`

---

*Update this file with significant lessons, decisions, and context worth keeping long-term.*
