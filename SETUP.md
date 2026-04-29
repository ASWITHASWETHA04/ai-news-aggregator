# Setup & Deployment Instructions

## Prerequisites

- Node.js 18+
- Python 3.10+
- MongoDB Atlas account
- OpenAI API key
- NewsAPI key (https://newsapi.org) or GNews key (https://gnews.io)

---

## Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

Run the backend:
```bash
uvicorn main:app --reload --port 8000
```

---

## Frontend Setup (Next.js)

```bash
cd frontend
npm install
```

Copy `.env.local.example` to `.env.local` and fill in values:
```bash
cp .env.local.example .env.local
```

Run the frontend:
```bash
npm run dev
```

Open http://localhost:3000

---

## Deployment

### Backend → Render

1. Push backend folder to GitHub
2. Create new Web Service on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env`

### Frontend → Vercel

1. Push frontend folder to GitHub
2. Import project on Vercel
3. Set `NEXT_PUBLIC_API_URL` to your Render backend URL
4. Deploy

---

## Environment Variables

### Backend `.env`
```
MONGODB_URL=mongodb+srv://...
JWT_SECRET=your_secret_key
OPENAI_API_KEY=sk-...
NEWS_API_KEY=your_newsapi_key
GNEWS_API_KEY=your_gnews_key
```

### Frontend `.env.local`
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
