# Obsessive Nutrition — Website Plan

## Brand
- **Domain:** obsessivenutrition.com
- **Tagline:** "The science of food, without the noise."
- **Audience:** Health obsessives — people who want peer-reviewed evidence, not wellness influencer fluff
- **Tone:** Intelligent, direct, sceptical of hype, occasionally funny. Think "smart friend who reads the actual studies."

## Site Structure

### Home
- Hero: Series overview + latest book
- "What we do": One sentence — deep-dive books on individual foods and health topics
- Latest books (3-up grid with Amazon links)
- Latest blog posts (3-up)
- Email signup: "Get the first chapter of our next book free"

### Books
- Series overview page
- Individual book pages:
  - Cover image
  - What's inside (chapter breakdown)
  - Key findings / "5 things you'll learn"
  - Buy buttons: Kindle | Paperback | Audiobook
  - Sample chapter download (PDF)
  - Reviews

### Blog
- SEO content supporting each book + health topics
- Categories mirror the book series:
  - Superfoods (sardines, olive oil, salmon, etc.)
  - Organ Health (liver, gut, skin, brain, heart)
  - Nutrition Science (debunking myths, research breakdowns)
  - The Obsessive's Kitchen (recipes based on featured foods)

### About
- Who is behind the series (Glenn's bio)
- The mission: cutting through wellness noise with actual science
- Methodology: how books are researched

### Newsletter
- "The Weekly Deep Dive" — one food/topic per week, one interesting study, one practical takeaway
- Free chapter of new book on signup

## Book Landing Page Template
Each book gets its own page at /books/[food-name]:
- Title + subtitle
- Cover (high quality)
- One-line hook
- Chapter list
- 3 key takeaways
- Author note
- Buy CTA (Kindle + Paperback)
- Reader reviews (import from Amazon)
- Related books in series

## Blog SEO Strategy
Each book spawns ~5-10 supporting blog posts targeting long-tail keywords:
- "sardines health benefits" → Book 1 supporting post
- "is canned sardine as healthy as fresh" → Book 1 supporting post
- "omega 3 in sardines vs salmon" → crosslinks Books 1 and 3
- "best olive oil for cooking" → Book 2 supporting post
- "extra virgin olive oil polyphenols" → Book 2 supporting post

## Tech Stack Options
1. **Ghost** (same as PT Brief) — easy to spin up, newsletter built in, good SEO
2. **Static site (Hugo/Astro)** — faster, cheaper, but no built-in newsletter
3. **WordPress** — most flexibility for book-specific plugins (affiliate, reviews)

**Recommendation: Ghost** — you already know it, Mailgun is configured, newsletter works.

## Monetisation Plan
1. **Amazon KDP affiliate links** on every book page (4-8% commission on own books + related)
2. **Newsletter sponsorships** once >1,000 subscribers — nutrition brands, supplement cos, meal kit services
3. **Direct PDF sales** via Gumroad (higher margin than KDP, ~70% vs 35%)
4. **Premium newsletter tier** — "Obsessive+" at €5/month: early access, extended research notes, Q&A

## Book Series Map

### Superfoods Series
1. ✅ Sardines
2. ✅ Olive Oil
3. 🔲 Salmon
4. 🔲 Blueberries
5. 🔲 Turmeric
6. 🔲 Garlic
7. 🔲 Dark Chocolate
8. 🔲 Eggs
9. 🔲 Walnuts
10. 🔲 Fermented Foods (yogurt, kefir, kimchi)
11. 🔲 Green Tea / Matcha
12. 🔲 Bone Broth

### Organ & System Health Series
13. 🔲 Liver Health
14. 🔲 Skin Health (nutrition-focused)
15. 🔲 Gut Health & Microbiome
16. 🔲 Brain Health & Cognitive Function
17. 🔲 Heart Health
18. 🔲 Hormonal Health

### Deep Science Series (advanced)
19. 🔲 Autophagy & Fasting
20. 🔲 Mitochondrial Health
21. 🔲 The Inflammation Spectrum

## Next Steps
1. Register obsessivenutrition.com
2. Spin up Ghost instance (r2d2 port 2372, or new VPS)
3. Design cover template (consistent series look)
4. Write Book 3 outline (Salmon)
5. Set up email list + free chapter lead magnet
6. Write 10 supporting blog posts for Books 1 & 2
