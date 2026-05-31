"""Twitter search and data fetching module."""

import logging
import re
import warnings
import contextlib
import os
from typing import Optional
from datetime import datetime, timedelta

import requests
from ddgs import DDGS

logger = logging.getLogger("twitter_fetcher")


def search_tweets(query: str, max_results: int = 20) -> list[str]:
    """Search DuckDuckGo for X (x.com) tweet URLs matching the query.

    Note: intentionally restricts searches to x.com only per user request.
    """
    full_query = f"site:x.com {query}"
    urls = []
    try:
        with warnings.catch_warnings(), open(os.devnull, "w") as devnull, contextlib.redirect_stderr(devnull):
            warnings.simplefilter("ignore")
            results = DDGS().text(full_query, max_results=max_results, timelimit="d")
        for r in results:
            href = r.get("href", "")
            if "x.com" in href and "/status/" in href:
                urls.append(href)
    except Exception as e:
        logger.error(f"Search failed: {e}")

    logger.info(f"Found {len(urls)} tweet URLs for query: {query[:60]}...")
    return urls


def extract_tweet_id(url: str) -> Optional[str]:
    """Extract tweet ID from an x.com or twitter.com URL."""
    m = re.search(r"(?:x\.com|twitter\.com)/\w+/status/(\d+)", url)
    return m.group(1) if m else None


def extract_username(url: str) -> Optional[str]:
    """Extract username from a tweet URL."""
    m = re.search(r"(?:x\.com|twitter\.com)/(\w+)/status/", url)
    return m.group(1) if m else None


def fetch_tweet(url: str) -> Optional[dict]:
    """Fetch tweet data from fxtwitter API."""
    username = extract_username(url)
    tweet_id = extract_tweet_id(url)
    if not tweet_id or not username:
        return None

    api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"
    try:
        resp = requests.get(api_url, timeout=15)
        if resp.status_code != 200:
            return None
        data = resp.json()
        tweet = data.get("tweet")
        if not tweet:
            return None
        author = tweet.get("author") or {}
        return {
            "id": tweet_id,
            "url": url,
            "author": author.get("screen_name", username),
            "author_name": author.get("name", ""),
            "text": tweet.get("text", ""),
            "likes": tweet.get("likes", 0),
            "retweets": tweet.get("retweets", 0),
            "replies": tweet.get("replies", 0),
            "created_at": tweet.get("created_at", ""),
        }
    except Exception as e:
        logger.warning(f"Failed to fetch tweet {tweet_id}: {e}")
        return None


def fetch_replies(tweet_id: str, username: str) -> list[dict]:
    """Fetch thread/conversation content for a tweet via fxtwitter."""
    api_url = f"https://api.fxtwitter.com/{username}/status/{tweet_id}"
    try:
        resp = requests.get(api_url, timeout=15)
        if resp.status_code != 200:
            return []
        data = resp.json()
        tweet = data.get("tweet") or {}
        thread = tweet.get("thread") or []
        replies = []
        for reply in thread:
            author = reply.get("author") or {}
            replies.append({
                "author": author.get("screen_name", ""),
                "text": reply.get("text", ""),
            })
        return replies
    except Exception as e:
        logger.warning(f"Failed to fetch replies for {tweet_id}: {e}")
        return []


def is_within_hours(timestamp_str: str, hours: int) -> bool:
    """Check if a tweet timestamp is within the last `hours` hours.

    Returns False when timestamp is missing or unparseable.
    """
    try:
        if not timestamp_str:
            return False

        # Try parsing ISO format with timezone (2024-05-31T12:30:45Z)
        if 'T' in timestamp_str and 'Z' in timestamp_str:
            tweet_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            # Fallback: try common formats and Twitter-style strings
            for fmt in [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%a %b %d %H:%M:%S %z %Y',
            ]:
                try:
                    tweet_time = datetime.strptime(timestamp_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                logger.warning(f"Unable to parse timestamp: {timestamp_str}")
                return False

        # Make tweet_time timezone-aware if it isn't
        if tweet_time.tzinfo is None:
            tweet_time = tweet_time.replace(tzinfo=None)
            now = datetime.utcnow()
        else:
            now = datetime.now(tweet_time.tzinfo)

        return (now - tweet_time) <= timedelta(hours=hours)
    except Exception as e:
        logger.warning(f"Error parsing timestamp {timestamp_str}: {e}")
        return False


def is_within_24_hours(timestamp_str: str) -> bool:
    """Backward-compatible helper for 24-hour window."""
    return is_within_hours(timestamp_str, 24)


def search_and_fetch(
    queries: list[str],
    max_results_per_query: int = 20,
    min_likes: int = 3,
    min_text_length: int = 0,
    time_window_hours: int = 24,
    fetch_replies_flag: bool = True,
    max_tweets: int = 30,
) -> list[dict]:
    """
    Search for tweets, fetch their data, filter, and return sorted results.
    """
    # Search for tweet URLs
    all_urls = []
    for q in queries:
        all_urls.extend(search_tweets(q, max_results_per_query))

    # Deduplicate by tweet ID
    seen_ids = set()
    unique_urls = []
    for url in all_urls:
        tid = extract_tweet_id(url)
        if tid and tid not in seen_ids:
            seen_ids.add(tid)
            unique_urls.append(url)
    logger.info(f"Unique tweet URLs: {len(unique_urls)}")

    # Fetch tweet content
    tweets = []
    for url in unique_urls:
        tweet = fetch_tweet(url)
        if tweet:
            tweets.append(tweet)

    logger.info(f"Fetched {len(tweets)} tweets successfully")

    # Filter by minimum engagement, text length, and time
    filter_msg = f"min {min_likes} likes, min {min_text_length} chars"
    if time_window_hours and time_window_hours > 0:
        tweets = [
            t for t in tweets 
            if t["likes"] >= min_likes 
            and len(t["text"]) >= min_text_length 
            and is_within_hours(t.get("created_at", ""), time_window_hours)
        ]
        filter_msg += f", within {time_window_hours} hours"
    else:
        tweets = [t for t in tweets if t["likes"] >= min_likes and len(t["text"]) >= min_text_length]
    
    logger.info(f"After filtering ({filter_msg}): {len(tweets)} tweets")

    if not tweets:
        return []

    # Sort by engagement (likes + retweets)
    tweets.sort(key=lambda t: t["likes"] + t["retweets"], reverse=True)
    tweets = tweets[:max_tweets]

    # Fetch replies for top posts
    if fetch_replies_flag:
        for t in tweets[:10]:
            replies = fetch_replies(t["id"], t["author"])
            if replies:
                t["reply_texts"] = replies
                logger.info(f"Fetched {len(replies)} replies for tweet {t['id']}")

    return tweets
