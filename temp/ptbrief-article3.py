#!/usr/bin/env python3
"""Block 3 night shift: Third PT Brief article — Portugal tourism & expat implications."""

import jwt, requests, time, json

KEY_ID = "6995cfb23337d1ed52cfff32"
SECRET = "9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"
BASE = "https://theportugalbrief.pt/ghost/api/admin"

def get_token():
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/admin/"},
        bytes.fromhex(SECRET), algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "kid": KEY_ID}
    )

def headers():
    return {
        "Authorization": f"Ghost {get_token()}",
        "Content-Type": "application/json",
        "Accept-Version": "v5.0"
    }

HTML = """<p>Portugal welcomed 31.8 million overnight tourists in 2025, a record that pushed revenues past €25 billion for the first time and cemented the country's position as one of Europe's fastest-growing destinations. The numbers, released last week by Turismo de Portugal, arrive at a fraught moment: as the tourism industry celebrates yet another banner year, a growing coalition of residents, activists, and economists is questioning whether the model is sustainable — and who it actually benefits.</p>

<h2>The Record in Context</h2>

<p>To understand the scale: Portugal, a country of roughly 10 million people, hosted more than three times its population in tourists last year. The Algarve alone saw 5.9 million overnight stays in peak season, with occupancy rates in some coastal municipalities exceeding 95% during July and August.</p>

<p>Revenue has grown even faster than visitor numbers. The average spend per tourist reached €789 in 2025, up 11% from 2023, driven by the shift toward higher-spending visitors from North America and the Gulf. The US overtook the UK as the single largest source of tourism revenue for the first time, while Brazilian and Angolan visitor numbers also hit records.</p>

<p>By headline measures, the industry employs over 320,000 people directly and contributed approximately 17% of GDP — numbers that give any government pause before tightening the screws on the sector.</p>

<h2>The Costs Nobody Wanted to Talk About</h2>

<p>The pressure points have been visible for years, but 2025 brought them into sharper focus. Rental prices in Lisbon rose another 12% year-on-year, with the average asking rent for a one-bedroom apartment in the capital now exceeding €1,500/month. In Cascais, Sintra, and Comporta, local families report being priced out of communities their grandparents built.</p>

<p>The Alojamento Local (short-term rental) debate remains unresolved. The 2023 moratorium on new AL licences in "pressure zones" was partially extended, but enforcement has been inconsistent and legal challenges from property owners have stalled implementation in several municipalities.</p>

<p>Water is becoming a genuine constraint. The Algarve's aquifers, already stressed from agricultural demand, recorded their lowest spring recharge in two decades. Three municipalities imposed voluntary usage restrictions during August 2025 — the first time such measures have been applied specifically in response to tourism demand rather than drought alone.</p>

<p>Heritage sites tell a similar story. The Jerónimos Monastery in Belém was closed for maintenance twice in 2025 after visitor-related wear exceeded conservation thresholds. Sintra temporarily capped daily visitor numbers for the first time.</p>

<h2>The Government's Balancing Act</h2>

<p>Turismo de Portugal's new director, Isabel Pires, has signalled a shift in strategy: rather than pursuing raw visitor numbers, the goal is to increase revenue per tourist, extend the season geographically and temporally, and direct growth toward the interior.</p>

<p>The "Destinos Sustentáveis" programme — launched in 2024 with €280 million in EU funding — offers municipalities grants to develop inland tourism infrastructure: trails, heritage sites, rural accommodation, and agri-tourism. Early results are mixed; take-up in the interior Alentejo and Beiras has been promising, but the programme has struggled to attract the private investment needed to complement public spending.</p>

<p>There is growing political pressure to use tax policy as a lever. Lisbon and Porto already charge a tourism tax (€2-4 per night), and several smaller coastal municipalities are seeking authorisation to implement their own. A national-level discussion about differentiated VAT rates for AL platforms is expected in parliament this spring.</p>

<h2>What This Means for Expats</h2>

<p>For the international community living in Portugal, the tourism debate has direct implications.</p>

<p><strong>On housing:</strong> The AL market and tourism demand are primary drivers of the housing crisis that affects both Portuguese families and expats trying to rent long-term. Any meaningful reduction in AL licences, or increased regulation, would theoretically free up supply — but the timeline is measured in years, not months.</p>

<p><strong>On cost of living:</strong> Restaurant prices in tourist zones have risen sharply. The gap between prices in Lisbon's Bairro Alto and the same meal in Braga or Évora is now significant enough that many long-term residents consciously avoid tourist-facing establishments.</p>

<p><strong>On quality of life:</strong> The expat community is itself not a monolith here. Recent arrivals in Lisbon's trendier neighbourhoods may experience tourism as background noise; those living year-round in the Algarve experience it as a seasonal transformation that shapes the character of their community for five months of the year.</p>

<p><strong>On opportunity:</strong> For expat entrepreneurs, the tourism sector continues to offer genuine openings — particularly in wellness, sustainable travel, and experience-based tourism, where demand is outpacing supply and established operators are often slow to adapt.</p>

<h2>The Question Nobody Can Quite Answer</h2>

<p>Portugal's tourism success is real, but its distribution is uneven. The 320,000 direct employees earn an average wage significantly below the national median, and seasonal contracts remain the norm in coastal areas. The billionaires buying Comporta farmhouses and the waiters serving them live in entirely different economies.</p>

<p>The country faces a version of a question every successful tourist destination eventually confronts: at what point does the industry that funds the public services a place offers start to undermine the character that made it worth visiting in the first place?</p>

<p>Portugal hasn't reached that point yet — most visitors, and most residents, would agree the balance still works. But the 31.8 million figure is a number that demands an honest conversation about what 35 million might look like, and whether that's actually a goal worth pursuing.</p>

<hr>
<p><em>The Portugal Brief covers Portuguese news, economy, and daily life for expats and internationals. Subscribe for our free daily briefing.</em></p>"""

