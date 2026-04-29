"""
News service: fetches articles from NewsAPI / GNews.
Falls back to demo articles when API keys are not configured.
"""

import httpx
from datetime import datetime
from typing import List, Optional
from config import settings
from database import get_db


# ─── Demo articles (shown when no API key is set) ────────────────────────────

DEMO_ARTICLES = [
    {
        "title": "OpenAI Releases GPT-5 with Unprecedented Reasoning Capabilities",
        "description": "The latest model from OpenAI demonstrates human-level reasoning across math, science, and coding benchmarks.",
        "content": "OpenAI has unveiled GPT-5, its most powerful language model to date. The model shows significant improvements in logical reasoning, mathematical problem-solving, and code generation.",
        "url": "https://example.com/openai-gpt5",
        "image": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800",
        "source": "Tech News Daily",
        "category": "ai",
        "published_at": "2026-04-29T10:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "Apple Announces M4 Ultra Chip for Mac Pro",
        "description": "Apple's new M4 Ultra chip delivers 2x performance improvement over its predecessor with 40% better energy efficiency.",
        "content": "Apple has announced the M4 Ultra chip, the most powerful chip ever built for a personal computer. The chip features 192GB of unified memory and a 32-core CPU.",
        "url": "https://example.com/apple-m4-ultra",
        "image": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800",
        "source": "MacRumors",
        "category": "technology",
        "published_at": "2026-04-29T09:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "Tesla Reports Record Q1 2026 Deliveries",
        "description": "Tesla delivered 550,000 vehicles in Q1 2026, beating analyst expectations by 15%.",
        "content": "Tesla Inc. reported record first-quarter deliveries of 550,000 vehicles, surpassing Wall Street estimates. The company attributed the growth to strong demand for the Model 3 refresh.",
        "url": "https://example.com/tesla-q1-2026",
        "image": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=800",
        "source": "Reuters",
        "category": "business",
        "published_at": "2026-04-28T14:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "Champions League Semi-Finals: Real Madrid vs Bayern Munich Preview",
        "description": "Both clubs are in top form heading into the first leg at the Bernabeu on Tuesday.",
        "content": "Real Madrid and Bayern Munich meet in the Champions League semi-finals for the fourth time in a decade. Madrid's Vinicius Jr. is in sensational form with 12 goals in the competition.",
        "url": "https://example.com/ucl-semifinal",
        "image": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800",
        "source": "ESPN",
        "category": "sports",
        "published_at": "2026-04-28T12:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "Scientists Discover New Treatment for Alzheimer's Disease",
        "description": "A breakthrough drug trial shows 60% reduction in cognitive decline in early-stage Alzheimer's patients.",
        "content": "Researchers at Johns Hopkins University have announced promising results from a Phase 3 clinical trial of a new Alzheimer's treatment. The drug targets amyloid plaques more effectively than previous treatments.",
        "url": "https://example.com/alzheimers-treatment",
        "image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",
        "source": "Medical News Today",
        "category": "health",
        "published_at": "2026-04-27T16:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "NASA's Artemis IV Mission Successfully Lands on the Moon",
        "description": "Four astronauts have landed near the lunar south pole, marking humanity's return to the Moon.",
        "content": "NASA's Artemis IV mission has successfully landed four astronauts near the lunar south pole. The crew will spend 14 days conducting scientific experiments and testing equipment for future Mars missions.",
        "url": "https://example.com/artemis-iv",
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800",
        "source": "NASA",
        "category": "science",
        "published_at": "2026-04-27T08:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "Google I/O 2026: Android 17 and Gemini Ultra Announced",
        "description": "Google unveiled Android 17 with deep Gemini AI integration and new privacy features at its annual developer conference.",
        "content": "At Google I/O 2026, the company announced Android 17 featuring native Gemini Ultra integration, improved battery life, and enhanced privacy controls. The update rolls out to Pixel devices first.",
        "url": "https://example.com/google-io-2026",
        "image": "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=800",
        "source": "The Verge",
        "category": "technology",
        "published_at": "2026-04-26T18:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "Global Stock Markets Hit All-Time Highs Amid AI Boom",
        "description": "S&P 500 crosses 7,000 points for the first time as AI-related stocks continue to surge.",
        "content": "Global equity markets reached record highs this week, driven by strong earnings from major technology companies. The AI sector has been the primary driver of market gains in 2026.",
        "url": "https://example.com/stock-market-highs",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
        "source": "Bloomberg",
        "category": "business",
        "published_at": "2026-04-26T15:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "Meta Launches Horizon OS 3.0 for Mixed Reality Headsets",
        "description": "The new operating system brings spatial computing features and improved hand tracking to Quest devices.",
        "content": "Meta has released Horizon OS 3.0, a major update to its mixed reality platform. The update introduces spatial app windows, improved hand tracking accuracy, and new developer APIs.",
        "url": "https://example.com/meta-horizon-os",
        "image": "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=800",
        "source": "Road to VR",
        "category": "technology",
        "published_at": "2026-04-25T11:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "LangChain 0.3 Released with Native MCP Support",
        "description": "The popular AI framework adds first-class support for Model Context Protocol, simplifying agent tool integration.",
        "content": "LangChain has released version 0.3 featuring native Model Context Protocol (MCP) support. Developers can now connect AI agents to external tools and data sources with minimal configuration.",
        "url": "https://example.com/langchain-03",
        "image": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800",
        "source": "AI Weekly",
        "category": "ai",
        "published_at": "2026-04-25T09:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "NBA Playoffs: Golden State Warriors Advance to Conference Finals",
        "description": "Stephen Curry's 45-point performance leads the Warriors past the Denver Nuggets in Game 6.",
        "content": "The Golden State Warriors advanced to the Western Conference Finals after Stephen Curry delivered a masterclass performance with 45 points, 8 assists, and 6 rebounds in Game 6.",
        "url": "https://example.com/warriors-playoffs",
        "image": "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800",
        "source": "ESPN",
        "category": "sports",
        "published_at": "2026-04-24T23:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
    {
        "title": "WHO Declares End of Global Health Emergency",
        "description": "The World Health Organization officially ends the global health emergency status that has been in place since 2020.",
        "content": "The World Health Organization has officially declared the end of the global health emergency, citing improved global health infrastructure and vaccination coverage worldwide.",
        "url": "https://example.com/who-emergency-end",
        "image": "https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=800",
        "source": "Reuters",
        "category": "health",
        "published_at": "2026-04-24T14:00:00Z",
        "fetched_at": datetime.utcnow(),
    },
]


# ─── NewsAPI Fetcher ──────────────────────────────────────────────────────────

async def fetch_from_newsapi(category: str, page_size: int = 20) -> List[dict]:
    """Fetch articles from NewsAPI.org."""
    if not settings.NEWS_API_KEY or settings.NEWS_API_KEY == "your-newsapi-org-key-here":
        return []

    category_map = {
        "technology": "technology", "ai": "technology",
        "sports": "sports", "business": "business",
        "health": "health", "science": "science",
        "entertainment": "entertainment", "politics": "general", "world": "general",
    }
    api_category = category_map.get(category, "general")

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": api_category,
        "pageSize": page_size,
        "language": "en",
        "apiKey": settings.NEWS_API_KEY,
    }

    if category == "ai":
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "artificial intelligence OR machine learning",
            "pageSize": page_size,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": settings.NEWS_API_KEY,
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        articles = []
        for item in data.get("articles", []):
            if not item.get("title") or item["title"] == "[Removed]":
                continue
            articles.append({
                "title": item.get("title", ""),
                "description": item.get("description", "") or "",
                "content": item.get("content", "") or "",
                "url": item.get("url", ""),
                "image": item.get("urlToImage", "") or "",
                "source": item.get("source", {}).get("name", ""),
                "category": category,
                "published_at": item.get("publishedAt", ""),
                "fetched_at": datetime.utcnow(),
            })
        return articles
    except Exception as e:
        print(f"NewsAPI error for {category}: {e}")
        return []


