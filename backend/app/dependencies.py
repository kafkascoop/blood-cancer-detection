from typing import Optional

from fastapi import Cookie, HTTPException, status
from bson import ObjectId

from app.services.auth import decode_access_token
from app.database import get_users_collection


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
) -> dict:
    """FastAPI dependency to get the authenticated user from the JWT cookie."""
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_access_token(access_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    users_collection = await get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