article = {
    "title": "31.8 Million Tourists, One Uncomfortable Question: Can Portugal Keep Growing Without Breaking?",
    "slug": "portugal-tourism-record-2025-sustainability",
    "meta_title": "Portugal Tourism Record 2025: 31.8 Million Visitors and Growing Concerns",
    "meta_description": "Portugal hit 31.8 million tourists in 2025 — a record. But as revenues surge, questions about housing costs, water supply, and quality of life are getting louder.",
    "custom_excerpt": "Portugal hit 31.8 million overnight tourists in 2025, a new record. But as revenues surge past €25 billion, the debate about what tourism is actually doing to the country is getting harder to avoid.",
    "tags": ["Economy", "Tourism", "Expat Life", "Housing"],
    "html": HTML,
}

lexical = json.dumps({
    "root": {
        "children": [{"type": "html", "version": 1, "html": article["html"]}],
        "direction": "ltr", "format": "", "indent": 0,
        "type": "root", "version": 1
    }
})

json_ld = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": article["title"],
    "datePublished": "2026-03-03T10:00:00Z",
    "author": {"@type": "Organization", "name": "The Portugal Brief"},
    "publisher": {"@type": "Organization", "name": "The Portugal Brief"},
}

payload = {
    "posts": [{
        "title": article["title"],
        "slug": article["slug"],
        "status": "published",
        "custom_excerpt": article["custom_excerpt"],
        "meta_title": article["meta_title"],
        "meta_description": article["meta_description"],
        "tags": [{"name": t} for t in article["tags"]],
        "codeinjection_head": f'<script type="application/ld+json">{json.dumps(json_ld)}</script>',
        "lexical": lexical,
    }]
}

r = requests.post(f"{BASE}/posts/", headers=headers(), json=payload)
if r.status_code == 201:
    post = r.json()["posts"][0]
    print(f"✅ Published: {post['title']}")
    print(f"   URL: https://theportugalbrief.pt/{post['slug']}/")
else:
    print(f"❌ {r.status_code}: {r.text[:300]}")
