"""
FAISS vector store management.
Handles embedding creation and similarity search for RAG.
"""

import os
import pickle
from typing import List, Optional
import numpy as np

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from config import settings

# Path to persist the FAISS index
FAISS_INDEX_PATH = "faiss_index"

# Global vector store instance (lazy-loaded)
_vector_store: Optional[FAISS] = None
_embeddings: Optional[OpenAIEmbeddings] = None


def get_embeddings() -> OpenAIEmbeddings:
    """Return (or create) the OpenAI embeddings instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small",
        )
    return _embeddings


def get_vector_store() -> Optional[FAISS]:
    """Return the current in-memory vector store."""
    return _vector_store


def articles_to_documents(articles: List[dict]) -> List[Document]:
    """Convert article dicts to LangChain Document objects."""
    docs = []
    for article in articles:
        # Combine title + description + content for richer embeddings
        text = f"{article.get('title', '')}\n{article.get('description', '')}\n{article.get('content', '')}"
        text = text.strip()
        if not text:
            continue
        metadata = {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "source": article.get("source", ""),
            "category": article.get("category", ""),
            "published_at": article.get("published_at", ""),
            "image": article.get("image", ""),
        }
        docs.append(Document(page_content=text, metadata=metadata))
    return docs


async def build_vector_store(articles: List[dict]) -> bool:
    """
    Build (or rebuild) the FAISS index from a list of articles.
    Returns True on success.
    """
    global _vector_store

    if not articles:
        print("No articles to index.")
        return False

    if not settings.OPENAI_API_KEY:
        print("OpenAI API key not set — skipping vector store build.")
        return False

    try:
        docs = articles_to_documents(articles)
        if not docs:
            return False

        embeddings = get_embeddings()
        _vector_store = FAISS.from_documents(docs, embeddings)

        # Persist to disk
        _vector_store.save_local(FAISS_INDEX_PATH)
        print(f"✅ FAISS index built with {len(docs)} documents.")
        return True
    except Exception as e:
        print(f"Error building vector store: {e}")
        return False


def load_vector_store() -> bool:
    """Load persisted FAISS index from disk."""
    global _vector_store

    if not os.path.exists(FAISS_INDEX_PATH):
        return False

    if not settings.OPENAI_API_KEY:
        return False

    try:
        embeddings = get_embeddings()
        _vector_store = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print(f"✅ FAISS index loaded from disk.")
        return True
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return False


def similarity_search(query: str, k: int = 5) -> List[Document]:
    """
    Perform similarity search on the vector store.
    Returns top-k relevant documents.
    """
    global _vector_store

    # Try loading from disk if not in memory
    if _vector_store is None:
        load_vector_store()

    if _vector_store is None:
        return []

    try:
        return _vector_store.similarity_search(query, k=k)
    except Exception as e:
        print(f"Similarity search error: {e}")
        return []


async def add_articles_to_store(articles: List[dict]) -> bool:
    """Add new articles to the existing vector store (incremental update)."""
    global _vector_store

    if not settings.OPENAI_API_KEY or not articles:
        return False

    try:
        docs = articles_to_documents(articles)
        if not docs:
            return False

        embeddings = get_embeddings()

        if _vector_store is None:
            _vector_store = FAISS.from_documents(docs, embeddings)
        else:
            _vector_store.add_documents(docs)

        _vector_store.save_local(FAISS_INDEX_PATH)
        return True
    except Exception as e:
        print(f"Error adding to vector store: {e}")
        return False
