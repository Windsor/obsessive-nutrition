# Social Media Auto-Posting for The Portugal Brief

## Research Summary (Feb 2026)

### Architecture Decision: Ghost Webhooks + Custom Python Script (Self-hosted on r2d2)

**Why this approach:**
- **Free** — runs on existing r2d2 server
- **No vendor lock-in** — no Zapier/IFTTT monthly fees
- **Full control** — customize post format per platform
- Ghost fires a webhook on `post.published` → hits our Flask listener → posts to all platforms

**Rejected alternatives:**
- **Zapier** — Free tier: 5 zaps, 100 tasks/mo. Would work but costs $20/mo for reliability
- **IFTTT** — Limited Ghost integration, formatting is poor
- **n8n** — Good but overkill for this use case; another service to maintain
- **Make.com** — Similar to Zapier, paid for useful features

---

## Platform Analysis

### 1. 🦋 Bluesky — **PRIORITY 1** (Easiest, Free)
- **Cost:** Completely free, no API tiers
- **Auth:** App Password (generate in Settings → Advanced → App Passwords)
- **Library:** `atproto` Python SDK
- **Rate limits:** Generous (creates: 1,666/day for createRecord)
- **What Glenn needs to do:**
  1. Create a Bluesky account (e.g., `theportugalbrief.bsky.social`)
  2. Go to Settings → Advanced → App Passwords → Create
  3. Save the app password

### 2. 🐦 Twitter/X — **PRIORITY 2** (Free tier works but fragile)
- **Cost:** Free tier allows posting (~1,500 tweets/month at app level)
  - ⚠️ Reports conflict: some say free tier lost write access in 2025, others confirm it works. Basic tier is $200/mo if free doesn't work.
  - **Recommendation:** Try free tier first. If blocked, consider Basic ($200/mo) — probably not worth it for a newsletter.
- **Auth:** OAuth 1.0a (API Key, API Secret, Access Token, Access Token Secret)
- **Library:** `tweepy`
- **What Glenn needs to do:**
  1. Go to https://developer.x.com and create a project/app
  2. Apply for free API access
  3. Generate API Key + Secret, Access Token + Secret (with Read+Write permissions)
  4. Save all 4 credentials

### 3. 💼 LinkedIn — **PRIORITY 3** (Hardest setup, worth it for audience)
- **Cost:** Free API access
- **Auth:** OAuth 2.0 with 3-legged flow (complex!)
- **Required product:** "Share on LinkedIn" or "Community Management API" (needs approval)
- **Library:** `requests` (direct API calls)
- **Complexity:** HIGH — requires OAuth token refresh, LinkedIn app review
- **What Glenn needs to do:**
  1. Go to https://www.linkedin.com/developers/ → Create App
  2. Associate with a LinkedIn Company Page (create "The Portugal Brief" page first if needed)
  3. Request "Share on LinkedIn" product (usually auto-approved)
  4. Note Client ID and Client Secret
  5. Run our one-time OAuth flow to get initial tokens (script provided)
  6. Tokens auto-refresh after that

---

## Setup Instructions

### Server Setup (r2d2)

```bash
# SSH to r2d2
ssh windsor1337@192.168.68.139

# Install dependencies
cd /opt
sudo mkdir -p social-poster
sudo chown windsor1337:windsor1337 social-poster
cd social-poster

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install flask gunicorn atproto tweepy requests

# Copy config and scripts (from workspace)
# See tools/social-poster/ for all files

# Create systemd service
sudo cp social-poster.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable social-poster
sudo systemctl start social-poster
```

### Ghost Webhook Setup

1. Go to Ghost Admin → Settings → Integrations → Add custom integration
2. Name: "Social Auto-Poster"
3. Add webhook:
   - **Event:** Post published (`post.published`)
   - **Target URL:** `http://localhost:5555/webhook/ghost`
4. Save

### Environment Variables (`.env` on r2d2)

```env
# Bluesky
BLUESKY_HANDLE=theportugalbrief.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Twitter/X (optional)
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

# LinkedIn (optional)
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_PERSON_URN=

# Ghost (for fetching full post data)
GHOST_URL=https://theportugalbrief.pt
GHOST_CONTENT_API_KEY=572ac18cd3e84202174908842b

# Webhook secret (set same in Ghost)
WEBHOOK_SECRET=
```

---

## Post Format

Each auto-post will include:
```
📰 {Title}

{First 1-2 sentences of the post / custom excerpt}

🔗 {URL}

#Portugal #Expats #PortugalNews #PortugalBrief
```

Character limits:
- **Bluesky:** 300 chars (will truncate summary if needed)
- **Twitter/X:** 280 chars (will truncate)
- **LinkedIn:** 3,000 chars (plenty of room)

---

## Files

- `tools/social-poster/app.py` — Flask webhook listener + social poster
- `tools/social-poster/config.py` — Configuration
- `tools/social-poster/posters/bluesky.py` — Bluesky posting
- `tools/social-poster/posters/twitter.py` — Twitter/X posting
- `tools/social-poster/posters/linkedin.py` — LinkedIn posting
- `tools/social-poster/social-poster.service` — systemd unit file
- `tools/social-poster/requirements.txt` — Python dependencies
- `tools/social-poster/linkedin_oauth.py` — One-time LinkedIn token setup

---

## Rollout Plan

1. **Phase 1:** Deploy webhook listener + Bluesky (1 hour)
2. **Phase 2:** Add Twitter/X once Glenn has API keys (30 min)
3. **Phase 3:** Add LinkedIn once OAuth is set up (1 hour)
