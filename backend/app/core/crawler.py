"""Scheduled crawler that periodically fetches configured accounts and queries.

Uses twitter_fetcher to fetch tweets and indexer to store them.
"""
import time
import threading
from typing import List
from . import twitter_fetcher, indexer
import yaml
import os
import logging

logger = logging.getLogger('crawler')

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def crawl_once(accounts: List[str], queries: List[str], max_per: int = 20):
    results = []
    # Fetch per-account timelines
    for a in accounts:
        q = f'from:{a}'
        try:
            tweets = twitter_fetcher.search_and_fetch([q], max_results_per_query=max_per, min_likes=0, min_text_length=0, time_window_hours=24, use_x_search=True)
            for t in tweets:
                indexer.upsert_tweet(t)
            results.extend(tweets)
        except Exception as e:
            logger.exception(f'Failed to crawl account {a}: {e}')

    # Fetch for generic queries/hashtags
    for q in queries:
        try:
            tweets = twitter_fetcher.search_and_fetch([q], max_results_per_query=max_per, min_likes=0, min_text_length=0, time_window_hours=24, use_x_search=True)
            for t in tweets:
                indexer.upsert_tweet(t)
            results.extend(tweets)
        except Exception as e:
            logger.exception(f'Failed to crawl query {q}: {e}')

    return results


def run_scheduler(poll_interval: int = 60):
    cfg = load_config()
    accounts = cfg.get('accounts', [])
    queries = cfg.get('queries', [])

    logger.info(f'Starting crawler: accounts={len(accounts)} queries={len(queries)} interval={poll_interval}s')

    while True:
        try:
            crawl_once(accounts, queries, max_per=cfg.get('max_per', 20))
        except Exception as e:
            logger.exception(f'Crawler run failed: {e}')
        time.sleep(poll_interval)


def start_in_thread(poll_interval: int = 60):
    t = threading.Thread(target=run_scheduler, args=(poll_interval,), daemon=True)
    t.start()
    return t
