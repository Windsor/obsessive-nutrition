# Portugal News Newsletter — Tech Stack

## Overview
English-language Portugal news/analysis newsletter with a freemium model (free + paid tiers), web archive, SEO, analytics, and GDPR compliance.

---

## Platform Comparison

### Ghost (Self-Hosted on Ubuntu Server 192.168.68.139)
| Factor | Details |
|---|---|
| **Cost** | Free software. Email via Mailgun (~$0.80/1,000 emails, first 1,000/mo free on Flex). Server already available. Total: **~$0–15/mo** at launch |
| **Commission** | **0%** — you keep everything via Stripe (minus Stripe's ~2.9% + €0.25) |
| **Paid Tiers** | Built-in membership & paid subscriptions via Stripe Connect |
| **Custom Domain** | Full support — point .pt domain directly |
| **SEO** | Excellent — server-rendered, structured data, meta tags, sitemap, clean URLs |
| **Web Archive** | Native — every post is a web page |
| **Analytics** | Built-in member analytics; add Plausible/Umami for web analytics |
| **GDPR** | Double opt-in configurable, easy unsubscribe, no third-party trackers by default, cookie-free if using Plausible |
| **Customization** | Full theme control (Handlebars), custom code injection, API |
| **Email Deliverability** | Depends on your Mailgun/Postmark setup — you control SPF/DKIM/DMARC on .pt domain |
| **Migration** | Content export (JSON + images), member CSV export. Can move to Ghost(Pro) or any platform |
| **Risks** | You handle updates, backups, SSL, security, uptime. Server is local (not cloud) — power/internet outage = downtime |

### Ghost(Pro) (Managed Hosting)
| Factor | Details |
|---|---|
| **Cost** | **$29/mo** (Publisher, billed yearly) — includes paid subscriptions, custom themes, 8,000+ integrations. Starter ($18/mo) has no paid subs |
| **Commission** | **0%** on revenue |
| **Paid Tiers** | Yes (Publisher plan and above) |
| **Custom Domain** | Free custom domain included |
| **SEO/Web/Analytics** | Same as self-hosted, fully managed deliverability |
| **GDPR** | Same as self-hosted + Ghost handles infrastructure compliance |
| **Customization** | Same theme/API access |
| **Email Deliverability** | Managed by Ghost team — excellent reputation, dedicated sending infrastructure |
| **Migration** | Identical export tools. Easy move from self-hosted ↔ Ghost(Pro) |
| **Risks** | Vendor-managed; no server maintenance. Scales pricing with member count |

### Substack
| Factor | Details |
|---|---|
| **Cost** | **Free** to start |
| **Commission** | **10%** of paid subscription revenue + Stripe ~3% = **~13% total** |
| **Paid Tiers** | Yes, built-in |
| **Custom Domain** | Supported (CNAME setup) but limited — always has Substack branding/footers |
| **SEO** | Decent but you're on substack.com subdomain by default; custom domain helps |
| **Web Archive** | Yes — every post is a web page |
| **Analytics** | Basic (open rates, subscribers). No web analytics |
| **GDPR** | Basic compliance; less control over data handling |
| **Customization** | Very limited — fixed templates, no custom code |
| **Email Deliverability** | Good — Substack manages it |
| **Migration** | CSV subscriber export, post export. Harder to move paid subscribers (Stripe transfers possible but manual) |
| **Risks** | 10% forever. Platform lock-in risk. Limited branding. No .pt domain feel |

### Beehiiv
| Factor | Details |
|---|---|
| **Cost** | Free (Launch: ≤2,500 subs). **Scale: $43/mo** (annual). **Max: $96/mo** (annual) |
| **Commission** | **0%** on paid subscriptions (Scale plan+) |
| **Paid Tiers** | Yes (Scale plan+) |
| **Custom Domain** | Yes, all plans |
| **SEO** | Good — web hosting included, custom domains |
| **Web Archive** | Yes — built-in website |
| **Analytics** | Good — campaign analytics on all plans, advanced on Scale+ |
| **GDPR** | Compliant; double opt-in, unsubscribe |
| **Customization** | Moderate — templates, no raw code access. Better than Substack, less than Ghost |
| **Email Deliverability** | Good — optimized infrastructure |
| **Migration** | Subscriber CSV export, content export |
| **Risks** | Pricing scales with features needed. Ad network/Boosts not available in all regions (Portugal may be limited) |

---

## Head-to-Head Summary

| Criteria | Ghost Self-Hosted | Ghost(Pro) | Substack | Beehiiv |
|---|---|---|---|---|
| Monthly cost (launch) | ~$0–5 | $29 | $0 | $0 |
| Monthly cost (1K paid subs) | ~$15 | $29–199 | $0 | $43 |
| Revenue commission | 0% | 0% | 10% | 0% |
| Customization | ★★★★★ | ★★★★★ | ★★ | ★★★ |
| SEO | ★★★★★ | ★★★★★ | ★★★ | ★★★★ |
| Ease of setup | ★★ | ★★★★★ | ★★★★★ | ★★★★★ |
| GDPR control | ★★★★★ | ★★★★ | ★★★ | ★★★★ |
| Email deliverability | ★★★ (DIY) | ★★★★★ | ★★★★ | ★★★★ |
| Migration flexibility | ★★★★★ | ★★★★★ | ★★★ | ★★★★ |

---

## Recommendation

### 🚀 Launch Stack: Ghost Self-Hosted
**Why:** Zero cost, zero commission, full control, already have the Ubuntu server. Perfect for validating the concept before spending money.

**Stack:**
- **CMS:** Ghost 5.x (self-hosted on 192.168.68.139)
- **Email:** Mailgun (Flex plan — free first 1,000 emails/mo, then ~$0.80/1K)
- **Payments:** Stripe (direct integration, ~2.9% + €0.25)
- **Domain:** .pt domain (via pt.pt or registrar like Namecheap/Porkbun)
- **SSL:** Let's Encrypt (via Caddy or Nginx + Certbot)
- **Analytics:** Plausible Analytics (self-hosted or €9/mo cloud) or Umami (self-hosted, free)
- **Backups:** Automated daily to cloud (S3/Backblaze B2)
- **GDPR:** Ghost's built-in double opt-in + cookie-free analytics (Plausible) = no cookie banner needed

### 📈 Long-Term Stack (if revenue justifies managed hosting)
**When to migrate:** When revenue exceeds ~$500/mo or you want to eliminate server ops.

**Option A — Ghost(Pro) Publisher ($29/mo):** Seamless migration from self-hosted. Same themes, same content, managed deliverability. Best if you want to stay in the Ghost ecosystem.

**Option B — Stay self-hosted, move to cloud VPS:** If the local server becomes unreliable, move Ghost to a €5-10/mo Hetzner/DigitalOcean VPS for better uptime. Keep 0% commission.

---

## Setup Steps (Ghost Self-Hosted on 192.168.68.139)

### 1. Prerequisites
```bash
# SSH into server
sshpass -p 'Smurf1337!' ssh windsor1337@192.168.68.139

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18 LTS (Ghost requirement)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Ghost-CLI
sudo npm install -g ghost-cli@latest

# Install MySQL (if not already installed)
sudo apt install -y mysql-server
sudo mysql_secure_installation
```

### 2. Create Ghost Database
```bash
sudo mysql -u root -p
```
```sql
CREATE DATABASE ghost_portugal;
CREATE USER 'ghost'@'localhost' IDENTIFIED BY '<STRONG_PASSWORD>';
GRANT ALL PRIVILEGES ON ghost_portugal.* TO 'ghost'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Install Ghost
```bash
# Create directory
sudo mkdir -p /var/www/portugal-news
sudo chown windsor1337:windsor1337 /var/www/portugal-news
cd /var/www/portugal-news

# Install Ghost
ghost install \
  --url https://yourdomain.pt \
  --db mysql \
  --dbhost localhost \
  --dbuser ghost \
  --dbpass '<STRONG_PASSWORD>' \
  --dbname ghost_portugal \
  --process systemd \
  --no-prompt
```

### 4. Configure Reverse Proxy (Caddy — simplest SSL)
```bash
sudo apt install -y caddy
```

Edit `/etc/caddy/Caddyfile`:
```
yourdomain.pt {
    reverse_proxy localhost:2368
}
```

```bash
sudo systemctl restart caddy
```

### 5. DNS & Domain Setup
- Register `.pt` domain (via pt.pt registrar or international registrar supporting .pt)
- Set DNS A record → server's public IP (or use Cloudflare Tunnel if behind NAT)
- If server is on local network (192.168.68.x), you'll need either:
  - **Cloudflare Tunnel** (recommended, free) — exposes local server securely
  - Port forwarding on router (less secure)

### 6. Configure Mailgun for Email
```bash
# Edit Ghost config
cd /var/www/portugal-news
nano config.production.json
```

Add to config:
```json
{
  "mail": {
    "transport": "SMTP",
    "options": {
      "service": "Mailgun",
      "host": "smtp.eu.mailgun.org",
      "port": 465,
      "secure": true,
      "auth": {
        "user": "postmaster@mail.yourdomain.pt",
        "pass": "MAILGUN_SMTP_PASSWORD"
      }
    }
  },
  "bulk_email": {
    "mailgun": {
      "baseUrl": "https://api.eu.mailgun.net/v3",
      "apiKey": "MAILGUN_API_KEY",
      "domain": "mail.yourdomain.pt"
    }
  }
}
```

Set up in Mailgun:
- Add domain `mail.yourdomain.pt` (use EU region for GDPR)
- Configure SPF, DKIM, DMARC DNS records as provided by Mailgun

```bash
ghost restart
```

### 7. Connect Stripe for Payments
- In Ghost Admin → Settings → Membership
- Connect Stripe account
- Configure free + paid tiers (e.g., Free / €5 monthly / €50 yearly)

### 8. GDPR Configuration
- Ghost Admin → Settings → Membership → enable **double opt-in**
- Every email includes unsubscribe link by default ✓
- Use Plausible Analytics (cookie-free) — no cookie banner needed
- Add a simple privacy policy page

### 9. Backups
```bash
# Add to crontab
crontab -e
```
```
# Daily Ghost backup at 3am
0 3 * * * cd /var/www/portugal-news && ghost backup && find /var/www/portugal-news/backup -mtime +30 -delete
```

### 10. Analytics (Plausible self-hosted)
```bash
# Or use Plausible Cloud at €9/mo for simplicity
# Self-hosted: clone and run via Docker
cd /opt
sudo git clone https://github.com/plausible/community-edition plausible
cd plausible
# Configure and docker compose up -d
```

Inject Plausible script in Ghost Admin → Settings → Code injection → Site Header.

---

## ⚠️ Key Consideration: Local Server
The Ubuntu server at 192.168.68.139 is on a local network. For a public-facing newsletter site you'll need:

1. **Cloudflare Tunnel** (recommended): Free, secure, no port forwarding. Install `cloudflared` on the server, create a tunnel, map your .pt domain.
2. **Static IP + port forwarding**: Riskier, requires router config.
3. **Hybrid**: Host Ghost on local server for writing/admin, use Cloudflare CDN for caching and DDoS protection.

If uptime becomes critical, migrate to a €5/mo Hetzner VPS running the same Ghost setup.

---

## Cost Summary at Launch

| Item | Monthly Cost |
|---|---|
| Ghost (self-hosted) | €0 |
| Mailgun (Flex, <1K subs) | €0 |
| .pt domain | ~€10–15/year (~€1/mo) |
| Cloudflare Tunnel | €0 |
| Plausible (self-hosted) | €0 |
| **Total** | **~€1/mo** |

*At 5,000 subscribers sending 2x/week: Mailgun ≈ €32/mo. Still far cheaper than any managed platform.*
