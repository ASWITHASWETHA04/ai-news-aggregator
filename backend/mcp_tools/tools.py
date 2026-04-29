"""
MCP (Model Context Protocol) Tools implemented as LangChain-compatible functions.

Tools:
  1. NewsRetrievalTool   - Retrieve relevant articles by topic
  2. SummarizationTool   - Summarize a list of articles
  3. RecommendationTool  - Recommend articles based on user preferences
"""

from typing import List, Optional
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from config import settings
from rag.vector_store import similarity_search
from services.news_service import get_articles_by_categories, search_articles


# ─── Helper: get LLM ─────────────────────────────────────────────────────────

def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model="gpt-3.5-turbo",
        temperature=temperature,
    )


# ─── Tool 1: News Retrieval ───────────────────────────────────────────────────

async def news_retrieval_tool(topic: str) -> str:
    """
    MCP Tool: Retrieve relevant news articles for a given topic.
    Uses FAISS vector similarity search first, falls back to keyword search.

    Input:  topic (str) - e.g., "artificial intelligence breakthroughs"
    Output: formatted string of relevant article titles and descriptions
    """
    # Try vector similarity search
    docs = similarity_search(topic, k=5)

    if docs:
        results = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            results.append(
                f"{i}. **{meta.get('title', 'No title')}**\n"
                f"   Source: {meta.get('source', 'Unknown')} | "
                f"Category: {meta.get('category', 'general')}\n"
                f"   {doc.page_content[:200]}...\n"
                f"   URL: {meta.get('url', '')}"
            )
        return "\n\n".join(results)

    # Fallback: keyword search in MongoDB
    articles = await search_articles(topic, limit=5)
    if not articles:
        return f"No articles found for topic: {topic}"

    results = []
    for i, a in enumerate(articles, 1):
        results.append(
            f"{i}. **{a.get('title', 'No title')}**\n"
            f"   Source: {a.get('source', 'Unknown')}\n"
            f"   {a.get('description', '')[:200]}"
        )
    return "\n\n".join(results)


# ─── Tool 2: Summarization ────────────────────────────────────────────────────

async def summarization_tool(articles_text: str) -> str:
    """
    MCP Tool: Summarize a collection of news articles.

    Input:  articles_text (str) - concatenated article content
    Output: concise bullet-point summary
    """
    if not settings.OPENAI_API_KEY:
        return "Summarization unavailable: OpenAI API key not configured."

    if not articles_text.strip():
        return "No content provided to summarize."

    llm = get_llm(temperature=0.2)

    messages = [
        SystemMessage(content=(
            "You are a professional news summarizer. "
            "Create a concise, bullet-point summary of the provided news articles. "
            "Focus on key facts, trends, and important developments. "
            "Keep it under 200 words."
        )),
        HumanMessage(content=f"Summarize these news articles:\n\n{articles_text[:3000]}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        return response.content
    except Exception as e:
        return f"Summarization error: {str(e)}"


# ─── Tool 3: Recommendation ───────────────────────────────────────────────────

async def recommendation_tool(preferences: str) -> str:
    """
    MCP Tool: Recommend personalized news based on user preferences.

    Input:  preferences (str) - comma-separated categories e.g. "technology, ai, sports"
    Output: formatted list of recommended articles
    """
    # Parse preferences string into list
    categories = [p.strip().lower() for p in preferences.split(",") if p.strip()]
    if not categories:
        categories = ["technology"]

    articles = await get_articles_by_categories(categories, limit=8)

    if not articles:
        return f"No personalized articles found for preferences: {preferences}"

    results = []
    for i, a in enumerate(articles, 1):
        results.append(
            f"{i}. **{a.get('title', 'No title')}**\n"
            f"   Category: {a.get('category', 'general')} | "
            f"Source: {a.get('source', 'Unknown')}\n"
            f"   {a.get('description', '')[:150]}"
        )

    return f"Personalized recommendations for [{preferences}]:\n\n" + "\n\n".join(results)


# ─── LangChain Tool Wrappers ──────────────────────────────────────────────────

def create_mcp_tools() -> List[Tool]:
    """
    Create LangChain Tool objects wrapping the MCP tool functions.
    These are passed to the LangChain agent.
    """
    return [
        Tool(
            name="NewsRetrieval",
            func=lambda topic: None,  # sync placeholder
            coroutine=news_retrieval_tool,
            description=(
                "Retrieve relevant news articles for a given topic or query. "
                "Input should be a topic string like 'AI news today' or 'sports results'. "
                "Returns a list of relevant articles with titles and descriptions."
            ),
        ),
        Tool(
            name="Summarization",
            func=lambda text: None,
            coroutine=summarization_tool,
            description=(
                "Summarize a collection of news articles. "
                "Input should be the article content or titles to summarize. "
                "Returns a concise bullet-point summary."
            ),
        ),
        Tool(
            name="Recommendation",
            func=lambda prefs: None,
            coroutine=recommendation_tool,
            description=(
                "Get personalized news recommendations based on user preferences. "
                "Input should be comma-separated categories like 'technology, sports, business'. "
                "Returns a personalized list of recommended articles."
            ),
        ),
    ]
