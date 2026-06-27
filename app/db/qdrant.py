# This file sets up our connection to Qdrant 
# and gives us helper functions to store and search vectors.

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import QDRANT_HOST, QDRANT_MODE, QDRANT_PATH, QDRANT_PORT, COLLECTION_NAME
import uuid

# Create one client that the whole app reuses
if QDRANT_MODE == "server":
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
else:
    client = QdrantClient(path=QDRANT_PATH, force_disable_check_same_thread=True)

# Gemini's embedding model outputs vectors of size 768
VECTOR_SIZE = 768


def create_collection_if_not_exist():

    """
    Creates the Qdrant collection (like a table in a regular database)
    only if it doesn't already exist. Safe to call on every startup.

    """
    try:
        existing = [c.name for c in client.get_collections().collections]
    except Exception as exc:
        raise RuntimeError(
            f"Could not connect to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}. "
            "Start Qdrant, or remove QDRANT_MODE=server from .env to use local storage."
        ) from exc

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name= COLLECTION_NAME,
            vectors_config= VectorParams(
                size = VECTOR_SIZE,
                distance= Distance.COSINE # measures similarity between vectors
            
            )
        )
        print(f"Created Collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")

def store_chunks(chunks: list[str],embeddings: list[list[float]], source :str):
    """
    Saves text chunks + their vector embeddings into Qdrant.
    
    chunks     = list of text strings (the actual transcript pieces)
    embeddings = list of vectors (one per chunk, from Gemini)
    source     = filename, so we know which transcript it came from
    """
    points = []

    for chunk, embedding in zip(chunks, embeddings):
        point = PointStruct(
            id = str(uuid.uuid4()),
            vector = embedding,
            payload = {
                "text": chunk,
                "source": source
            }
        )
        points.append(point)

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} chunks from '{source}'")


def search_similar(query_vector: list[float], top_k: int = 5) -> list[str]:

# Finds the top_k most similar chunks to the query vector.
# Returns just the text of those chunks.
    if hasattr(client, "query_points"):
        response = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k
        )
        results = response.points
    else:
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k
        )

    return [result.payload["text"] for result in results]
