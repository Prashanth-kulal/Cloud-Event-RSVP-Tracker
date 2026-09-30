"""
Announcement routes.
POST /api/events/{event_id}/announcements  — Organizer creates announcement
GET  /api/events/{event_id}/announcements  — Everyone sees announcements
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.event import Event, EventStatus
from backend.models.announcement import Announcement
from backend.models.user import User
from backend.schemas.schemas import AnnouncementCreateRequest
from backend.middleware.auth import get_current_user
from realtime.realtime_service import manager

router = APIRouter(tags=["announcements"])


@router.post("/api/events/{event_id}/announcements", status_code=201)
async def create_announcement(
    event_id: str,
    req: AnnouncementCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only the event organizer can create announcements.")
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot add announcements to a cancelled event.")

    ann = Announcement(
        event_id=event_id,
        created_by=current_user.id,
        title=req.title,
        message=req.message
    )
    db.add(ann)
    await db.flush()
    await db.refresh(ann)

    ann_data = {
        "id": ann.id, "event_id": ann.event_id, "title": ann.title,
        "message": ann.message, "created_at": str(ann.created_at)
    }

    # Broadcast to real-time subscribers
    await manager.broadcast_announcement(event_id, ann_data)

    # Notify all GOING/MAYBE attendees
    from backend.models.rsvp import RSVP, RSVPStatus
    from backend.models.notification import Notification, NotificationType
    rsvp_result = await db.execute(
        select(RSVP).where(RSVP.event_id == event_id,
                           RSVP.status.in_([RSVPStatus.GOING, RSVPStatus.MAYBE]))
    )
    for rsvp in rsvp_result.scalars().all():
        notif = Notification(
            user_id=rsvp.user_id,
            event_id=event_id,
            type=NotificationType.ANNOUNCEMENT,
            message=f'New announcement for "{event.event_name}": {req.title}'
        )
        db.add(notif)

    return {"success": True, "message": "Announcement created.", "data": ann_data}


@router.get("/api/events/{event_id}/announcements")
async def get_announcements(event_id: str, db: AsyncSession = Depends(get_db)):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    result = await db.execute(
        select(Announcement).where(Announcement.event_id == event_id)
        .order_by(Announcement.created_at.desc())
    )
    anns = result.scalars().all()
    data = []
    for a in anns:
        data.append({
            "id": a.id, "event_id": a.event_id, "title": a.title,
            "message": a.message, "created_by": a.created_by, "created_at": a.created_at
        })
    return {"success": True, "data": data}
