"""
Chat router: /chat
AI-powered chatbot endpoint using RAG + MCP tools.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Tuple

from models import ChatMessage, ChatResponse
from auth_utils import get_current_user
from rag.rag_chain import get_rag_answer
from rag.vector_store import build_vector_store, load_vector_store
from services.news_service import get_articles_by_categories, refresh_news_for_categories
from database import get_db

router = APIRouter()

# In-memory chat history per user (keyed by user_id)
# In production, store this in Redis or MongoDB
_chat_histories: dict = {}


@router.post("/", response_model=ChatResponse)
async def chat(
    payload: ChatMessage,
    current_user: dict = Depends(get_current_user),
):
    """
    Main chat endpoint.
    Processes user message through RAG pipeline and returns AI response.
    """
    user_id = current_user["_id"]
    preferences = current_user.get("preferences", ["technology"])

    # Ensure vector store is loaded
    load_vector_store()

    # Get or initialize chat history for this user
    history: List[Tuple[str, str]] = _chat_histories.get(user_id, [])

    # Get RAG answer
    result = await get_rag_answer(
        query=payload.message,
        user_preferences=preferences,
        chat_history=history,
    )

    # Update chat history (keep last 10 turns)
    history.append((payload.message, result["answer"]))
    _chat_histories[user_id] = history[-10:]

    return ChatResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
    )


@router.post("/index")
async def index_news(current_user: dict = Depends(get_current_user)):
    """
    Trigger re-indexing of news articles into FAISS vector store.
    Call this after refreshing news to update the RAG knowledge base.
    """
    preferences = current_user.get("preferences", ["technology"])

    # Fetch fresh articles
    await refresh_news_for_categories(preferences)

    # Get all articles for indexing
    all_categories = [
        "technology", "ai", "sports", "business",
        "health", "science", "entertainment"
    ]
    articles = await get_articles_by_categories(all_categories, limit=200)

    if not articles:
        raise HTTPException(status_code=404, detail="No articles available to index")

    success = await build_vector_store(articles)

    if success:
        return {"message": f"Successfully indexed {len(articles)} articles into FAISS."}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to build vector store. Check OpenAI API key."
        )


@router.delete("/history")
async def clear_history(current_user: dict = Depends(get_current_user)):
    """Clear the chat history for the current user."""
    user_id = current_user["_id"]
    _chat_histories.pop(user_id, None)
    return {"message": "Chat history cleared."}


@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    """Return the current user's chat history."""
    user_id = current_user["_id"]
    history = _chat_histories.get(user_id, [])
    formatted = [
        {"role": "user", "content": h} if i % 2 == 0 else {"role": "assistant", "content": h}
        for turn in history
        for i, h in enumerate(turn)
    ]
    return {"history": history}
