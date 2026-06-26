from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from bson import ObjectId

from app.models.user import UserCreate, UserLogin, UserResponse
from app.services.auth import hash_password, verify_password, create_access_token
from app.database import get_users_collection
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _user_to_response(user: dict) -> UserResponse:
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        full_name=user["full_name"],
        created_at=user["created_at"],
    )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    users_collection = await get_users_collection()

    existing = await users_collection.find_one({
        "$or": [{"email": user_data.email}, {"username": user_data.username}]
    })
    if existing:
        if existing["email"] == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail="Username already taken")

    now = datetime.now(timezone.utc)
    user_doc = {
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "created_at": now,
        "updated_at": now,
    }

    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return _user_to_response(user_doc)


@router.post("/login")
async def login(user_data: UserLogin, response: Response):
    """Log in and set a httpOnly JWT cookie."""
    users_collection = await get_users_collection()
    user = await users_collection.find_one({
        "$or": [{"email": user_data.username}, {"username": user_data.username}]
    })

    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user["_id"])})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
        secure=False,  # Set True in production with HTTPS
    )

    return {
        "message": "Login successful",
        "user": _user_to_response(user).model_dump(),
    }


@router.post("/logout")
async def logout(response: Response):
    """Log out by clearing the JWT cookie."""
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get the currently authenticated user."""
    return _user_to_response(current_user)
