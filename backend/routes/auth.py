"""
Auth routes: /api/auth/register, /api/auth/login, /api/auth/me
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.user import User
from backend.schemas.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse, UpdateProfileRequest
)
from backend.utils.password import hash_password, verify_password
from backend.utils.jwt_utils import create_access_token
from backend.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=dict, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user. Prevents duplicate email."""
    result = await db.execute(select(User).where(User.email == req.email.lower()))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(
        name=req.name,
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        role=req.role
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    token = create_access_token({"sub": user.id, "role": user.role.value})
    return {
        "success": True,
        "message": "Account created successfully.",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump()
        }
    }


@router.post("/login", response_model=dict)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user with email/password. Returns JWT."""
    result = await db.execute(select(User).where(User.email == req.email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")
    token = create_access_token({"sub": user.id, "role": user.role.value})
    return {
        "success": True,
        "message": "Login successful.",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user).model_dump()
        }
    }


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return {
        "success": True,
        "data": UserResponse.model_validate(current_user).model_dump()
    }


@router.put("/me", response_model=dict)
async def update_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update authenticated user's profile."""
    if req.name:
        current_user.name = req.name.strip()
    if req.profile_picture is not None:
        current_user.profile_picture = req.profile_picture
    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return {
        "success": True,
        "message": "Profile updated.",
        "data": UserResponse.model_validate(current_user).model_dump()
    }
