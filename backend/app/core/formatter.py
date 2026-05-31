"""Output formatting module."""

import json
from datetime import datetime


def format_tweets_json(tweets: list[dict]) -> str:
    """Format tweets as JSON."""
    return json.dumps(tweets, indent=2, ensure_ascii=False)


def format_tweets_markdown(tweets: list[dict], date: str = None) -> str:
    """Format tweets as Markdown."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        f"# X/Twitter Digest — {date}\n",
        f"*{len(tweets)} posts, ranked by engagement*\n",
    ]
    
    for i, t in enumerate(tweets, 1):
        engagement = f"{t['likes']}L / {t['retweets']}RT / {t['replies']}R"
        lines.append(f"## {i}. @{t['author']} ({t['author_name']})")
        lines.append("")
        quoted = "\n> ".join(t["text"].splitlines())
        lines.append(f"> {quoted}")
        lines.append("")
        lines.append(f"**Engagement:** {engagement}  ")
        lines.append(f"**Posted:** {t['created_at']}  ")
        lines.append(f"**Link:** {t['url']}")
        
        if t.get("reply_texts"):
            lines.append("")
            lines.append("<details><summary>Thread replies</summary>\n")
            for r in t["reply_texts"][:5]:
                lines.append(f"> **@{r['author']}:** {r['text']}")
                lines.append("")
            lines.append("</details>")
        lines.append("")
    
    return "\n".join(lines) + "\n"


def build_claude_prompt(tweets: list[dict], queries: list[str] = None) -> str:
    """Build prompt for Claude API summarization."""
    lines = []
    for i, t in enumerate(tweets, 1):
        engagement = f"[{t['likes']}L/{t['retweets']}RT/{t['replies']}R]"
        lines.append(f"---\nTweet {i} by @{t['author']} ({t['author_name']}) {engagement}\nURL: {t['url']}\nPosted: {t['created_at']}")
        lines.append(t["text"])
        if t.get("reply_texts"):
            lines.append("Notable replies:")
            for r in t["reply_texts"][:5]:
                lines.append(f"  @{r['author']}: {r['text']}")
    tweet_block = "\n".join(lines)

    query_context = ""
    if queries:
        query_context = f"\n\nThe user searched for: {', '.join(queries)}\n"

    return f"""You are producing a daily digest of X/Twitter posts.{query_context}
Below are {len(tweets)} tweets collected today, ranked by engagement. Analyze them and produce a structured markdown report relevant to the search query.

## Output format

Start with a heading: # [Topic] Daily Digest — [today's date]

Then organize into 3-5 sections that fit the content. Choose section names that match what the tweets are actually about.

For each item:
- One-line summary of the insight
- Link to the original tweet (use the EXACT URL provided for each tweet, do NOT fabricate URLs)
- @author attribution and post date/time

Keep it concise and scannable. No fluff. IMPORTANT: Use the exact tweet URLs provided — never generate or guess URLs.

---
TWEETS:
{tweet_block}"""
