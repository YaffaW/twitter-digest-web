"""API routes for Twitter digest."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import logging

from ..core import twitter_fetcher, formatter, summarizer

logger = logging.getLogger("api")

router = APIRouter(prefix="/api", tags=["twitter"])


class SearchRequest(BaseModel):
    """Request model for tweet search."""
    queries: list[str]
    max_results_per_query: int = 20
    min_likes: int = 3
    min_text_length: int = 0
    within_24_hours: bool = False
    fetch_replies: bool = True
    max_tweets: int = 30
    mode: str = "markdown"  # json, markdown, or claude


class SearchResponse(BaseModel):
    """Response model for tweet search."""
    tweets: list[dict]
    count: int
    digest: str = None
    status: str


@router.post("/search")
async def search_tweets(request: SearchRequest):
    """
    Search for tweets based on queries.
    
    - queries: List of search queries (DuckDuckGo syntax)
    - max_results_per_query: Max tweets per query
    - min_likes: Minimum likes threshold
    - fetch_replies: Whether to fetch thread replies
    - max_tweets: Max tweets to return
    - mode: Output format (json, markdown, claude)
    """
    try:
        if not request.queries or len(request.queries) == 0:
            raise HTTPException(status_code=400, detail="At least one query is required")
        
        if request.mode not in ["json", "markdown", "claude"]:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}. Must be json, markdown, or claude")
        
        # Fetch tweets
        tweets = twitter_fetcher.search_and_fetch(
            queries=request.queries,
            max_results_per_query=request.max_results_per_query,
            min_likes=request.min_likes,
            min_text_length=request.min_text_length,
            within_24_hours=request.within_24_hours,
            fetch_replies_flag=request.fetch_replies,
            max_tweets=request.max_tweets,
        )
        
        if not tweets:
            return SearchResponse(
                tweets=[],
                count=0,
                digest="No tweets found matching your criteria.",
                status="success"
            )
        
        # Format response
        digest = None
        if request.mode == "markdown":
            digest = formatter.format_tweets_markdown(tweets)
        elif request.mode == "claude":
            digest = summarizer.summarize_tweets_with_claude(tweets, request.queries)
            if not digest:
                digest = formatter.format_tweets_markdown(tweets)
        
        return SearchResponse(
            tweets=tweets,
            count=len(tweets),
            digest=digest,
            status="success"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
