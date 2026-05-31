"""Claude API summarization module."""

import logging
import os
import subprocess

logger = logging.getLogger("summarizer")


def summarize_with_claude(prompt: str) -> str:
    """Call claude CLI to summarize tweets."""
    try:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        if result.returncode != 0:
            logger.error(f"claude -p failed: {result.stderr}")
            return ""
        return result.stdout.strip()
    except FileNotFoundError:
        logger.error("'claude' CLI not found in PATH")
        return ""
    except subprocess.TimeoutExpired:
        logger.error("claude -p timed out after 120s")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error calling claude: {e}")
        return ""


def summarize_tweets_with_claude(tweets: list[dict], queries: list[str] = None) -> str:
    """
    Summarize tweets using Claude.
    
    Returns the markdown summary or empty string if summarization fails.
    """
    from .formatter import build_claude_prompt
    
    if not tweets:
        return ""
    
    prompt = build_claude_prompt(tweets, queries=queries)
    logger.info(f"Sending {len(tweets)} tweets to Claude for summarization...")
    
    summary = summarize_with_claude(prompt)
    
    if not summary:
        logger.error("Summarization returned empty.")
        return ""
    
    # Insert subtitle after the first heading line
    date = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    subtitle = f"\n\n*Generated from {len(tweets)} top posts on X/Twitter on {date}*\n"
    
    lines = summary.split("\n", 1)
    if len(lines) == 2:
        output = lines[0] + subtitle + lines[1]
    else:
        output = summary + subtitle
    
    return output + "\n"
