import google.generativeai as genai
from app.config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_answers(question: str, context_chunks: list[str], history: list = None) -> str:
    """
    Builds a RAG prompt that includes:
    1. The transcript context (retrieved from Qdrant)
    2. The conversation history (retrieved from PostgreSQL)
    3. The current question
    
    This gives Gemini memory of the conversation so answers
    can reference previous questions naturally.
    """
    context = "\n\n---\n\n".join(context_chunks)

    # Format conversation history into readable text
    history_text = ""
    if history:
        history_lines = []
        for msg in history:
            # role is "user" or "assistant"
            label = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{label}: {msg['content']}")
        history_text = "\n".join(history_lines)

    # Build the full prompt
    if history_text:
        prompt = f"""You are a helpful assistant that answers questions about podcast transcripts.

Use ONLY the transcript context below to answer questions.
If the answer isn't in the context, say "I couldn't find that in the transcript."

TRANSCRIPT CONTEXT:
{context}

CONVERSATION HISTORY:
{history_text}

CURRENT QUESTION:
{question}

ANSWER:"""
    else:
        # No history yet — simpler prompt for first message
        prompt = f"""You are a helpful assistant that answers questions about podcast transcripts.

Use ONLY the transcript context below to answer the question.
If the answer isn't in the context, say "I couldn't find that in the transcript."

TRANSCRIPT CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    response = model.generate_content(prompt)
    return response.text