"""Twitter/X poster using Tweepy."""

import tweepy
import config


def post_to_twitter(text: str):
    """Post a tweet."""
    client = tweepy.Client(
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
    )
    client.create_tweet(text=text)
