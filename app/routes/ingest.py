# This is your first real FastAPI endpoint. 
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.security import verify_api_key
from app.services.chunker import chunk_text
from app.services.embedder import embed_texts
from app.db.qdrant import store_chunks

#APIRouter is like a mini-app we register routes on it
#then attach it to the main app in main.py

router = APIRouter()


@router.post("/ingest")
async def ingest_transcript(
    file: UploadFile = File(...),
    authorized: bool = Depends(verify_api_key)):
    """
    Accepts a .txt transcript file, chunks it, embeds it, stores in Qdrant.
    """
    #only allow a .txt transcript file, chunk it , embed it, store in qdrant
    
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    # Read rhe file contents
    content = await file.read()
    text = content.decode("utf-8")

    if not text.strip():
        raise HTTPException(status_code=400,detail="The file is empty")

# Step 1: Split into chunks
    chunks = chunk_text(text)
# Step 2: Embed all chunks (send to Gemini, get vectors back )
    try:
        embeddings = embed_texts(chunks)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
#Step 3: Store in Qdrant
    try:
        store_chunks(chunks, embeddings, source = file.filename)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Could not store chunks in Qdrant: {exc}") from exc

    return{
        "status": "success",
        "filename": file.filename,
        "chunks_stored": len(chunks)
    }
