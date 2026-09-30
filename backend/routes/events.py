"""
Event management routes.
POST   /api/events          — Organizer creates event (DRAFT)
GET    /api/events          — List published events (or all for organizer)
GET    /api/events/{id}     — Get event detail with RSVP counts
PUT    /api/events/{id}     — Organizer updates event
DELETE /api/events/{id}     — Organizer deletes DRAFT event
POST   /api/events/{id}/publish  — Publish event
POST   /api/events/{id}/cancel   — Cancel event
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database import get_db
from backend.models.event import Event, EventStatus
from backend.models.rsvp import RSVP, RSVPStatus
from backend.models.waitlist import Waitlist, WaitlistStatus
from backend.models.user import User
from backend.schemas.schemas import (
    EventCreateRequest, EventUpdateRequest, EventResponse
)
from backend.middleware.auth import get_current_user, require_organizer, get_optional_user
from realtime.realtime_service import manager

router = APIRouter(prefix="/api/events", tags=["events"])


async def _build_event_response(event: Event, db: AsyncSession) -> dict:
    """Build an EventResponse dict with live RSVP count aggregates."""
    going = await db.scalar(
        select(func.count()).where(RSVP.event_id == event.id, RSVP.status == RSVPStatus.GOING)
    ) or 0
    maybe = await db.scalar(
        select(func.count()).where(RSVP.event_id == event.id, RSVP.status == RSVPStatus.MAYBE)
    ) or 0
    not_going = await db.scalar(
        select(func.count()).where(RSVP.event_id == event.id, RSVP.status == RSVPStatus.NOT_GOING)
    ) or 0
    waitlist = await db.scalar(
        select(func.count()).where(Waitlist.event_id == event.id, Waitlist.status == WaitlistStatus.WAITING)
    ) or 0

    organizer_name = None
    if event.organizer:
        organizer_name = event.organizer.name
    else:
        org = await db.get(User, event.organizer_id)
        if org:
            organizer_name = org.name

    return {
        "id": event.id,
        "organizer_id": event.organizer_id,
        "organizer_name": organizer_name,
        "event_name": event.event_name,
        "description": event.description,
        "event_type": event.event_type,
        "event_date": event.event_date,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "venue": event.venue,
        "online_link": event.online_link,
        "maximum_capacity": event.maximum_capacity,
        "registration_deadline": event.registration_deadline,
        "status": event.status,
        "is_online": event.is_online,
        "going_count": going,
        "maybe_count": maybe,
        "not_going_count": not_going,
        "waitlist_count": waitlist,
        "available_seats": max(0, event.maximum_capacity - going),
        "created_at": event.created_at,
    }


@router.post("", status_code=201)
async def create_event(
    req: EventCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Create a new event in DRAFT status."""
    event = Event(
        organizer_id=current_user.id,
        event_name=req.event_name,
        description=req.description,
        event_type=req.event_type,
        event_date=req.event_date,
        start_time=req.start_time,
        end_time=req.end_time,
        venue=req.venue,
        online_link=req.online_link,
        maximum_capacity=req.maximum_capacity,
        registration_deadline=req.registration_deadline,
        is_online=req.is_online,
        status=EventStatus.DRAFT
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return {"success": True, "message": "Event created.", "data": await _build_event_response(event, db)}


@router.get("")
async def list_events(
    status: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """List events — public can see PUBLISHED events; organizers see their own."""
    from sqlalchemy import or_
    stmt = select(Event)

    # Default: show published events
    if status:
        try:
            stmt = stmt.where(Event.status == EventStatus(status.upper()))
        except ValueError:
            pass
    else:
        stmt = stmt.where(Event.status.in_([EventStatus.PUBLISHED, EventStatus.FULL]))

    if event_type:
        from backend.models.event import EventType
        try:
            stmt = stmt.where(Event.event_type == EventType(event_type.upper()))
        except ValueError:
            pass

    if search:
        stmt = stmt.where(or_(
            Event.event_name.ilike(f"%{search}%"),
            Event.description.ilike(f"%{search}%"),
            Event.venue.ilike(f"%{search}%")
        ))

    stmt = stmt.order_by(Event.event_date.asc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    events = result.scalars().all()
    data = [await _build_event_response(e, db) for e in events]
    return {"success": True, "data": data, "total": len(data)}


@router.get("/mine")
async def list_my_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Return all events created by the authenticated organizer."""
    result = await db.execute(
        select(Event).where(Event.organizer_id == current_user.id).order_by(Event.created_at.desc())
    )
    events = result.scalars().all()
    data = [await _build_event_response(e, db) for e in events]
    return {"success": True, "data": data}


@router.get("/{event_id}")
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed event info including RSVP counts."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return {"success": True, "data": await _build_event_response(event, db)}


@router.put("/{event_id}")
async def update_event(
    event_id: str,
    req: EventUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Update event — only the organizer who created it can update."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only modify your own events.")
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot modify a cancelled event.")

    for field, value in req.model_dump(exclude_none=True).items():
        setattr(event, field, value)
    event.updated_at = datetime.now(timezone.utc)
    db.add(event)
    await db.flush()
    await db.refresh(event)

    event_data = await _build_event_response(event, db)
    await manager.broadcast_to_event(event_id, {"type": "EVENT_UPDATED", "data": event_data})
    return {"success": True, "message": "Event updated.", "data": event_data}


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Delete a DRAFT event — only the owning organizer."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own events.")
    if event.status not in (EventStatus.DRAFT, EventStatus.CANCELLED):
        raise HTTPException(status_code=400, detail="Only DRAFT or CANCELLED events can be deleted.")
    await db.delete(event)


@router.post("/{event_id}/publish")
async def publish_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Publish a DRAFT event — makes it visible to attendees."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only publish your own events.")
    if event.status != EventStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only DRAFT events can be published.")
    event.status = EventStatus.PUBLISHED
    event.updated_at = datetime.now(timezone.utc)
    db.add(event)
    await db.flush()
    await db.refresh(event)
    await manager.broadcast_event_status(event_id, "PUBLISHED")
    return {"success": True, "message": "Event published.", "data": await _build_event_response(event, db)}


@router.post("/{event_id}/cancel")
async def cancel_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Cancel an event — notifies all RSVP'd attendees."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own events.")
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Event is already cancelled.")

    event.status = EventStatus.CANCELLED
    event.updated_at = datetime.now(timezone.utc)
    db.add(event)
    await db.flush()

    # Create notifications for all GOING/MAYBE attendees
    from backend.models.notification import Notification, NotificationType
    rsvp_result = await db.execute(
        select(RSVP).where(RSVP.event_id == event_id,
                           RSVP.status.in_([RSVPStatus.GOING, RSVPStatus.MAYBE]))
    )
    for rsvp in rsvp_result.scalars().all():
        notif = Notification(
            user_id=rsvp.user_id,
            event_id=event_id,
            type=NotificationType.EVENT_CANCELLED,
            message=f'Event "{event.event_name}" has been cancelled by the organizer.'
        )
        db.add(notif)

    await manager.broadcast_event_status(event_id, "CANCELLED")
    return {"success": True, "message": "Event cancelled.", "data": await _build_event_response(event, db)}
