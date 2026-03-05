"""Bluesky poster using AT Protocol SDK."""

from atproto import Client, client_utils
import config


def post_to_bluesky(text: str, url: str, image_url: str = None):
    """Post to Bluesky with link card."""
    client = Client()
    client.login(config.BLUESKY_HANDLE, config.BLUESKY_APP_PASSWORD)

    # Build text with embedded link
    # Use TextBuilder for rich text with link facets
    tb = client_utils.TextBuilder()

    # Split text to embed the URL as a clickable link
    if url and "🔗 " in text:
        before_link = text.split("🔗 ")[0]
        after_url_parts = text.split(url)
        after_link = after_url_parts[1] if len(after_url_parts) > 1 else ""

        tb.text(before_link + "🔗 ")
        tb.link(url, url)
        tb.text(after_link)
    else:
        tb.text(text)

    # Create external embed (link card) if possible
    embed = None
    try:
        from atproto import models
        embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=url,
                title=text.split("\n")[0].replace("📰 ", ""),
                description=text.split("\n\n")[1] if "\n\n" in text else "",
            )
        )
    except Exception:
        pass  # Post without embed card if it fails

    client.send_post(tb, embed=embed)
