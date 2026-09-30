"""
Notification routes.
GET /api/notifications             — Get all notifications for current user
PUT /api/notifications/{id}/read   — Mark a notification as read
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.notification import Notification
from backend.models.user import User
from backend.middleware.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifs = result.scalars().all()
    unread_count = sum(1 for n in notifs if not n.read)
    data = [
        {
            "id": n.id, "event_id": n.event_id, "type": n.type,
            "message": n.message, "read": n.read, "created_at": n.created_at
        }
        for n in notifs
    ]
    return {"success": True, "data": data, "unread_count": unread_count}


@router.put("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = await db.get(Notification, notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    if notif.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another user's notification.")
    notif.read = True
    db.add(notif)
    return {"success": True, "message": "Notification marked as read."}


@router.put("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id, Notification.read == False)  # noqa: E712
    )
    for notif in result.scalars().all():
        notif.read = True
        db.add(notif)
    return {"success": True, "message": "All notifications marked as read."}
