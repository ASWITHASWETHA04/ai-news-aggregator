"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# ─── Auth Models ────────────────────────────────────────────────────────────

class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ─── Preferences Models ──────────────────────────────────────────────────────

VALID_CATEGORIES = [
    "technology", "ai", "sports", "business",
    "health", "science", "entertainment", "politics", "world"
]


class PreferencesUpdate(BaseModel):
    categories: List[str] = Field(..., min_length=1)


class PreferencesResponse(BaseModel):
    categories: List[str]


# ─── News Models ─────────────────────────────────────────────────────────────

class NewsArticle(BaseModel):
    title: str
    description: Optional[str] = ""
    content: Optional[str] = ""
    url: str
    image: Optional[str] = ""
    source: Optional[str] = ""
    category: Optional[str] = "general"
    published_at: Optional[str] = ""


class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    total: int


# ─── Chat Models ─────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = []
