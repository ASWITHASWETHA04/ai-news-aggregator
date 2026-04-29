"""
Main FastAPI application entry point.
Registers all routers and configures CORS.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from routers import auth, news, chat, preferences
from database import connect_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="AI News Aggregator API",
    description="Personalized News Aggregator with RAG + MCP AI Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(news.router, prefix="/news", tags=["News"])
app.include_router(chat.router, prefix="/chat", tags=["AI Chat"])
app.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "AI News Aggregator API is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
