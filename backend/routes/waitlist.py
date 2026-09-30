"""
Waitlist routes.
GET /api/events/{event_id}/waitlist  — Organizer: view waitlist
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.event import Event
from backend.models.waitlist import Waitlist
from backend.models.user import User
from backend.middleware.auth import get_current_user

router = APIRouter(tags=["waitlist"])


@router.get("/api/events/{event_id}/waitlist")
async def get_waitlist(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only the event organizer can view the waitlist.")

    result = await db.execute(
        select(Waitlist).where(Waitlist.event_id == event_id).order_by(Waitlist.position.asc())
    )
    entries = result.scalars().all()
    data = []
    for e in entries:
        user = await db.get(User, e.user_id)
        data.append({
            "id": e.id, "position": e.position, "status": e.status,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "",
            "joined_at": e.joined_at
        })
    return {"success": True, "data": data}


@router.delete("/api/events/{event_id}/waitlist")
async def leave_waitlist(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allow a user to remove themselves from the waitlist."""
    result = await db.execute(
        select(Waitlist).where(Waitlist.event_id == event_id, Waitlist.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="You are not on the waitlist for this event.")
    await db.delete(entry)
    return {"success": True, "message": "Removed from waitlist."}
