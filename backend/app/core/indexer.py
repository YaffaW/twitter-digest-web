"""Lightweight indexer using SQLite + FTS5 for local testing.

Provides functions to initialize DB and upsert tweet records and simple search.
"""
import sqlite3
import threading
from typing import Optional, List, Dict
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'index.db')
_DB_LOCK = threading.Lock()


def _ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # main table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id TEXT PRIMARY KEY,
        url TEXT,
        author TEXT,
        author_name TEXT,
        text TEXT,
        likes INTEGER,
        retweets INTEGER,
        replies INTEGER,
        created_at TEXT,
        meme_score REAL
    )
    ''')
    # FTS table for text search
    cur.execute('CREATE VIRTUAL TABLE IF NOT EXISTS tweets_fts USING fts5(id, text, author, content="")')
    conn.commit()
    conn.close()


def upsert_tweet(tweet: Dict):
    """Insert or update a tweet into the index."""
    _ensure_db()
    with _DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO tweets (id, url, author, author_name, text, likes, retweets, replies, created_at, meme_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            url=excluded.url,
            author=excluded.author,
            author_name=excluded.author_name,
            text=excluded.text,
            likes=excluded.likes,
            retweets=excluded.retweets,
            replies=excluded.replies,
            created_at=excluded.created_at,
            meme_score=excluded.meme_score
        ''', (
            tweet.get('id'), tweet.get('url'), tweet.get('author'), tweet.get('author_name'), tweet.get('text'),
            tweet.get('likes', 0), tweet.get('retweets', 0), tweet.get('replies', 0), tweet.get('created_at', ''), tweet.get('meme_score')
        ))
        # update FTS
        cur.execute('DELETE FROM tweets_fts WHERE id=?', (tweet.get('id'),))
        cur.execute('INSERT INTO tweets_fts (id, text, author) VALUES (?, ?, ?)', (tweet.get('id'), tweet.get('text'), tweet.get('author')))
        conn.commit()
        conn.close()


def search_text(q: str, limit: int = 20) -> List[Dict]:
    _ensure_db()
    with _DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
        SELECT t.id, t.url, t.author, t.author_name, t.text, t.likes, t.retweets, t.replies, t.created_at, t.meme_score
        FROM tweets t JOIN tweets_fts f ON t.id = f.id
        WHERE tweets_fts MATCH ?
        ORDER BY t.likes + t.retweets DESC
        LIMIT ?
        ''', (q, limit))
        rows = cur.fetchall()
        conn.close()
    res = []
    for r in rows:
        res.append({
            'id': r[0], 'url': r[1], 'author': r[2], 'author_name': r[3], 'text': r[4],
            'likes': r[5], 'retweets': r[6], 'replies': r[7], 'created_at': r[8], 'meme_score': r[9]
        })
    return res
