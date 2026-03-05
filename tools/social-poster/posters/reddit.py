"""Reddit poster using PRAW (Python Reddit API Wrapper).

Cross-posts Portugal Brief articles to relevant subreddits.
Requires Reddit app credentials (script type) — see:
https://www.reddit.com/prefs/apps/

Config env vars:
  REDDIT_CLIENT_ID
  REDDIT_CLIENT_SECRET
  REDDIT_USERNAME
  REDDIT_PASSWORD
  REDDIT_USER_AGENT (optional, defaults to "ThePortugalBrief/1.0")
"""

import time
import config

# Subreddit targets with posting rules
SUBREDDITS = {
    "portugal": {
        "flair": None,  # Check available flairs on first post
        "min_interval_hours": 24,  # Max 1 post/day to avoid spam
        "link_post": True,  # Submit as link post (not text)
    },
    "PortugalExpats": {
        "flair": None,
        "min_interval_hours": 12,
        "link_post": True,
    },
    # Add more as we grow:
    # "europe": {"flair": None, "min_interval_hours": 48, "link_post": True},
    # "eupersonalfinance": for finance articles
}

# Tag-to-subreddit mapping — only post to relevant subs based on article tags
TAG_SUBREDDIT_MAP = {
    "politics": ["portugal"],
    "economy": ["portugal", "PortugalExpats"],
    "housing": ["portugal", "PortugalExpats"],
    "expat-life": ["PortugalExpats"],
    "guides": ["PortugalExpats"],
    "technology": ["portugal"],
    "culture": ["portugal"],
    "business": ["portugal", "PortugalExpats"],
    "daily-briefing": ["portugal"],  # Morning briefings
}

# State tracking (in-memory, reset on restart — persistent state via social-poster's dedup)
_last_post_times = {}


def _get_client():
    """Create authenticated Reddit client."""
    import praw
    return praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        username=config.REDDIT_USERNAME,
        password=config.REDDIT_PASSWORD,
        user_agent=getattr(config, "REDDIT_USER_AGENT", "ThePortugalBrief/1.0"),
    )


def _get_target_subreddits(tags: list) -> list:
    """Determine which subreddits to post to based on article tags."""
    targets = set()
    for tag in (tags or []):
        tag_slug = tag.lower().replace(" ", "-")
        if tag_slug in TAG_SUBREDDIT_MAP:
            targets.update(TAG_SUBREDDIT_MAP[tag_slug])

    # Default: post to portugal if no specific match
    if not targets:
        targets.add("portugal")

    return list(targets)


def _check_rate_limit(subreddit: str) -> bool:
    """Check if we're within rate limits for this subreddit."""
    key = subreddit.lower()
    if key not in _last_post_times:
        return True

    config_sub = SUBREDDITS.get(key, {})
    min_interval = config_sub.get("min_interval_hours", 24) * 3600
    elapsed = time.time() - _last_post_times[key]
    return elapsed >= min_interval


def post_to_reddit(title: str, url: str, tags: list = None, text: str = None):
    """
    Cross-post article to relevant subreddits.

    Args:
        title: Article title (used as Reddit post title)
        url: Article URL
        tags: List of article tag names (determines subreddit targeting)
        text: Optional selftext body (used if link_post=False)

    Returns:
        list of dicts with posting results per subreddit
    """
    if not getattr(config, "REDDIT_CLIENT_ID", ""):
        return [{"subreddit": "all", "status": "skipped", "reason": "no credentials"}]

    targets = _get_target_subreddits(tags)
    results = []

    try:
        reddit = _get_client()
    except Exception as e:
        return [{"subreddit": "all", "status": "error", "reason": str(e)}]

    for sub_name in targets:
        if not _check_rate_limit(sub_name):
            results.append({
                "subreddit": sub_name,
                "status": "skipped",
                "reason": "rate limited"
            })
            continue

        sub_config = SUBREDDITS.get(sub_name, {"link_post": True})

        try:
            subreddit = reddit.subreddit(sub_name)

            if sub_config.get("link_post", True):
                submission = subreddit.submit(
                    title=title,
                    url=url,
                    resubmit=False,  # Don't repost same URL
                )
            else:
                body = text or f"Read the full article: {url}"
                submission = subreddit.submit(
                    title=title,
                    selftext=body,
                )

            _last_post_times[sub_name.lower()] = time.time()
            results.append({
                "subreddit": sub_name,
                "status": "posted",
                "url": f"https://reddit.com{submission.permalink}",
                "id": submission.id,
            })

            # Small delay between subreddit posts to be nice
            time.sleep(2)

        except Exception as e:
            error_msg = str(e)
            results.append({
                "subreddit": sub_name,
                "status": "error",
                "reason": error_msg,
            })

    return results
