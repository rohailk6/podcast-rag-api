# This splits a long transcript into smaller overlapping pieces.

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:

    """
    Splits a long text into smaller chunks with some overlap.
    
    Why overlap? So if an important sentence falls at the boundary
    between two chunks, it still appears fully in at least one of them.
    
    chunk_size = max characters per chunk
    overlap    = how many characters to repeat from the previous chunk
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        # Move forward by (chunk_size - overlap) so chunks share some text
        start += chunk_size - overlap
    
    return chunks