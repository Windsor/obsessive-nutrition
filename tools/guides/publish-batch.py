#!/usr/bin/env python3
"""Batch publish markdown guides to Ghost as drafts."""
import jwt, time, json, requests, re, sys, os

GHOST_URL = "https://theportugalbrief.pt"
ADMIN_KEY = "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"

def get_token():
    key_id, secret = ADMIN_KEY.split(":")
    iat = int(time.time())
    return jwt.encode(
        {"iat": iat, "exp": iat + 300, "aud": "/admin/"},
        bytes.fromhex(secret), algorithm="HS256",
        headers={"alg": "HS256", "typ": "JWT", "kid": key_id}
    )

def md_to_mobiledoc(md_content):
    """Convert markdown to mobiledoc card format."""
    return json.dumps({
        "version": "0.3.1",
        "markups": [],
        "atoms": [],
        "cards": [["markdown", {"markdown": md_content}]],
        "sections": [[10, 0]]
    })

GUIDES = [
    {
        "file": "nhr-tax-portugal-2026.md",
        "title": "NHR Tax Regime in Portugal 2026: Complete Guide for Expats",
        "slug": "nhr-tax-portugal-2026",
        "excerpt": "Portugal's NHR tax regime ended for new applicants in 2024. Learn about the replacement IFICI program, current tax rates, and what it means for expats and retirees.",
        "tags": ["Guides", "Tax", "Expat Life", "NHR", "Finance"],
        "meta_title": "NHR Tax Portugal 2026: Complete Guide | IFICI Replacement Explained",
        "meta_description": "Portugal NHR tax regime guide 2026. IFICI replacement program, tax rates, pension taxation, deductions, and expert advice for expats and retirees."
    },
    {
        "file": "healthcare-portugal-2026.md",
        "slug": "healthcare-portugal-2026",
        "title": "Healthcare in Portugal 2026: Complete Guide for Expats",
        "excerpt": "Everything expats need to know about Portuguese healthcare — public SNS, private hospitals, insurance, costs, pharmacies, and how to register.",
        "tags": ["Guides", "Healthcare", "Expat Life", "Living in Portugal"],
        "meta_title": "Healthcare in Portugal 2026: Expat Guide to Public & Private Care",
        "meta_description": "Complete guide to healthcare in Portugal for expats. SNS registration, private hospitals, insurance costs, pharmacies, dental care, and emergency services."
    },
    {
        "file": "retiring-portugal-2026.md",
        "slug": "retiring-portugal-2026",
        "title": "Retiring in Portugal 2026: Complete Guide",
        "excerpt": "Why Portugal is one of the best places to retire. Visa options, best locations, cost of living, healthcare, taxes, and practical steps to make it happen.",
        "tags": ["Guides", "Retirement", "Expat Life", "D7 Visa", "Living in Portugal"],
        "meta_title": "Retiring in Portugal 2026: The Complete Expat Guide",
        "meta_description": "Retire in Portugal 2026: visa options, best places (Algarve, Lisbon, Porto), cost of living, healthcare, taxes, and step-by-step guide for expat retirees."
    },
    {
        "file": "real-estate-portugal-2026.md",
        "slug": "real-estate-portugal-2026",
        "title": "Portugal Real Estate Market 2026: What Expats Need to Know",
        "excerpt": "Portugal property market overview — prices by region, buying process, costs, mortgages for foreigners, rental market, and investment opportunities.",
        "tags": ["Guides", "Real Estate", "Property", "Investment", "Expat Life"],
        "meta_title": "Portugal Real Estate 2026: Prices, Buying Guide & Market Trends",
        "meta_description": "Portugal real estate guide 2026. Property prices by region, buying process, IMT tax, mortgages for foreigners, rental market trends, and investment yields."
    },
    {
        "file": "portugal-taxes-2026.md",
        "slug": "portugal-taxes-2026",
        "title": "Portugal Taxes 2026: Complete Guide for Expats and Residents",
        "excerpt": "Complete overview of Portuguese taxes — income tax rates, capital gains, property taxes, VAT, self-employment, and tax tips for expats.",
        "tags": ["Guides", "Tax", "Finance", "Expat Life"],
        "meta_title": "Portugal Tax Guide 2026: Income Tax, Capital Gains, Property & VAT",
        "meta_description": "Portugal tax guide 2026. IRS income tax brackets, capital gains, IMI property tax, VAT rates, self-employment tax, deductions, and filing deadlines."
    },
    {
        "file": "residency-permit-portugal-2026.md",
        "slug": "residency-permit-portugal-2026",
        "title": "Portugal Residency Permit 2026: Complete Guide",
        "excerpt": "All visa types explained — D7, D8, D1, D2, Golden Visa, family reunification. Application process, renewals, and path to permanent residency and citizenship.",
        "tags": ["Guides", "Immigration", "Visa", "Residency", "Expat Life"],
        "meta_title": "Portugal Residency Permit 2026: Visa Types, Process & Citizenship Path",
        "meta_description": "Portugal residency guide 2026. D7, D8 digital nomad, Golden Visa, work permits. Application process, AIMA, renewals, permanent residency, and citizenship."
    }
]

def publish_guide(guide):
    guide_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(guide_dir, guide["file"]), "r") as f:
        content = f.read()
    
    # Remove the H1 title (first line) from content since Ghost uses its own title
    lines = content.strip().split("\n")
    if lines[0].startswith("# "):
        content = "\n".join(lines[1:]).strip()
    
    post = {
        "posts": [{
            "title": guide["title"],
            "slug": guide["slug"],
            "mobiledoc": md_to_mobiledoc(content),
            "status": "draft",
            "tags": [{"name": t} for t in guide["tags"]],
            "custom_excerpt": guide["excerpt"],
            "meta_title": guide["meta_title"],
            "meta_description": guide["meta_description"],
        }]
    }
    
    token = get_token()
    r = requests.post(
        f"{GHOST_URL}/ghost/api/admin/posts/",
        json=post,
        headers={"Authorization": f"Ghost {token}"}
    )
    
    if r.status_code == 201:
        data = r.json()["posts"][0]
        print(f"✅ {guide['title']} → /{data['slug']}/ (draft)")
        return True
    else:
        print(f"❌ {guide['title']}: {r.status_code} — {r.text[:200]}")
        return False

if __name__ == "__main__":
    success = 0
    for g in GUIDES:
        if publish_guide(g):
            success += 1
    print(f"\nPublished {success}/{len(GUIDES)} guides as drafts")
