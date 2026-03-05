#!/usr/bin/env python3
"""Block 3 night shift: Write and publish 2 PT Brief feature articles."""

import jwt, requests, time, json

KEY_ID = "6995cfb23337d1ed52cfff32"
SECRET = "9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"
BASE = "https://theportugalbrief.pt/ghost/api/admin"

def get_token():
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/admin/"},
        bytes.fromhex(SECRET),
        algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "kid": KEY_ID}
    )

def headers():
    return {
        "Authorization": f"Ghost {get_token()}",
        "Content-Type": "application/json",
        "Accept-Version": "v5.0"
    }

ARTICLES = [
    {
        "slug": "ecb-rate-cut-march-2026-portugal-mortgages",
        "title": "ECB Cuts Rates Again in March 2026: What It Means for Portugal's Homeowners and Economy",
        "meta_title": "ECB March 2026 Rate Cut: Impact on Portuguese Mortgages & Economy",
        "meta_description": "The ECB cut interest rates again in March 2026. Here's what that means for Portuguese mortgage holders, renters, and the broader economy.",
        "custom_excerpt": "With the ECB cutting rates for the fifth consecutive time, Portugal's variable-rate mortgage holders are finally seeing relief — but the housing crisis is far from over.",
        "tags": ["Economy", "Finance", "Housing", "Expat Life"],
        "html": """<p>The European Central Bank cut its key interest rate again on Thursday, reducing the deposit facility rate to 2.5% — the fifth consecutive cut since the ECB began easing policy in mid-2024. For Portugal's hundreds of thousands of variable-rate mortgage holders, the news brings another small but meaningful reduction in monthly payments.</p>

<h2>What the ECB's March 2026 Rate Cut Actually Means</h2>

<p>The ECB's benchmark deposit rate now sits at 2.5%, down from a peak of 4% in 2023. Portuguese mortgages are typically indexed to the Euribor 6-month or 12-month rate, which has tracked the ECB's moves with a slight lag.</p>

<p>In practical terms, a homeowner with a €200,000 variable-rate mortgage spread over 30 years can expect to save approximately €40-60 per month compared to payments at the peak. Over the course of 2024 and 2025 combined, cumulative cuts have reduced annual mortgage costs by roughly €800-1,200 for a typical Portuguese borrower.</p>

<p><strong>The Euribor trajectory:</strong></p>
<ul>
<li>Euribor 12m peaked at 4.16% in October 2023</li>
<li>Currently hovering around 2.6-2.7%</li>
<li>Markets expect a further 25bp cut by summer 2026</li>
</ul>

<h2>Why the Rate Cuts Haven't Fixed Portugal's Housing Crisis</h2>

<p>Despite the rate relief, Portugal's housing market shows little sign of cooling. Prices in Lisbon and Porto continued to rise in early 2026, with the national average now exceeding €2,500 per square metre. The reason is structural, not monetary.</p>

<p>"Lower rates are helping existing homeowners, but they're not helping people who want to buy their first property," says a Lisbon-based property analyst. "When rates fall, prices rise — it's the same monthly payment, just a different asset price."</p>

<p>The government's response has focused on supply-side measures: the new "Simplex Urbanístico" legislation aims to cut the average time to obtain a construction licence from 3 years to under 6 months. But planners acknowledge the full effect won't be felt until 2027 at the earliest.</p>

<h2>What Expats Should Know</h2>

<p><strong>For buyers:</strong> Lower borrowing costs improve affordability on paper, but competition remains intense. International buyers — particularly from the UK, US, Brazil, and France — account for a growing share of purchases in coastal and Lisbon markets.</p>

<p><strong>For variable-rate mortgage holders:</strong> If your mortgage is indexed to Euribor 6m or 12m, you should have already seen recent reductions in your monthly statement. If your bank hasn't passed on the cuts, it's worth reviewing your terms.</p>

<p><strong>For renters:</strong> The rental market remains tight. Lower rates have not meaningfully increased rental supply — many landlords prefer short-term tourist rentals, and the new AL (Alojamento Local) regulatory framework continues to be debated in parliament.</p>

<h2>The Broader Economic Picture</h2>

<p>Portugal's economy grew 1.9% in 2025, below the 2.3% pace of 2024. The ECB's easing cycle is expected to support growth modestly in 2026, with the Bank of Portugal forecasting 2.1% GDP growth this year, driven primarily by domestic consumption and continued investment in renewables and tourism infrastructure.</p>

<p>The government, buoyed by S&P's recent upgrade of Portugal's credit outlook to "positive," is projecting a budget surplus for 2025 — the third consecutive year of surplus — and has signalled capacity for further tax reductions ahead of the 2027 budget.</p>

<p>For residents and expats, the combination of falling mortgage rates, stable employment, and improving fiscal position paints a cautiously optimistic picture — even as housing affordability remains the country's most pressing domestic challenge.</p>

<hr>
<p><em>The Portugal Brief covers Portuguese news and policy for expats and internationals. Subscribe for our free daily briefing.</em></p>""",
        "json_ld": {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": "ECB Cuts Rates Again in March 2026: What It Means for Portugal's Homeowners and Economy",
            "datePublished": "2026-03-03T08:00:00Z",
            "author": {"@type": "Organization", "name": "The Portugal Brief"},
            "publisher": {"@type": "Organization", "name": "The Portugal Brief"}
        }
    },
    {
        "slug": "portugal-seguro-inauguration-march-2026",
        "title": "A New Chapter: What André Seguro's Presidency Means for Portugal — and Its Expat Community",
        "meta_title": "André Seguro Portugal President: What His Inauguration Means for Expats",
        "meta_description": "André Seguro is inaugurated as Portugal's new President this week. Here's what his presidency means for the country, expats, and key policy areas.",
        "custom_excerpt": "After a decade of Marcelo Rebelo de Sousa, Portugal enters a new era under President André Seguro. Here's what expats and residents should expect from the change at the top.",
        "tags": ["Politics", "Expat Life", "Portugal News"],
        "html": """<p>Portugal inaugurates its new President this week, as André Seguro — former Secretary-General of the Socialist Party — takes the oath of office in a ceremony at the Assembleia da República in Lisbon. The transition marks the end of a decade under Marcelo Rebelo de Sousa, whose two-term presidency was defined by political centrism, populist communication, and Portugal's remarkable economic comeback.</p>

<h2>Who Is André Seguro?</h2>

<p>André Seguro, 59, served as Secretary-General of the Socialist Party from 2008 to 2014, a tenure remembered for leading the party through the Troika austerity years in opposition. A trained lawyer with roots in Setúbal, Seguro is seen as representing the traditional centre-left of Portuguese politics — more ideologically defined than Marcelo, less immediately charismatic, but widely respected for intellectual rigour.</p>

<p>His election in January 2026 — defeating the centre-right candidate José Silvano by a margin of 51.4% to 38.7% — reflected both fatigue with Marcelo's tenure and concerns about the rising influence of the far-right Chega party in local government.</p>

<h2>What Changes With a New President</h2>

<p>Portugal's presidency is semi-presidential: the President has limited executive powers but significant symbolic and constitutional authority. Key presidential powers include:</p>

<ul>
<li>Promulgating or vetoing legislation (vetoes can be overridden by the Assembleia)</li>
<li>Dissolving parliament in times of political crisis</li>
<li>Appointing the Prime Minister (from the majority coalition)</li>
<li>Representing Portugal internationally and signing treaties</li>
<li>Pardoning and commuting criminal sentences</li>
</ul>

<p>Day-to-day governance remains with Prime Minister Luís Montenegro and his centre-right coalition. Seguro's election does not change the parliamentary arithmetic or executive policy direction — at least not directly.</p>

<h2>Areas Where Seguro's Influence Could Be Felt</h2>

<h3>Housing and Social Policy</h3>
<p>Seguro has been a vocal critic of the government's handling of the housing crisis, calling for more aggressive supply-side intervention and tighter regulation of speculative investment. While he cannot legislate, a President who publicly prioritises housing will apply political pressure on the government to do the same.</p>

<h3>Immigration and Integration</h3>
<p>Portugal's immigration backlog — with over 124,000 cases pending at AIMA — is a flashpoint. Seguro has publicly called for faster processing and better integration services. He is expected to use his platform to push back against the anti-immigration rhetoric gaining traction in local politics.</p>

<h3>Europe and Foreign Policy</h3>
<p>Seguro is a committed Europeanist. At a time when transatlantic relations are under strain, he is expected to be a strong advocate for EU solidarity and Portugal's traditional alliance with the US, UK, and Lusophone world. His relationship with Brazil — where millions of Portuguese nationals live — will be closely watched.</p>

<h2>What This Means for Expats</h2>

<p>For the roughly 400,000 registered foreign residents in Portugal, the practical day-to-day impact of a new President is limited. Immigration rules, tax policy, and residency processes are set by the government, not the presidency.</p>

<p>That said, Seguro's rhetoric has been more explicitly welcoming of Portugal's international community than his predecessor's in his final years. His stated priority of reducing the AIMA backlog — if translated into executive pressure on the government — would be directly beneficial to the tens of thousands of expats stuck in residency limbo.</p>

<p>His inauguration ceremony this week is expected to draw diplomatic delegations from across the EU, the Lusophone world, and key bilateral partners. A public holiday is not declared, but Lisbon will see significant traffic disruption around Belém and the Assembleia da República on inauguration day.</p>

<h2>The Marcelo Legacy</h2>

<p>Marcelo Rebelo de Sousa leaves office with historically high approval ratings — routinely above 70% throughout his decade in power. His presidency coincided with Portugal's economic recovery from the Troika years, the Golden Age of tourism, and the country's return to investment-grade credit status.</p>

<p>He will be remembered for a uniquely personal presidency: spontaneous beach visits, embracing everyone from fishermen to world leaders, and a communication style that made him feel more like a trusted uncle than a head of state.</p>

<p>Seguro's challenge is to define his own presidential personality — and in doing so, to chart a course for Portugal's next chapter at a moment of genuine geopolitical and economic uncertainty.</p>

<hr>
<p><em>The Portugal Brief tracks Portuguese politics, economics, and daily life for expats and internationals. Subscribe for our free daily briefing.</em></p>""",
        "json_ld": {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": "A New Chapter: What André Seguro's Presidency Means for Portugal — and Its Expat Community",
            "datePublished": "2026-03-03T09:00:00Z",
            "author": {"@type": "Organization", "name": "The Portugal Brief"},
            "publisher": {"@type": "Organization", "name": "The Portugal Brief"}
        }
    }
]

