# Obsessive Nutrition — Website

Static HTML/CSS/JS website for obsessivenutrition.com.

## Structure
```
website/
├── index.html          # Homepage
├── books.html          # All books listing
├── about.html          # About page
├── css/style.css       # Full stylesheet
├── js/main.js          # Minimal JS (subscribe, scroll animations)
├── blog/
│   ├── index.html      # Blog listing
│   ├── omega-3-daily-dose.html     # Full article (~2,500 words)
│   ├── fake-olive-oil.html         # TODO
│   └── curcumin-bioavailability.html # TODO
└── books/
    ├── sardines.html   # TODO: book landing page
    └── olive-oil.html  # TODO: book landing page
```

## Deployment Options

### Option A: GitHub Pages (Free, instant)
1. Create repo: `obsessive-nutrition-web` (Windsor org)
2. Push this directory
3. Enable GitHub Pages in Settings → Pages → Deploy from branch (main/root)
4. Add custom domain: `obsessivenutrition.com`
5. Add CNAME record in domain registrar pointing to `windsor.github.io`

### Option B: Netlify (Free tier, better CDN)
1. Drag-and-drop the `website/` folder at netlify.com/drop
2. Or: `npm install -g netlify-cli && netlify deploy --dir=website`
3. Set custom domain in Netlify dashboard

### Option C: r2d2 via Nginx (Already have server)
```nginx
server {
    listen 80;
    server_name obsessivenutrition.com www.obsessivenutrition.com;
    root /var/www/obsessive-nutrition;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
```
Then: `scp -r website/* windsor1337@192.168.68.139:/var/www/obsessive-nutrition/`

## Email Integration
The subscribe form currently uses a fake handler.
Replace `handleSubscribe()` in js/main.js with:

### ConvertKit
```javascript
// POST to: https://app.convertkit.com/forms/{FORM_ID}/subscriptions
```

### MailerLite
```javascript
// Use their JS embed
```

## TODO
- [ ] Register obsessivenutrition.com
- [ ] Deploy to chosen host
- [ ] Set up email list (ConvertKit or MailerLite)
- [ ] Create Amazon Associates account
- [ ] Add book landing pages (books/sardines.html, books/olive-oil.html)
- [ ] Write 2 more blog articles (fake-olive-oil.html, curcumin-bioavailability.html)
- [ ] Add sitemap.xml
- [ ] Google Search Console verification
- [ ] Google Analytics
- [ ] Set up KDP accounts and publish books
