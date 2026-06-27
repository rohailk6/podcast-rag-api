# Podcast RAG API

A production-grade REST API that lets you upload podcast transcripts and ask questions about them using Retrieval-Augmented Generation (RAG).

## Features

- **Phase 1 — Core RAG**: Upload `.txt` transcripts, chunk and embed them with Google Gemini, store in Qdrant vector database, query with semantic search
- **Phase 2 — Auth + Rate Limiting**: API key authentication on all endpoints, per-user rate limiting (10 requests/minute) using slowapi
- **Phase 3 — PostgreSQL + Sessions**: User management with unique API keys, persistent conversation sessions, full message history per session

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI + Uvicorn |
| Vector Database | Qdrant |
| Relational Database | PostgreSQL + asyncpg |
| Embeddings | Google Gemini (gemini-embedding-001) |
| LLM | Google Gemini 2.5 Flash |
| Auth | API key via Authorization header |
| Rate Limiting | slowapi |

## Project Structure

podcast-rag/

├── app/

│   ├── main.py           # FastAPI app, startup/shutdown

│   ├── config.py         # Environment variables

│   ├── security.py       # API key authentication

│   ├── limiter.py        # Rate limiting setup

│   ├── routes/

│   │   ├── ingest.py     # POST /ingest

│   │   ├── query.py      # POST /query

│   │   ├── users.py      # POST /users

│   │   └── sessions.py   # POST /sessions, GET /sessions/{id}/history

│   ├── services/

│   │   ├── chunker.py    # Text chunking

│   │   ├── embedder.py   # Gemini embeddings

│   │   └── rag.py        # Prompt assembly + answer generation

│   └── db/

│       ├── qdrant.py     # Vector storage and search

│       └── postgres.py   # User, session, message operations

└── transcripts/

└── sample.txt        # Example transcript

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users` | Create user + get API key | No |
| POST | `/ingest` | Upload transcript | Yes |
| POST | `/query` | Ask a question | Yes |
| POST | `/sessions` | Create conversation session | Yes |
| GET | `/sessions/{id}/history` | Get conversation history | Yes |

## Setup

### Prerequisites
- Python 3.9+
- Docker (for Qdrant)
- PostgreSQL 15

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/podcast-rag-api.git
cd podcast-rag-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Gemini API key and database URL

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Start PostgreSQL and create database
psql postgres -c "CREATE DATABASE podcast_rag;"

# Start the server
uvicorn app.main:app --reload
```

### Environment Variables

Create a `.env` file with:
GOOGLE_API_KEY=your_gemini_api_key

QDRANT_HOST=localhost

QDRANT_PORT=6333

COLLECTION_NAME=podcast_transcripts

DATABASE_URL=postgresql://postgres@localhost/podcast_rag

## Usage

1. Create a user at `POST /users` and save your API key
2. Ingest a transcript at `POST /ingest` (upload a `.txt` file)
3. Create a session at `POST /sessions`
4. Ask questions at `POST /query` with your `session_id`
5. View history at `GET /sessions/{session_id}/history`

Interactive API docs available at `http://localhost:8000/docs`

