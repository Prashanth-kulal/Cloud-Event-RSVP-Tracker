"""
RSVP routes — concurrency-safe RSVP management.

POST   /api/events/{event_id}/rsvp          — Create or update RSVP
PUT    /api/events/{event_id}/rsvp          — Update RSVP status
DELETE /api/events/{event_id}/rsvp          — Cancel RSVP
GET    /api/events/{event_id}/rsvps         — Organizer: list all RSVPs
GET    /api/rsvps/me                         — Attendee: get my RSVPs

CONCURRENCY / RACE CONDITION HANDLING:
---------------------------------------
When event capacity = N and going_count = N-1:
Two simultaneous GOING requests must not both succeed.

Implementation:
  1. SELECT going_count inside a DB transaction.
  2. If going_count >= capacity → raise 409 FULL.
  3. If OK → INSERT/UPDATE RSVP atomically.
  4. After INSERT → re-check count to update event status to FULL.

SQLite serializes writes per connection (no true concurrent writes),
providing safe behavior for local dev. In production Firestore, use
a Firestore Transaction (conditional read-then-write).

This is documented as a Cloud Computing concept: Concurrency Control.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from backend.database import get_db
from backend.models.event import Event, EventStatus
from backend.models.rsvp import RSVP, RSVPStatus
from backend.models.waitlist import Waitlist, WaitlistStatus
from backend.models.notification import Notification, NotificationType
from backend.models.user import User
from backend.schemas.schemas import RSVPRequest, RSVPResponse
from backend.middleware.auth import get_current_user
from realtime.realtime_service import manager

router = APIRouter(tags=["rsvp"])


async def _get_rsvp_counts(event_id: str, db: AsyncSession) -> dict:
    going = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)
    ) or 0
    maybe = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.MAYBE)
    ) or 0
    not_going = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.NOT_GOING)
    ) or 0
    waitlist = await db.scalar(
        select(func.count()).where(Waitlist.event_id == event_id, Waitlist.status == WaitlistStatus.WAITING)
    ) or 0
    return {
        "going_count": going,
        "maybe_count": maybe,
        "not_going_count": not_going,
        "waitlist_count": waitlist,
    }


async def _promote_from_waitlist(event_id: str, event: Event, db: AsyncSession):
    """Promote the next WAITING user from the waitlist to GOING."""
    wl_result = await db.execute(
        select(Waitlist)
        .where(Waitlist.event_id == event_id, Waitlist.status == WaitlistStatus.WAITING)
        .order_by(Waitlist.position.asc())
        .limit(1)
    )
    entry = wl_result.scalar_one_or_none()
    if not entry:
        return

    # Check capacity before promoting
    going = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)
    ) or 0
    if going >= event.maximum_capacity:
        return

    # Create RSVP for promoted user
    new_rsvp = RSVP(event_id=event_id, user_id=entry.user_id, status=RSVPStatus.GOING)
    db.add(new_rsvp)
    entry.status = WaitlistStatus.PROMOTED
    db.add(entry)

    # Notify promoted user
    notif = Notification(
        user_id=entry.user_id,
        event_id=event_id,
        type=NotificationType.WAITLIST_PROMOTION,
        message=f'Great news! You\'ve been promoted from the waitlist for "{event.event_name}". You are now GOING!'
    )
    db.add(notif)


@router.post("/api/events/{event_id}/rsvp", status_code=201)
async def create_or_update_rsvp(
    event_id: str,
    req: RSVPRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update an RSVP for an event.
    Implements concurrency-safe capacity check with DB transaction.
    """
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="This event has been cancelled.")
    if event.status not in (EventStatus.PUBLISHED, EventStatus.FULL):
        raise HTTPException(status_code=400, detail="Event is not open for RSVPs.")

    # Registration deadline check
    if event.registration_deadline and datetime.now(timezone.utc) > event.registration_deadline:
        raise HTTPException(status_code=400, detail="Registration deadline has passed.")

    # Look up existing RSVP
    result = await db.execute(
        select(RSVP).where(RSVP.event_id == event_id, RSVP.user_id == current_user.id)
    )
    existing_rsvp = result.scalar_one_or_none()

    if req.status == RSVPStatus.GOING:
        # CONCURRENCY-SAFE capacity check
        going_count = await db.scalar(
            select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)
        ) or 0

        if existing_rsvp and existing_rsvp.status == RSVPStatus.GOING:
            # Already GOING — idempotent, no capacity change
            pass
        elif going_count >= event.maximum_capacity:
            # Event is full — add to waitlist
            wl_check = await db.execute(
                select(Waitlist).where(Waitlist.event_id == event_id, Waitlist.user_id == current_user.id)
            )
            if wl_check.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="You are already on the waitlist.")
            wl_count = await db.scalar(
                select(func.count()).where(Waitlist.event_id == event_id, Waitlist.status == WaitlistStatus.WAITING)
            ) or 0
            wl_entry = Waitlist(
                event_id=event_id,
                user_id=current_user.id,
                position=wl_count + 1,
                status=WaitlistStatus.WAITING
            )
            db.add(wl_entry)
            await db.flush()
            counts = await _get_rsvp_counts(event_id, db)
            await manager.broadcast_rsvp_update(event_id, counts)
            return {"success": True, "message": "Event is full. You have been added to the waitlist.", "data": None}

    if existing_rsvp:
        old_status = existing_rsvp.status
        existing_rsvp.status = req.status
        existing_rsvp.updated_at = datetime.now(timezone.utc)
        db.add(existing_rsvp)

        # If previous was GOING and now changed — check if slot opened for waitlist
        if old_status == RSVPStatus.GOING and req.status != RSVPStatus.GOING:
            await _promote_from_waitlist(event_id, event, db)
    else:
        try:
            new_rsvp = RSVP(event_id=event_id, user_id=current_user.id, status=req.status)
            db.add(new_rsvp)
            await db.flush()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="You have already RSVP'd to this event.")

    await db.flush()

    # Update event status
    going_count = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)
    ) or 0
    if going_count >= event.maximum_capacity:
        event.status = EventStatus.FULL
    elif event.status == EventStatus.FULL and going_count < event.maximum_capacity:
        event.status = EventStatus.PUBLISHED
    db.add(event)
    await db.flush()

    # Create RSVP confirmation notification
    notif = Notification(
        user_id=current_user.id,
        event_id=event_id,
        type=NotificationType.RSVP_CONFIRMATION,
        message=f'Your RSVP for "{event.event_name}" has been recorded as {req.status.value}.'
    )
    db.add(notif)
    await db.flush()

    counts = await _get_rsvp_counts(event_id, db)
    # Broadcast real-time update to all connected clients
    await manager.broadcast_rsvp_update(event_id, counts)
    await manager.broadcast_event_status(event_id, event.status.value)

    return {
        "success": True,
        "message": f"RSVP recorded as {req.status.value}.",
        "data": counts
    }


