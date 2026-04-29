"""
News router: /news
Endpoints for personalized feed, search, trending, and article detail.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional

from auth_utils import get_current_user
from services.news_service import (
    get_articles_by_categories,
    search_articles,
    get_trending_articles,
    get_article_by_url,
    refresh_news_for_categories,
)
from models import VALID_CATEGORIES

router = APIRouter()


@router.get("/feed")
async def get_personalized_feed(
    limit: int = Query(20, ge=1, le=50),
    skip: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """
    Return personalized news feed based on user preferences.
    Automatically refreshes news if the feed is empty.
    """
    preferences = current_user.get("preferences", ["technology"])

    articles = await get_articles_by_categories(preferences, limit=limit, skip=skip)

    # If no articles cached, fetch fresh ones
    if not articles and skip == 0:
        await refresh_news_for_categories(preferences)
        articles = await get_articles_by_categories(preferences, limit=limit, skip=skip)

    return {"articles": articles, "total": len(articles), "categories": preferences}


@router.get("/trending")
async def get_trending(limit: int = Query(10, ge=1, le=20)):
    """Return trending news (no auth required)."""
    articles = await get_trending_articles(limit=limit)

    # Seed with default categories if empty
    if not articles:
        await refresh_news_for_categories(["technology", "business", "sports"])
        articles = await get_trending_articles(limit=limit)

    return {"articles": articles, "total": len(articles)}


@router.get("/search")
async def search_news(
    q: str = Query(..., min_length=2, description="Search keyword"),
    limit: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """Keyword search across all stored articles."""
    articles = await search_articles(q, limit=limit)
    return {"articles": articles, "total": len(articles), "query": q}


@router.get("/category/{category}")
async def get_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=50),
    refresh: bool = Query(False),
):
    """
    Get articles for a specific category.
    Pass ?refresh=true to force-fetch fresh articles.
    """
    if category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    if refresh:
        await refresh_news_for_categories([category])

    articles = await get_articles_by_categories([category], limit=limit)

    if not articles:
        await refresh_news_for_categories([category])
        articles = await get_articles_by_categories([category], limit=limit)

    return {"articles": articles, "total": len(articles), "category": category}


@router.get("/article")
async def get_article_detail(
    url: str = Query(..., description="Article URL"),
    current_user: dict = Depends(get_current_user),
):
    """Return full details of a single article by URL."""
    article = await get_article_by_url(url)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/refresh")
async def refresh_feed(current_user: dict = Depends(get_current_user)):
    """Manually trigger a news refresh for the user's preferences."""
    preferences = current_user.get("preferences", ["technology"])
    count = await refresh_news_for_categories(preferences)
    return {"message": f"Refreshed news feed. {count} new articles added."}