async def fetch_from_gnews(category: str, page_size: int = 10) -> List[dict]:
    """Fetch articles from GNews API."""
    if not settings.GNEWS_API_KEY or settings.GNEWS_API_KEY == "your-gnews-io-key-here":
        return []

    topic_map = {
        "technology": "technology", "ai": "technology",
        "sports": "sports", "business": "business",
        "health": "health", "science": "science",
        "entertainment": "entertainment", "politics": "politics", "world": "world",
    }
    topic = topic_map.get(category, "general")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://gnews.io/api/v4/top-headlines",
                params={"topic": topic, "max": page_size, "lang": "en", "token": settings.GNEWS_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()

        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title": item.get("title", ""),
                "description": item.get("description", "") or "",
                "content": item.get("content", "") or "",
                "url": item.get("url", ""),
                "image": item.get("image", "") or "",
                "source": item.get("source", {}).get("name", ""),
                "category": category,
                "published_at": item.get("publishedAt", ""),
                "fetched_at": datetime.utcnow(),
            })
        return articles
    except Exception as e:
        print(f"GNews error for {category}: {e}")
        return []


# ─── Storage & Retrieval ──────────────────────────────────────────────────────

async def store_articles(articles: List[dict]) -> int:
    """Upsert articles by URL. Returns count of new articles."""
    db = get_db()
    inserted = 0
    for article in articles:
        result = await db.articles.update_one(
            {"url": article["url"]},
            {"$setOnInsert": article},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
    return inserted


async def seed_demo_articles():
    """Seed demo articles into the store if empty."""
    db = get_db()
    existing = await db.articles.find({}).to_list(length=1)
    if not existing:
        await store_articles(DEMO_ARTICLES)
        print(f"✅ Seeded {len(DEMO_ARTICLES)} demo articles")


async def get_articles_by_categories(
    categories: List[str], limit: int = 30, skip: int = 0
) -> List[dict]:
    db = get_db()
    await seed_demo_articles()
    cursor = (
        db.articles.find({"category": {"$in": categories}}, {"_id": 0})
        .sort("published_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def search_articles(query: str, limit: int = 20) -> List[dict]:
    db = get_db()
    await seed_demo_articles()
    await db.articles.create_index([("title", "text"), ("description", "text")])
    cursor = (
        db.articles.find({"$text": {"$search": query}}, {"_id": 0})
        .sort("published_at", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def get_article_by_url(url: str) -> Optional[dict]:
    db = get_db()
    return await db.articles.find_one({"url": url}, {"_id": 0})


async def get_trending_articles(limit: int = 10) -> List[dict]:
    db = get_db()
    await seed_demo_articles()
    cursor = (
        db.articles.find({}, {"_id": 0})
        .sort("fetched_at", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def refresh_news_for_categories(categories: List[str]) -> int:
    """Fetch fresh news; fall back to demo articles if no API keys."""
    total = 0
    has_real_news = False

    for category in categories:
        articles = await fetch_from_newsapi(category)
        if not articles:
            articles = await fetch_from_gnews(category)
        if articles:
            has_real_news = True
            count = await store_articles(articles)
            total += count
            print(f"  [{category}] fetched {len(articles)}, stored {count} new")

    if not has_real_news:
        # Seed demo articles so the UI always has content
        await seed_demo_articles()

    return total