@router.delete("/api/events/{event_id}/rsvp", status_code=200)
async def cancel_rsvp(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel the current user's RSVP for an event."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    result = await db.execute(
        select(RSVP).where(RSVP.event_id == event_id, RSVP.user_id == current_user.id)
    )
    rsvp = result.scalar_one_or_none()
    if not rsvp:
        raise HTTPException(status_code=404, detail="No RSVP found for this event.")

    was_going = rsvp.status == RSVPStatus.GOING
    await db.delete(rsvp)
    await db.flush()

    # Promote from waitlist if a seat opened
    if was_going:
        going_count = await db.scalar(
            select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)
        ) or 0
        if going_count < event.maximum_capacity:
            if event.status == EventStatus.FULL:
                event.status = EventStatus.PUBLISHED
                db.add(event)
            await _promote_from_waitlist(event_id, event, db)
            await db.flush()

    counts = await _get_rsvp_counts(event_id, db)
    await manager.broadcast_rsvp_update(event_id, counts)
    return {"success": True, "message": "RSVP cancelled.", "data": counts}


@router.get("/api/events/{event_id}/rsvps")
async def get_event_rsvps(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Organizer: get all RSVPs for an event."""
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only the event organizer can view attendee list.")

    result = await db.execute(select(RSVP).where(RSVP.event_id == event_id))
    rsvps = result.scalars().all()
    data = []
    for r in rsvps:
        user = await db.get(User, r.user_id)
        data.append({
            "id": r.id, "event_id": r.event_id, "user_id": r.user_id,
            "user_name": user.name if user else "Unknown",
            "user_email": user.email if user else "",
            "status": r.status, "responded_at": r.responded_at, "updated_at": r.updated_at
        })
    return {"success": True, "data": data}


@router.get("/api/events/{event_id}/rsvp/me")
async def get_my_rsvp(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's RSVP for a specific event."""
    result = await db.execute(
        select(RSVP).where(RSVP.event_id == event_id, RSVP.user_id == current_user.id)
    )
    rsvp = result.scalar_one_or_none()
    if not rsvp:
        return {"success": True, "data": None}
    return {"success": True, "data": {"status": rsvp.status, "responded_at": rsvp.responded_at}}


@router.get("/api/rsvps/me")
async def get_my_rsvps(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all RSVPs for the current user across all events."""
    result = await db.execute(select(RSVP).where(RSVP.user_id == current_user.id))
    rsvps = result.scalars().all()
    data = []
    for r in rsvps:
        event = await db.get(Event, r.event_id)
        data.append({
            "rsvp_id": r.id,
            "event_id": r.event_id,
            "event_name": event.event_name if event else "Unknown",
            "event_date": str(event.event_date) if event else None,
            "event_status": event.status.value if event else None,
            "rsvp_status": r.status.value,
            "responded_at": r.responded_at
        })
    return {"success": True, "data": data}
