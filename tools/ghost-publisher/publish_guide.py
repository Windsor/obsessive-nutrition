#!/usr/bin/env python3
"""
Publish evergreen guides to The Portugal Brief Ghost CMS.
Reads markdown guides, converts to HTML, adds SEO metadata, and publishes as draft.
Designed to batch-publish when r2d2 comes back online.
"""

import json
import hashlib
import hmac
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# Ghost Admin API config
GHOST_URL = "https://theportugalbrief.pt"
ADMIN_KEY = "6995cfb23337d1ed52cfff32:9e00c393663db42dd8fd1f6641b6042b18469e8ff38ec089920d605ba93b0ad4"

GUIDES_DIR = Path(__file__).parent.parent.parent / "projects" / "portugal-news" / "guides"


def make_token():
    """Create Ghost Admin API JWT token."""
    key_id, secret = ADMIN_KEY.split(":")
    
    import base64
    
    # Header
    header = base64.urlsafe_b64encode(json.dumps({
        "alg": "HS256", "typ": "JWT", "kid": key_id
    }).encode()).rstrip(b"=").decode()
    
    # Payload
    iat = int(time.time())
    payload = base64.urlsafe_b64encode(json.dumps({
        "iat": iat, "exp": iat + 300, "aud": "/admin/"
    }).encode()).rstrip(b"=").decode()
    
    # Sign
    signing_input = f"{header}.{payload}".encode()
    signature = hmac.new(
        bytes.fromhex(secret), signing_input, hashlib.sha256
    ).digest()
    sig = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    
    return f"{header}.{payload}.{sig}"


def md_to_mobiledoc(md_content):
    """Convert markdown content to Ghost mobiledoc (using HTML card)."""
    html = md_to_html(md_content)
    mobiledoc = {
        "version": "0.3.1",
        "atoms": [],
        "cards": [["html", {"html": html}]],
        "markups": [],
        "sections": [[10, 0]]
    }
    return json.dumps(mobiledoc)


def md_to_html(md):
    """Basic markdown to HTML conversion for guides."""
    lines = md.split("\n")
    html_parts = []
    in_table = False
    in_list = False
    table_rows = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip metadata block (frontmatter-like headers)
        if stripped.startswith("**Meta description:") or stripped.startswith("**Primary keyword:") or \
           stripped.startswith("**Secondary:") or stripped.startswith("**Tags:") or \
           stripped.startswith("**Excerpt:"):
            continue
        
        # Horizontal rule
        if stripped == "---":
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append("<hr>")
            continue
        
        # Headers
        if stripped.startswith("# "):
            continue  # Skip H1, Ghost uses title field
        if stripped.startswith("## "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h2>{stripped[3:]}</h2>")
            continue
        if stripped.startswith("### "):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<h3>{stripped[4:]}</h3>")
            continue
        
        # Table
        if "|" in stripped and stripped.startswith("|"):
            if not in_table:
                in_table = True
                table_rows = []
            # Skip separator rows
            if re.match(r"^\|[\s\-|]+\|$", stripped):
                continue
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            table_rows.append(cells)
            continue
        elif in_table:
            # End of table
            if table_rows:
                html_parts.append("<table>")
                html_parts.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in table_rows[0]) + "</tr></thead>")
                html_parts.append("<tbody>")
                for row in table_rows[1:]:
                    html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
                html_parts.append("</tbody></table>")
            table_rows = []
            in_table = False
        
        # Unordered list
        if stripped.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            content = stripped[2:]
            # Handle bold
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            # Handle links
            content = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', content)
            html_parts.append(f"<li>{content}</li>")
            continue
        elif in_list and not stripped.startswith("- "):
            html_parts.append("</ul>")
            in_list = False
        
        # Empty line
        if not stripped:
            continue
        
        # Regular paragraph
        content = stripped
        content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
        content = re.sub(r"\*(.+?)\*", r"<em>\1</em>", content)
        content = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', content)
        html_parts.append(f"<p>{content}</p>")
    
    # Close any open elements
    if in_list:
        html_parts.append("</ul>")
    if in_table and table_rows:
        html_parts.append("<table>")
        html_parts.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in table_rows[0]) + "</tr></thead>")
        html_parts.append("<tbody>")
        for row in table_rows[1:]:
            html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
        html_parts.append("</tbody></table>")
    
    return "\n".join(html_parts)


def parse_guide(filepath):
    """Parse guide markdown file and extract metadata."""
    content = filepath.read_text()
    lines = content.split("\n")
    
    meta = {}
    body_start = 0
    
    for i, line in enumerate(lines):
        if line.startswith("# "):
            meta["title"] = line[2:].strip()
        elif line.startswith("**Meta description:**"):
            meta["meta_description"] = line.split("**Meta description:**")[1].strip()
        elif line.startswith("**Primary keyword:**"):
            meta["primary_keyword"] = line.split("**Primary keyword:**")[1].strip()
        elif line.startswith("**Tags:**"):
            meta["tags"] = [t.strip() for t in line.split("**Tags:**")[1].split(",")]
        elif line.startswith("**Excerpt:**"):
            meta["excerpt"] = line.split("**Excerpt:**")[1].strip()
        elif line.strip() == "---" and i > 5:
            body_start = i + 1
            break
    
    body = "\n".join(lines[body_start:])
    meta["body"] = body
    meta["slug"] = filepath.stem
    
    return meta


def create_post(meta, status="draft"):
    """Create a Ghost post via Admin API."""
    token = make_token()
    
    post_data = {
        "posts": [{
            "title": meta["title"],
            "slug": meta["slug"],
            "mobiledoc": md_to_mobiledoc(meta["body"]),
            "status": status,
            "tags": [{"name": tag} for tag in meta.get("tags", [])],
            "meta_title": meta.get("title", ""),
            "meta_description": meta.get("meta_description", ""),
            "custom_excerpt": meta.get("excerpt", ""),
        }]
    }
    
    req = urllib.request.Request(
        f"{GHOST_URL}/ghost/api/admin/posts/?source=html",
        data=json.dumps(post_data).encode(),
        headers={
            "Authorization": f"Ghost {token}",
            "Content-Type": "application/json",
        },
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            post = result["posts"][0]
            print(f"  ✅ Published: {post['title']} → {GHOST_URL}/{post['slug']}/")
            return post
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None


def main():
    guides = sorted(GUIDES_DIR.glob("*.md"))
    
    if not guides:
        print("No guides found in", GUIDES_DIR)
        return
    
    print(f"Found {len(guides)} guides in {GUIDES_DIR}\n")
    
    if "--publish" in sys.argv:
        for guide_path in guides:
            print(f"Publishing: {guide_path.name}")
            meta = parse_guide(guide_path)
            create_post(meta, status="draft")
            print()
    else:
        for guide_path in guides:
            meta = parse_guide(guide_path)
            print(f"  📝 {meta.get('title', guide_path.stem)}")
            print(f"     Slug: {meta.get('slug')}")
            print(f"     Tags: {', '.join(meta.get('tags', []))}")
            print(f"     Meta: {meta.get('meta_description', 'N/A')[:80]}...")
            print()
        print("Run with --publish to publish all as drafts to Ghost.")


if __name__ == "__main__":
    main()
