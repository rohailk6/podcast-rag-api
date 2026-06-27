from fastapi import APIRouter, HTTPException, Depends
from app.security import verify_api_key
from app.db.postgres import create_session, get_session, get_session_messages

router = APIRouter()


@router.post("/sessions")
async def new_session(user: dict = Depends(verify_api_key)):
    """
    Creates a new conversation session for the authenticated user.
    Returns the session_id — the user passes this to /query.
    """
    session_id = await create_session(user["id"])
    return {
        "session_id": session_id,
        "message": "Session created. Pass session_id to /query."
    }


@router.get("/sessions/{session_id}/history")
async def get_history(session_id: int, user: dict = Depends(verify_api_key)):
    """
    Returns all messages in a session.
    Only the session owner can access it.
    """
    # Verify this session belongs to this user
    session = await get_session(session_id, user["id"])

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found or you don't have access to it."
        )

    messages = await get_session_messages(session_id)

    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": messages
    }