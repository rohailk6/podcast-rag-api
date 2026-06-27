from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.routes import ingest, query
from app.routes import ingest, query, users, sessions
from app.db.qdrant import create_collection_if_not_exist
from app.limiter import limiter
from app.db.postgres import init_db, close_db

# 1. Define the lifespan (startup and shutdown logic)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs BEFORE the server starts taking requests (Startup)
    print("Starting up...")
    create_collection_if_not_exist()
    await init_db() # <- connects to PostgresSQL, creates tables
    print("Ready!")
    
    yield  # The API runs while paused right here
    
    # This runs AFTER the server shuts down (Shutdown)
    await close_db() # <- closes database connections cleanly
    print("Shutting down...")

# 2. Pass the lifespan to your FastAPI app
app = FastAPI(
    title="Podcast RAG API",
    description="Ask questions about podcast transcripts using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# Attach the limiter to the app so slowapi can find it on requests
app.state.limiter = limiter

# Register the 429 handler — this is what sends the proper error response
# when someone exceeds their limit. slowapi provides this handler built-in.
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Your routers stay exactly the same
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(query.router, tags=["Query"])
app.include_router(users.router , tags=["Users"]) # <- new 
app.include_router(sessions.router, tags=["Sessions"]) # <- new

@app.get("/")
async def root():
    return {"message": "Podcast RAG API is running!"}