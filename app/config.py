# This is the first real Python file.
# Its only job is to read your .env file and make those values available to the rest of the app.

from dotenv import load_dotenv
import os

load_dotenv() # reads your env file

# os.getenv("KEY") fetches a value by name

GOOGLE_API_KEY= os.getenv("GOOGLE_API_KEY")
QDRANT_MODE=os.getenv("QDRANT_MODE", "local").lower()
QDRANT_HOST=os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT=int(os.getenv("QDRANT_PORT", 6333))
QDRANT_PATH=os.getenv("QDRANT_PATH", "qdrant_data")
COLLECTION_NAME=os.getenv("COLLECTION_NAME", "product_transcripts")
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL") # <- new

# The second argument like "localhost" is a default 
# if the .env doesn't have that key, it falls back to the default
