"""Twitter search and data fetching module."""

import logging
import re
import warnings
import contextlib
import os
from typing import Optional

import requests
from ddgs import DDGS

logger = logging.getLogger("twitter_fetcher")


def search_tweets(query: str, max_results: int = 20) -> list[str]:
    """Search DuckDuckGo for X/Twitter URLs matching the query."""
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


def search_and_fetch(
    queries: list[str],
    max_results_per_query: int = 20,
    min_likes: int = 3,
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

    # Filter by minimum engagement
    tweets = [t for t in tweets if t["likes"] >= min_likes]
    logger.info(f"After filtering (min {min_likes} likes): {len(tweets)} tweets")

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
