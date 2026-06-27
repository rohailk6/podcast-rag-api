from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from app.db.postgres import get_user_by_api_key

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(authorization: Optional[str] = Security(api_key_header)):
    """
    Now checks the API key against the database instead of .env.
    Returns the full user record so routes know who is calling.
    """
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header must start with 'Bearer '."
        )

    # Strip the "Bearer " prefix to get the raw key
    api_key = authorization[len("Bearer "):]

    # Look up the key in the database
    user = await get_user_by_api_key(api_key)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key."
        )

    # Return the user dict — routes receive this via Depends()
    # This is how /query knows which user is asking
    return dict(user)