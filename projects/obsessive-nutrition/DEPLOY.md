# Deploying obsessivenutrition.com

Domain is registered: obsessivenutrition.com (registered Mar 4 2026, expires 2029, via Cloudflare)
Git repo: Windsor/obsessive-nutrition

## Option A: GitHub Pages (Recommended — Free, fast, zero maintenance)

### Step 1: Enable GitHub Pages
1. Go to https://github.com/Windsor/obsessive-nutrition
2. Settings → Pages
3. Source: Deploy from a branch
4. Branch: `main`, Folder: `/website`
5. Save

### Step 2: Configure Custom Domain in GitHub
1. In the same Pages settings panel, enter: `obsessivenutrition.com`
2. Check "Enforce HTTPS" once DNS propagates

### Step 3: Configure DNS in Cloudflare
Since the domain is on Cloudflare, add these DNS records:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | @ | 185.199.108.153 | DNS only (grey cloud) |
| A | @ | 185.199.109.153 | DNS only (grey cloud) |
| A | @ | 185.199.110.153 | DNS only (grey cloud) |
| A | @ | 185.199.111.153 | DNS only (grey cloud) |
| CNAME | www | Windsor.github.io | DNS only (grey cloud) |

**Important:** Disable Cloudflare proxy (grey cloud) for GitHub Pages to work with HTTPS.

### Step 4: Wait for DNS propagation (~5-30 minutes)
Site will be live at https://obsessivenutrition.com

The CNAME file in `/website/CNAME` is already set to `obsessivenutrition.com` — GitHub Pages needs this file to serve on your custom domain.

---

## Option B: Netlify (Also free, drag-and-drop)

1. Go to https://app.netlify.com/
2. "Add new site" → "Deploy manually"
3. Drag the `/website/` folder onto the Netlify UI
4. Site deploys instantly with a netlify.app URL
5. Go to "Domain settings" → add `obsessivenutrition.com`
6. Update Cloudflare DNS to point to Netlify's IPs (they'll show you the exact records)

---

## Option C: r2d2 (nginx, same server as PT Brief)

If you want full control:
```bash
ssh windsor1337@192.168.68.139
sudo mkdir -p /var/www/obsessive-nutrition
# rsync the website folder
sudo nano /etc/nginx/sites-available/obsessive-nutrition
```

nginx config:
```nginx
server {
    listen 80;
    server_name obsessivenutrition.com www.obsessivenutrition.com;
    root /var/www/obsessive-nutrition;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
```

Then:
```bash
sudo ln -s /etc/nginx/sites-available/obsessive-nutrition /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
# Add Cloudflare origin cert for HTTPS
```

---

## Recommendation

**GitHub Pages** — zero cost, zero maintenance, auto-deploys on every git push. Perfect for a static site.

Once live:
1. Submit sitemap to Google Search Console: https://search.google.com/search-console/
2. Add Google Analytics (optional)
3. Set up email capture (ConvertKit / Mailchimp free tier)
