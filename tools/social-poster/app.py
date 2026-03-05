#!/usr/bin/env python3
"""
Social Auto-Poster for The Portugal Brief
Receives Ghost webhooks on post.published, posts to social platforms.
"""

import json
import logging
import html
import re
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

import config
from posters.bluesky import post_to_bluesky
from posters.twitter import post_to_twitter
from posters.linkedin import post_to_linkedin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("social-poster")

app = Flask(__name__)


def extract_summary(html_content: str, max_chars: int = 200) -> str:
    """Extract first 1-2 sentences from Ghost HTML content."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Get text from first few paragraphs
    paragraphs = soup.find_all("p")
    text = ""
    for p in paragraphs[:3]:
        t = p.get_text(strip=True)
        if t:
            text = t
            break
    if not text:
        text = soup.get_text(strip=True)

    # Truncate to ~2 sentences or max_chars
    sentences = re.split(r'(?<=[.!?])\s+', text)
    summary = ""
    for s in sentences[:2]:
        if len(summary) + len(s) > max_chars:
            break
        summary += s + " "
    return summary.strip() or text[:max_chars]


def fetch_post_data(post_data: dict) -> dict:
    """Extract what we need from the Ghost webhook payload."""
    post = post_data.get("post", {}).get("current", {})
    if not post:
        # Try alternative payload structures
        post = post_data.get("post", post_data)

    title = post.get("title", "")
    url = post.get("url", "")
    custom_excerpt = post.get("custom_excerpt", "")
    html_content = post.get("html", "")
    feature_image = post.get("feature_image", "")

    # Use custom excerpt if available, otherwise extract from content
    summary = custom_excerpt if custom_excerpt else extract_summary(html_content)

    # Ensure URL is absolute
    if url and not url.startswith("http"):
        url = config.GHOST_URL.rstrip("/") + url

    return {
        "title": title,
        "url": url,
        "summary": summary,
        "feature_image": feature_image,
    }


def format_post(data: dict, max_chars: int = 300) -> str:
    """Format the social media post text."""
    title = data["title"]
    summary = data["summary"]
    url = data["url"]
    hashtags = config.DEFAULT_HASHTAGS

    # Build the post
    post = f"📰 {title}\n\n{summary}\n\n🔗 {url}\n\n{hashtags}"

    # Truncate if needed (preserve URL and hashtags)
    if len(post) > max_chars:
        # Shorten summary
        overhead = len(f"📰 {title}\n\n\n\n🔗 {url}\n\n{hashtags}")
        available = max_chars - overhead - 3  # for "..."
        if available > 20:
            short_summary = summary[:available] + "..."
        else:
            short_summary = ""
        post = f"📰 {title}\n\n{short_summary}\n\n🔗 {url}\n\n{hashtags}"

    return post


@app.route("/webhook/ghost", methods=["POST"])
def ghost_webhook():
    """Handle Ghost post.published webhook."""
    try:
        payload = request.get_json(force=True)
        log.info(f"Received webhook: {json.dumps(payload)[:500]}")

        data = fetch_post_data(payload)
        if not data["title"] or not data["url"]:
            log.warning("Missing title or URL in webhook payload")
            return jsonify({"error": "missing data"}), 400

        log.info(f"Processing: {data['title']} -> {data['url']}")

        results = {}

        # Post to Bluesky
        if config.BLUESKY_HANDLE and config.BLUESKY_APP_PASSWORD:
            try:
                text = format_post(data, max_chars=300)
                post_to_bluesky(text, data["url"], data.get("feature_image"))
                results["bluesky"] = "ok"
                log.info("✅ Posted to Bluesky")
            except Exception as e:
                results["bluesky"] = f"error: {e}"
                log.error(f"❌ Bluesky failed: {e}")

        # Post to Twitter
        if config.TWITTER_API_KEY and config.TWITTER_ACCESS_TOKEN:
            try:
                text = format_post(data, max_chars=280)
                post_to_twitter(text)
                results["twitter"] = "ok"
                log.info("✅ Posted to Twitter")
            except Exception as e:
                results["twitter"] = f"error: {e}"
                log.error(f"❌ Twitter failed: {e}")

        # Post to LinkedIn
        if config.LINKEDIN_ACCESS_TOKEN and config.LINKEDIN_PERSON_URN:
            try:
                text = format_post(data, max_chars=3000)
                post_to_linkedin(text, data["url"], data["title"], data.get("feature_image"))
                results["linkedin"] = "ok"
                log.info("✅ Posted to LinkedIn")
            except Exception as e:
                results["linkedin"] = f"error: {e}"
                log.error(f"❌ LinkedIn failed: {e}")

        return jsonify({"status": "ok", "results": results}), 200

    except Exception as e:
        log.error(f"Webhook handler error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    platforms = []
    if config.BLUESKY_HANDLE:
        platforms.append("bluesky")
    if config.TWITTER_API_KEY:
        platforms.append("twitter")
    if config.LINKEDIN_ACCESS_TOKEN:
        platforms.append("linkedin")
    return jsonify({"status": "ok", "platforms": platforms})


if __name__ == "__main__":
    log.info(f"Starting Social Poster on port {config.LISTEN_PORT}")
    app.run(host="127.0.0.1", port=config.LISTEN_PORT, debug=False)
