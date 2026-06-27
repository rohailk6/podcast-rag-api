from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from app.security import verify_api_key
from app.services.embedder import embed_query
from app.services.rag import generate_answers
from app.db.qdrant import search_similar
from app.db.postgres import (
    get_session,
    get_session_messages,
    save_message,
    create_session
)
from app.limiter import limiter

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[int] = None  # optional — creates new session if not provided


@router.post("/query")
@limiter.limit("10/minute")
async def query_transcript(
    request: Request,
    body: QueryRequest,
    user: dict = Depends(verify_api_key)   # ← now receives full user dict
):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # ── Session handling ──────────────────────────────────────────────────────
    if body.session_id:
        # User provided a session_id — verify it belongs to them
        session = await get_session(body.session_id, user["id"])
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or you don't have access to it."
            )
        session_id = body.session_id
    else:
        # No session_id provided — create a new one automatically
        session_id = await create_session(user["id"])

    # ── Load conversation history ─────────────────────────────────────────────
    # Get all previous messages in this session so the LLM has context
    history = await get_session_messages(session_id)

    # ── RAG: embed → search → generate ───────────────────────────────────────
    try:
        query_vector = embed_query(body.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        relevant_chunks = search_similar(query_vector, top_k=5)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Could not search Qdrant: {exc}") from exc

    if not relevant_chunks:
        raise HTTPException(
            status_code=404,
            detail="No transcript chunks found. Ingest a transcript first."
        )

    # Pass both the transcript chunks AND the conversation history to Gemini
    answer = generate_answers(body.question, relevant_chunks, history=history)

    # ── Save this exchange to the database ────────────────────────────────────
    await save_message(session_id, "user", body.question)
    await save_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "question": body.question,
        "answer": answer,
        "sources_used": len(relevant_chunks)
    }