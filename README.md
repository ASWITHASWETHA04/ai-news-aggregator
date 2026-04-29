<div align="center">

# 🤖 AI News Aggregator
### RAG + MCP आधारित Personalized AI News Assistant

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=for-the-badge&logo=langchain)](https://langchain.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=for-the-badge&logo=openai)](https://openai.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb)](https://mongodb.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**A production-ready full-stack AI web application that aggregates news, personalizes content, and provides an intelligent chatbot using RAG (Retrieval-Augmented Generation) with MCP tools.**

🌐 **Live Local Preview:** [http://localhost:3000](http://localhost:3000) *(run locally — see setup below)*

[Features](#-features) • [Architecture](#-architecture) • [AI Concepts](#-ai-concepts-implemented) • [Setup](#-quick-start) • [API Docs](#-api-documentation) • [Deploy](#-deployment)

</div>

---

## 📸 Screenshots

| Home Feed | AI Chatbot | Preferences |
|-----------|-----------|-------------|
| Personalized news by category | RAG-powered Q&A | Select your interests |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Secure signup/login with bcrypt password hashing |
| 🎯 **Personalized Feed** | News filtered by user-selected categories |
| 🤖 **AI Chatbot (RAG)** | Ask questions, get AI answers grounded in real articles |
| 🔍 **Smart Search** | Keyword search across all stored articles |
| 📰 **News Aggregation** | Real-time articles from NewsAPI + GNews |
| 🧠 **MCP Tools** | NewsRetrieval, Summarization, Recommendation agents |
| 🌙 **Dark Mode** | Full light/dark theme toggle |
| 📱 **Responsive UI** | Mobile + desktop optimized |
| 🔥 **Trending Section** | Latest articles across all categories |
| 📄 **Article Detail** | Full article view with share functionality |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js 14)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  Home    │ │  Chat    │ │  Search  │ │  Preferences │   │
│  │  Feed    │ │  (RAG)   │ │  Page    │ │  Page        │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│              Axios HTTP Client + JWT Auth                    │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  /auth   │ │  /news   │ │  /chat   │ │ /preferences │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              RAG PIPELINE                           │    │
│  │  NewsAPI/GNews → MongoDB → FAISS Vector Store       │    │
│  │  Query → Embeddings → Similarity Search → LLM       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              MCP TOOLS (LangChain Agent)            │    │
│  │  NewsRetrievalTool | SummarizationTool | RecommTool │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
    MongoDB Atlas         FAISS Index          OpenAI API
```

---

## 🧠 AI Concepts Implemented

### 1. 🔗 RAG (Retrieval-Augmented Generation)

RAG combines information retrieval with language model generation to produce accurate, grounded answers.

```
User Query
    │
    ▼
[OpenAI Embeddings]          ← text-embedding-3-small
    │
    ▼
[FAISS Vector Search]        ← Top-K similar articles retrieved
    │
    ▼
[Context + Query → LLM]      ← GPT-3.5-turbo generates answer
    │
    ▼
Grounded Answer + Sources
```

**Implementation:** `backend/rag/vector_store.py` + `backend/rag/rag_chain.py`

```python
# How RAG works in this project
docs = similarity_search(query, k=5)          # Retrieve relevant articles
context = format_context(docs)                 # Build context window
answer = llm.invoke(context + query)           # Generate grounded answer
```

**Why RAG?** Without RAG, LLMs hallucinate. With RAG, answers are grounded in real, current news articles stored in our vector database.

---

### 2. 🛠️ MCP (Model Context Protocol) Tools

MCP tools are structured functions that AI agents can call to interact with external systems. We implement 3 MCP tools as LangChain-compatible functions:

```
┌─────────────────────────────────────────────────────────┐
│                    MCP TOOLS                            │
│                                                         │
│  Tool 1: NewsRetrievalTool                              │
│  ├── Input:  topic (str) — e.g. "AI breakthroughs"     │
│  ├── Action: FAISS similarity search → MongoDB fallback │
│  └── Output: Formatted list of relevant articles        │
│                                                         │
│  Tool 2: SummarizationTool                              │
│  ├── Input:  articles_text (str)                        │
│  ├── Action: GPT-3.5 summarization prompt               │
│  └── Output: Concise bullet-point summary               │
│                                                         │
│  Tool 3: RecommendationTool                             │
│  ├── Input:  preferences (str) — "technology, sports"  │
│  ├── Action: MongoDB category filter                    │
│  └── Output: Personalized article recommendations      │
└─────────────────────────────────────────────────────────┘
```

**Implementation:** `backend/mcp_tools/tools.py`

```python
# MCP Tool definition pattern
Tool(
    name="NewsRetrieval",
    coroutine=news_retrieval_tool,
    description="Retrieve relevant news articles for a given topic..."
)
```

---

### 3. 🤖 Agentic Frameworks

The chatbot uses a **LangChain ReAct Agent** — an autonomous agent that reasons and acts:

```
User: "Summarize today's AI news"
         │
         ▼
    [LangChain Agent]
         │
    ┌────▼────────────────────────────────────┐
    │  THINK: I need to find AI news first    │
    │  ACT:   Call NewsRetrievalTool("AI")    │
    │  OBS:   Got 5 articles about AI         │
    │  THINK: Now I should summarize them     │
    │  ACT:   Call SummarizationTool(articles)│
    │  OBS:   Got concise summary             │
    │  ANSWER: Here's today's AI summary...  │
    └─────────────────────────────────────────┘
```

**Implementation:** `backend/rag/rag_chain.py` using `create_openai_tools_agent`

```python
agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, max_iterations=3)
result = await executor.ainvoke({"input": user_query})
```

---

### 4. 🌐 Multi-Agent Systems

The system uses a **multi-tool agent architecture** where specialized tools collaborate:

```
                    ┌─────────────────┐
                    │  Orchestrator   │
                    │  (LangChain     │
                    │   Agent)        │
                    └────────┬────────┘
                             │ delegates to
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──┐  ┌────────▼───┐  ┌──────▼──────┐
    │  News      │  │Summarization│  │Recommendation│
    │  Retrieval │  │   Agent    │  │    Agent    │
    │  Agent     │  │            │  │             │
    └────────────┘  └────────────┘  └─────────────┘
         │                │                │
    FAISS/MongoDB      OpenAI LLM      MongoDB Filter
```

Each MCP tool acts as a **specialized sub-agent** with its own:
- Input schema (typed parameters)
- Action logic (retrieval, generation, filtering)
- Output format (structured response)

---

### 5. 🛡️ Guardrails (Safety, Validation, Constraints)

Multiple layers of guardrails protect the system:

```
INPUT GUARDRAILS
├── Pydantic validation (models.py)
│   ├── Email format validation
│   ├── Password minimum length (6 chars)
│   ├── Message max length (1000 chars)
│   └── Category whitelist validation
│
├── JWT authentication on all protected routes
│   └── 401 Unauthorized for invalid/expired tokens
│
└── Rate limiting via max_iterations=3 on agent

OUTPUT GUARDRAILS
├── LLM response validation
│   └── handle_parsing_errors=True on AgentExecutor
│
├── Graceful degradation
│   ├── No OpenAI key → helpful fallback message
│   ├── No MongoDB → in-memory storage
│   └── No NewsAPI → demo articles served
│
└── Content filtering
    └── Articles with "[Removed]" titles are skipped
```

**Implementation examples:**

```python
# Input validation (models.py)
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

# Category whitelist (preferences router)
VALID_CATEGORIES = ["technology", "ai", "sports", "business", ...]
invalid = [c for c in payload.categories if c not in VALID_CATEGORIES]
if invalid:
    raise HTTPException(400, f"Invalid categories: {invalid}")

# Agent constraint
AgentExecutor(max_iterations=3, handle_parsing_errors=True)
```

---

### 6. 📊 Observability (Logging, Monitoring, Tracing)

The system implements structured observability at multiple levels:

```
LOGGING LAYERS
├── Application Startup
│   ├── ✅ Connected to MongoDB Atlas: newsdb
│   └── ⚠️  MongoDB not configured — using in-memory storage
│
├── News Fetching
│   └── [technology] fetched 20, stored 5 new
│
├── Vector Store
│   ├── ✅ FAISS index built with 150 documents
│   └── ✅ FAISS index loaded from disk
│
├── RAG Pipeline
│   └── RAG error: <exception details>  ← with fallback
│
└── API Request Logging (uvicorn)
    └── INFO: 127.0.0.1 - "POST /chat/ HTTP/1.1" 200 OK

HEALTH MONITORING
├── GET /health          → {"status": "healthy"}
├── GET /               → {"status": "ok", "message": "..."}
└── GET /docs           → Interactive API documentation

TRACING (LangChain)
└── AgentExecutor(verbose=True)  ← enable for full trace
    ├── > Entering new AgentExecutor chain...
    ├── > Invoking: NewsRetrieval with {'topic': 'AI'}
    └── > Finished chain.
```

**To enable full LangChain tracing**, set in `rag_chain.py`:
```python
AgentExecutor(agent=agent, tools=tools, verbose=True)  # Full trace
```

**To enable LangSmith observability** (production), add to `.env`:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=news-aggregator
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (free tier)
- OpenAI API key
- NewsAPI key

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-news-aggregator.git
cd ai-news-aggregator
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local
```

### 4. Run Locally
```bash
# Terminal 1 — Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

**Open:** [http://localhost:3000](http://localhost:3000)

> ✅ **Works without API keys!** Demo articles are pre-loaded. Add API keys for real news + full AI features.

---

## 🔑 Environment Variables

### `backend/.env`
```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/newsdb
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
OPENAI_API_KEY=sk-your-openai-key
NEWS_API_KEY=your-newsapi-org-key
GNEWS_API_KEY=your-gnews-io-key
CORS_ORIGINS=["http://localhost:3000"]
```

### `frontend/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
ai-news-aggregator/
│
├── 📂 backend/                    # FastAPI Python backend
│   ├── main.py                    # App entry point + CORS
│   ├── config.py                  # Settings from .env
│   ├── database.py                # MongoDB + in-memory fallback
│   ├── models.py                  # Pydantic request/response models
│   ├── auth_utils.py              # JWT + bcrypt utilities
│   ├── requirements.txt           # Python dependencies
│   │
│   ├── 📂 routers/                # API route handlers
│   │   ├── auth.py                # /auth/signup, /auth/login
│   │   ├── news.py                # /news/feed, /news/search
│   │   ├── chat.py                # /chat/ (RAG chatbot)
│   │   └── preferences.py        # /preferences/
│   │
│   ├── 📂 services/
│   │   └── news_service.py        # NewsAPI + GNews fetching
│   │
│   ├── 📂 rag/                    # RAG implementation
│   │   ├── vector_store.py        # FAISS index management
│   │   └── rag_chain.py           # LangChain agent pipeline
│   │
│   └── 📂 mcp_tools/              # MCP Tool definitions
│       └── tools.py               # 3 LangChain tools
│
├── 📂 frontend/                   # Next.js React frontend
│   ├── 📂 app/
│   │   ├── layout.tsx             # Root layout
│   │   ├── providers.tsx          # Theme + Auth providers
│   │   ├── 📂 (main)/             # Protected pages
│   │   │   ├── page.tsx           # Home feed
│   │   │   ├── chat/page.tsx      # AI chatbot
│   │   │   ├── search/page.tsx    # Search
│   │   │   ├── preferences/page.tsx
│   │   │   └── article/page.tsx   # Article detail
│   │   └── 📂 (auth)/             # Auth pages
│   │       ├── login/page.tsx
│   │       └── signup/page.tsx
│   │
│   ├── 📂 components/
│   │   ├── Navbar.tsx             # Navigation + dark mode
│   │   ├── NewsCard.tsx           # Article card (3 variants)
│   │   ├── LoadingSkeleton.tsx    # Loading states
│   │   └── ProtectedRoute.tsx     # Auth guard
│   │
│   ├── 📂 context/
│   │   └── AuthContext.tsx        # Global auth state
│   │
│   └── 📂 lib/
│       ├── api.ts                 # Axios client + interceptors
│       ├── auth.ts                # Session management
│       └── types.ts               # TypeScript types
│
├── README.md                      # This file
├── SETUP.md                       # Detailed setup guide
└── .gitignore
```

---

## 📡 API Documentation

Interactive docs available at: **http://localhost:8000/docs**

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login, get JWT token |
| GET | `/auth/me` | ✅ | Get current user |
| GET | `/news/feed` | ✅ | Personalized news feed |
| GET | `/news/trending` | ❌ | Trending articles |
| GET | `/news/search?q=` | ✅ | Keyword search |
| GET | `/news/category/{cat}` | ❌ | Articles by category |
| GET | `/news/article?url=` | ✅ | Single article detail |
| POST | `/news/refresh` | ✅ | Refresh news feed |
| POST | `/chat/` | ✅ | Send message to AI |
| POST | `/chat/index` | ✅ | Index news into FAISS |
| DELETE | `/chat/history` | ✅ | Clear chat history |
| GET | `/preferences/` | ✅ | Get user preferences |
| PUT | `/preferences/` | ✅ | Update preferences |

---

## 🚢 Deployment

### Frontend → Vercel
```bash
# 1. Push to GitHub
# 2. Import at vercel.com
# 3. Set environment variable:
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Backend → Render
```bash
# 1. Push backend/ to GitHub
# 2. New Web Service on render.com
# Build: pip install -r requirements.txt
# Start: uvicorn main:app --host 0.0.0.0 --port $PORT
# 3. Add all environment variables
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14, React 18 | UI framework |
| Styling | Tailwind CSS | Utility-first CSS |
| HTTP Client | Axios | API calls + interceptors |
| Backend | FastAPI (Python) | REST API server |
| Auth | JWT + bcrypt | Secure authentication |
| Database | MongoDB Atlas | User data + articles |
| Vector DB | FAISS | Semantic similarity search |
| Embeddings | OpenAI text-embedding-3-small | Article vectorization |
| LLM | GPT-3.5-turbo | Answer generation |
| AI Framework | LangChain 0.2 | Agent + tool orchestration |
| News Sources | NewsAPI + GNews | Real-time articles |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using RAG + MCP + LangChain**

⭐ Star this repo if you found it helpful!

</div>
