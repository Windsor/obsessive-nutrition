# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## Samsung Frame TV

- **IP:** 192.168.68.151
- **Library:** samsungtvws (Python 3.9: `/Users/jarvis/Library/Python/3.9/lib/python/site-packages/`)
- **Dashboard script:** `tools/samsung-frame/dashboard.py`
- **LaunchAgent:** `com.openclaw.frame-dashboard.plist` (runs every 15 min)
- **Active hours:** 7am-10pm (skips upload outside these hours to avoid waking TV)
- **Location:** Braga, Portugal (center of city)
- **Data sources:** Open-Meteo (weather), CoinGecko (crypto), Yahoo Finance (markets), The Portugal Brief Ghost API (news)
- **Layout:** Time 1/3 | Weather 2/3 // Crypto 1/2 | Markets 1/2 // News full width (8 headlines)

## GoAPI — Unified AI API

- **API Key:** `28d1e993476e658cb20cccc52afefd95efb1c7195831e6793b30e6c8bcd91f63`
- **Endpoint:** `https://api.goapi.ai/api/v1/task` (POST to create, GET `/{task_id}` to poll)
- **Header:** `x-api-key: <key>`
- **Docs:** https://goapi.ai/docs
- **Pricing:** PPU (pay-per-use credits) or BYOA (bring your own account)

### Midjourney
- **Script:** `tools/goapi-midjourney/generate.py`
- **Imagine:** `{"model":"midjourney","task_type":"imagine","input":{"prompt":"...","aspect_ratio":"10:16","process_mode":"fast"}}`
- **Upscale:** `{"model":"midjourney","task_type":"upscale","input":{"origin_task_id":"...","index":"1"}}`
- **Modes:** fast, relax, turbo
- **IMPORTANT:** Use `"service_mode": "public"` in config (private bot expired)
- **Note:** MJ API being sunsetted by GoAPI — check for alternatives

### Nano Banana Pro (Gemini 3 Pro Image)
- **Model:** `gemini`, **task_type:** `nano-banana-pro`
- **Input:** `{"prompt":"...","aspect_ratio":"16:9","resolution":"1K"}`
- **Resolutions:** 1K, 2K, 4K
- **Features:** 64K context, multi-turn editing, 8-image composition, text rendering
- **Cost:** ~1,050,000 credits per image (1K)

### Gemini 2.5 Flash Image (Nano Banana)
- **Model:** `gemini`, **task_type:** `gemini-2.5-flash-image`
- **Input:** `{"prompt":"...","aspect_ratio":"16:9","resolution":"1K"}`
- **Faster/cheaper than Nano Banana Pro**

### Other Available Models
- **Flux:** `Qubico/flux1-schnell`, `Qubico/flux1-dev` (task_type: txt2img, img2img, kontext)
- **Kling:** Video generation (txt2video, img2video, virtual try-on, effects)
- **Veo3/3.1:** Google video generation
- **Sora2:** OpenAI video generation
- **GPT-image:** `{"model":"gpt-image","task_type":"image-generation"}`
- **Faceswap, TTS, DiffRhythm, Ace Step, Hailuo, Hunyuan, WanX, Wan, Skyreels, Framepack, Trellis**
- Full list: https://goapi.ai/docs/overview

## Ghost CMS — Finance Newsletter (Daily Finance Pulse)

- **URL:** http://192.168.68.139:2370
- **Admin:** http://192.168.68.139:2370/ghost/
- **Admin API Key:** 6998e826bb07b687f6c5a2b1:224fbf8e1b29fe60ba40410532d0f8e968c32e82b97a558db6adad1c58a72906
- **Content API Key:** 495686c7f28fa54a5dea9d13eb
- **DB:** ghost_finance on r2d2 (MySQL)
- **Service:** ghost-finance (systemd)
- **Publish script:** `tools/finance-publisher/publish.py` (also at `~/finance-publisher/` on r2d2)
- **Cron:** Daily 7am Lisbon

## BTC Monitor

- **Script:** `tools/bitcoin-alert/btc_monitor.py` (TODO: rebuild)
- **LaunchAgent:** `com.openclaw.btc-monitor.plist` (runs every 5 min)

---

## Cloudflare API

- **Token:** `ARzzd5mrTiA5vTFy7nbhAgdV8feuRIHjTDKzGfPS` (Edit zone DNS — obsessivenutrition.com)
- **obsessivenutrition.com Zone ID:** `b730474554ad152039787687ef30c57b`
- API base: `https://api.cloudflare.com/client/v4/`

---

## WhatsApp File Sending

- **Allowed local directories:** `/tmp`, `~/.openclaw/media`, `~/.openclaw/agents`
- To send a local file via WhatsApp, copy it to `~/.openclaw/media/` first
- Example: `cp file.pdf ~/.openclaw/media/ && message(media="/Users/jarvis/.openclaw/media/file.pdf")`

---

## Ubuntu Server (r2d2)

- **IP:** 192.168.68.139
- **User:** windsor1337
- **Password:** Smurf1337!
- **SSH:** `sshpass -p 'Smurf1337!' ssh -o StrictHostKeyChecking=no windsor1337@192.168.68.139`
- **Services:** project-tracker (port 3001), quiz-generator (port 5000)

---

Add whatever helps you do your job. This is your cheat sheet.

## Ghost CMS (Portugal News Newsletter)

- **URL:** https://theportugalbrief.pt (Ghost redirects local HTTP to this)
- **Admin:** https://theportugalbrief.pt/ghost/
- **Content API Key:** 572ac18cd3e84202174908842b
- **Admin API Key:** 6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4
- **API Version:** v5.0 (Ghost v6)
- **DB:** ghost_portugal on r2d2
- **Service:** ghost-portugal (systemd)
