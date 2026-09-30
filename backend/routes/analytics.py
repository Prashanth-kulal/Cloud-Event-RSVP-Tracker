"""
Analytics routes.
GET /api/events/{event_id}/analytics  — Organizer analytics for an event
GET /api/analytics/dashboard          — Organizer platform dashboard summary
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.event import Event, EventStatus
from backend.models.rsvp import RSVP, RSVPStatus
from backend.models.waitlist import Waitlist, WaitlistStatus
from backend.models.user import User
from backend.middleware.auth import get_current_user, require_organizer

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/events/{event_id}")
async def get_event_analytics(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")
    if event.organizer_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only the event organizer can view analytics.")

    going = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)
    ) or 0
    maybe = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.MAYBE)
    ) or 0
    not_going = await db.scalar(
        select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.NOT_GOING)
    ) or 0
    waitlist_count = await db.scalar(
        select(func.count()).where(Waitlist.event_id == event_id, Waitlist.status == WaitlistStatus.WAITING)
    ) or 0

    total_responses = going + maybe + not_going
    available_seats = max(0, event.maximum_capacity - going)
    response_rate = round((total_responses / event.maximum_capacity) * 100, 1) if event.maximum_capacity > 0 else 0
    capacity_utilization = round((going / event.maximum_capacity) * 100, 1) if event.maximum_capacity > 0 else 0

    # RSVP timeline — group by date
    rsvp_result = await db.execute(
        select(RSVP).where(RSVP.event_id == event_id).order_by(RSVP.responded_at.asc())
    )
    rsvps = rsvp_result.scalars().all()
    timeline: dict = {}
    for r in rsvps:
        day = r.responded_at.strftime("%Y-%m-%d")
        if day not in timeline:
            timeline[day] = {"date": day, "going": 0, "maybe": 0, "not_going": 0}
        if r.status == RSVPStatus.GOING:
            timeline[day]["going"] += 1
        elif r.status == RSVPStatus.MAYBE:
            timeline[day]["maybe"] += 1
        else:
            timeline[day]["not_going"] += 1

    return {
        "success": True,
        "data": {
            "event_id": event_id,
            "event_name": event.event_name,
            "maximum_capacity": event.maximum_capacity,
            "going_count": going,
            "maybe_count": maybe,
            "not_going_count": not_going,
            "waitlist_count": waitlist_count,
            "total_responses": total_responses,
            "available_seats": available_seats,
            "response_rate": response_rate,
            "capacity_utilization": capacity_utilization,
            "rsvp_timeline": list(timeline.values())
        }
    }


@router.get("/dashboard")
async def get_organizer_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Organizer dashboard summary across all their events."""
    result = await db.execute(
        select(Event).where(Event.organizer_id == current_user.id)
    )
    events = result.scalars().all()
    total_events = len(events)
    upcoming_events = sum(1 for e in events if e.status == EventStatus.PUBLISHED and e.event_date >= datetime.now(timezone.utc).date())
    cancelled_events = sum(1 for e in events if e.status == EventStatus.CANCELLED)

    total_going = 0
    total_maybe = 0
    total_not_going = 0
    total_capacity = 0

    for e in events:
        going = await db.scalar(
            select(func.count()).where(RSVP.event_id == e.id, RSVP.status == RSVPStatus.GOING)
        ) or 0
        maybe = await db.scalar(
            select(func.count()).where(RSVP.event_id == e.id, RSVP.status == RSVPStatus.MAYBE)
        ) or 0
        not_going = await db.scalar(
            select(func.count()).where(RSVP.event_id == e.id, RSVP.status == RSVPStatus.NOT_GOING)
        ) or 0
        total_going += going
        total_maybe += maybe
        total_not_going += not_going
        total_capacity += e.maximum_capacity

    total_responses = total_going + total_maybe + total_not_going
    response_rate = round((total_responses / total_capacity) * 100, 1) if total_capacity > 0 else 0

    return {
        "success": True,
        "data": {
            "total_events": total_events,
            "upcoming_events": upcoming_events,
            "cancelled_events": cancelled_events,
            "total_going": total_going,
            "total_maybe": total_maybe,
            "total_not_going": total_not_going,
            "total_responses": total_responses,
            "total_capacity": total_capacity,
            "response_rate": response_rate
        }
    }
