from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.db.postgres import create_user

router = APIRouter()


class CreateUserRequest(BaseModel):
    name: str
    email: str    


@router.post("/users")
async def register_user(request: CreateUserRequest):
    """
    Creates a new user and returns their API key.
    
    IMPORTANT: The API key is shown exactly once here.
    It is not stored in plain text in the database.
    The user must copy and save it immediately.
    """
    try:
        user = await create_user(request.name, request.email)
    except Exception as exc:
        # Duplicate email triggers this
        raise HTTPException(
            status_code=400,
            detail=f"Could not create user: {exc}"
        )

    return {
        "message": "User created. Save your API key — it won't be shown again.",
        "user": user
    }