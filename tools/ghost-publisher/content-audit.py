#!/usr/bin/env python3
"""Ghost Content Audit - checks for missing SEO fields, images, tags etc."""
import requests, re, sys
from html import unescape

CONTENT_API = 'https://theportugalbrief.pt/ghost/api/content'
CONTENT_KEY = '572ac18cd3e84202174908842b'

def audit():
    posts = []
    page = 1
    while True:
        r = requests.get(f'{CONTENT_API}/posts/?key={CONTENT_KEY}&include=tags&limit=50&page={page}&fields=id,title,slug,feature_image,meta_description,custom_excerpt,published_at')
        data = r.json()
        posts.extend(data['posts'])
        if not data.get('meta',{}).get('pagination',{}).get('next'): break
        page += 1

    issues = {
        'no_image': [p for p in posts if not p.get('feature_image')],
        'no_meta': [p for p in posts if not p.get('meta_description')],
        'no_excerpt': [p for p in posts if not p.get('custom_excerpt')],
        'no_tags': [p for p in posts if not p.get('tags')],
    }

    print(f'=== Ghost Content Audit ({len(posts)} posts) ===')
    all_good = True
    for label, items in issues.items():
        if items:
            all_good = False
            print(f'\n⚠ {label.replace("_"," ").title()}: {len(items)}')
            for p in items[:10]:
                print(f'  - {p["title"][:70]}')
    
    if all_good:
        print('✅ All posts have images, meta descriptions, excerpts, and tags')
    
    return 0 if all_good else 1

if __name__ == '__main__':
    sys.exit(audit())
