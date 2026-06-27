import requests
from app.config import GOOGLE_API_KEY

EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
EMBEDDING_TIMEOUT_SECONDS = 20
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def _embed_content(content: str, task_type: str) -> list[float]:
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    url = f"{GEMINI_API_BASE_URL}/{EMBEDDING_MODEL}:embedContent"
    payload = {
        "model": EMBEDDING_MODEL,
        "content": {"parts": [{"text": content}]},
        "taskType": task_type,
        "outputDimensionality": EMBEDDING_DIMENSIONS,
    }

    try:
        response = requests.post(
            url,
            params={"key": GOOGLE_API_KEY},
            json=payload,
            timeout=EMBEDDING_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("error", {}).get("message", "")
            except ValueError:
                detail = exc.response.text
        message = detail or str(exc)
        raise RuntimeError(f"Gemini embedding request failed: {message}") from exc

    try:
        return response.json()["embedding"]["values"]
    except (KeyError, ValueError) as exc:
        raise RuntimeError(f"Could not create Gemini embedding: {exc}") from exc

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Converts a list of text strings into a list of embedding vectors.
    One vector per text, each vector is a list of 768 floats.
    """
    embeddings = [] # Fixed spelling from "embedddings"

    # Loop through every text chunk
    for text in texts:
        # 2. FIX TYPO: changed "embedddings.appemnd" to "embeddings.append"
        embeddings.append(_embed_content(text, "RETRIEVAL_DOCUMENT")) 

    # 3. FIX LOGIC: Un-indented the return statement so it executes AFTER the loop completes!
    return embeddings

def embed_query(query: str) -> list[float]:
    """
    Converts a single search query into a vector.
    Uses task_type="retrieval_query" (different from document embedding).
    """
    # 5. FIX TYPO: changed "embeddding" to "embedding"
    return _embed_content(query, "RETRIEVAL_QUERY")
