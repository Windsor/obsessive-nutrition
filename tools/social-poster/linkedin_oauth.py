#!/usr/bin/env python3
"""
One-time LinkedIn OAuth2 token setup.
Run this locally, follow the URL, paste the redirect code.

Usage:
  python3 linkedin_oauth.py

You'll need LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in your .env
"""

import os
import sys
from urllib.parse import urlencode
from dotenv import load_dotenv
import requests

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8585/callback"

if not CLIENT_ID or not CLIENT_SECRET:
    print("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env first")
    sys.exit(1)

# Step 1: Generate auth URL
params = urlencode({
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": "openid profile w_member_social",
})
auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{params}"

print(f"\n1. Open this URL in your browser:\n\n{auth_url}\n")
print("2. Authorize the app")
print("3. You'll be redirected to a URL like: http://localhost:8585/callback?code=XXXXX")
print("4. Copy the 'code' parameter value and paste it below:\n")

code = input("Authorization code: ").strip()

# Step 2: Exchange code for token
resp = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    timeout=30,
)
resp.raise_for_status()
token_data = resp.json()

access_token = token_data["access_token"]
expires_in = token_data.get("expires_in", "unknown")

print(f"\n✅ Access Token (expires in {expires_in}s):\n{access_token}")

# Step 3: Get person URN
me = requests.get(
    "https://api.linkedin.com/v2/userinfo",
    headers={"Authorization": f"Bearer {access_token}"},
    timeout=30,
)
me.raise_for_status()
sub = me.json().get("sub", "")
print(f"\nPerson URN: urn:li:person:{sub}")
print(f"\nAdd these to your .env:")
print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
print(f"LINKEDIN_PERSON_URN=urn:li:person:{sub}")
