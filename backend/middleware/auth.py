"""
FastAPI dependency for authenticated and role-authorized requests.
Extracts Bearer token from Authorization header, decodes JWT,
and loads the user from the database.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.user import User, UserRole
from backend.utils.jwt_utils import decode_access_token

bearer_scheme = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Decode JWT and return the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Decode JWT and return the user if valid, or None if unauthenticated."""
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        return None
    return user


async def require_organizer(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures the current user is an ORGANIZER or ADMIN."""
    if current_user.role not in (UserRole.ORGANIZER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires ORGANIZER role."
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures the current user is an ADMIN."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires ADMIN role."
        )
    return current_user