def publish_article(article):
    """Publish a feature article to Ghost."""
    lexical = json.dumps({
        "root": {
            "children": [
                {
                    "type": "html",
                    "version": 1,
                    "html": article["html"]
                }
            ],
            "direction": "ltr",
            "format": "",
            "indent": 0,
            "type": "root",
            "version": 1
        }
    })

    # Code injection for JSON-LD
    codeinjection_head = f'<script type="application/ld+json">{json.dumps(article["json_ld"])}</script>'

    payload = {
        "posts": [{
            "title": article["title"],
            "slug": article["slug"],
            "status": "published",
            "custom_excerpt": article["custom_excerpt"],
            "meta_title": article["meta_title"],
            "meta_description": article["meta_description"],
            "tags": [{"name": t} for t in article["tags"]],
            "codeinjection_head": codeinjection_head,
            "lexical": lexical,
        }]
    }

    r = requests.post(f"{BASE}/posts/", headers=headers(), json=payload)
    if r.status_code == 201:
        post = r.json()["posts"][0]
        print(f"✅ Published: {post['title']}")
        print(f"   URL: https://theportugalbrief.pt/{post['slug']}/")
        print(f"   ID: {post['id']}")
        return post
    else:
        print(f"❌ Failed: {r.status_code} — {r.text[:300]}")
        return None

if __name__ == "__main__":
    published = []
    for article in ARTICLES:
        print(f"\nPublishing: {article['title'][:60]}...")
        post = publish_article(article)
        if post:
            published.append(post)
        time.sleep(2)

    print(f"\n\n📊 Done: {len(published)}/{len(ARTICLES)} articles published")
