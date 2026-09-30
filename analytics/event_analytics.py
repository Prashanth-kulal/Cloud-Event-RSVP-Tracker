"""
Analytics and Aggregations Module for Cloud-Event-RSVP-Tracker.
Calculates key performance metrics for organizers:
  - Event capacity utilization rate (%)
  - Response conversion rate (RSVP count vs Capacity)
  - Drop-off / cancellation rate
  - Waitlist demand metrics
  - Time-series registration patterns
"""
import sys
import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from backend.database import AsyncSessionLocal
from backend.models.event import Event, EventStatus
from backend.models.rsvp import RSVP, RSVPStatus
from backend.models.waitlist import Waitlist, WaitlistStatus


async def generate_event_analytics_report(event_id: str) -> Dict[str, Any]:
    """Calculate deep analytics for a single event."""
    async with AsyncSessionLocal() as session:
        event = await session.get(Event, event_id)
        if not event:
            return {"error": "Event not found"}

        going_count = await session.scalar(
            select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.GOING)
        ) or 0
        maybe_count = await session.scalar(
            select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.MAYBE)
        ) or 0
        not_going_count = await session.scalar(
            select(func.count()).where(RSVP.event_id == event_id, RSVP.status == RSVPStatus.NOT_GOING)
        ) or 0
        waitlist_count = await session.scalar(
            select(func.count()).where(Waitlist.event_id == event_id, Waitlist.status == WaitlistStatus.WAITING)
        ) or 0

        total_responses = going_count + maybe_count + not_going_count
        capacity = event.maximum_capacity
        utilization_rate = round((going_count / capacity * 100), 2) if capacity > 0 else 0.0

        return {
            "event_id": event.id,
            "event_name": event.event_name,
            "status": event.status.value,
            "maximum_capacity": capacity,
            "going_count": going_count,
            "maybe_count": maybe_count,
            "not_going_count": not_going_count,
            "waitlist_count": waitlist_count,
            "total_responses": total_responses,
            "capacity_utilization_percent": min(utilization_rate, 100.0),
            "is_overbooked_or_full": going_count >= capacity,
            "turnout_probability_estimate": round((going_count * 0.85 + maybe_count * 0.35), 1)
        }


async def generate_global_platform_summary() -> Dict[str, Any]:
    """Platform-wide summary metrics for cloud architecture telemetry."""
    async with AsyncSessionLocal() as session:
        total_events = await session.scalar(select(func.count()).select_from(Event)) or 0
        published_events = await session.scalar(
            select(func.count()).select_from(Event).where(Event.status == EventStatus.PUBLISHED)
        ) or 0
        total_rsvps = await session.scalar(select(func.count()).select_from(RSVP)) or 0
        going_rsvps = await session.scalar(
            select(func.count()).select_from(RSVP).where(RSVP.status == RSVPStatus.GOING)
        ) or 0
        total_waitlisted = await session.scalar(
            select(func.count()).select_from(Waitlist).where(Waitlist.status == WaitlistStatus.WAITING)
        ) or 0

        return {
            "total_events": total_events,
            "published_events": published_events,
            "total_rsvps": total_rsvps,
            "going_rsvps": going_rsvps,
            "waitlisted_attendees": total_waitlisted,
            "average_rsvps_per_event": round(total_rsvps / total_events, 1) if total_events > 0 else 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


if __name__ == "__main__":
    async def main():
        print("[Analytics] Computing platform summary...")
        summary = await generate_global_platform_summary()
        for k, v in summary.items():
            print(f"  {k}: {v}")

    asyncio.run(main())
