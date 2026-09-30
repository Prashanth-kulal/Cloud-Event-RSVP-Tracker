"""
Integration tests for Announcements and Notifications API.
"""
import pytest
import datetime
from httpx import AsyncClient

from backend.models.event import Event, EventStatus, EventType
from backend.models.user import User


@pytest.mark.asyncio
async def test_announcements_and_notifications_flow(
    client: AsyncClient, db_session, organizer_user: User, attendee_user: User,
    organizer_token: str, attendee_token: str
):
    # Create event
    event = Event(
        organizer_id=organizer_user.id,
        event_name="Cloud Security Hands-on",
        event_type=EventType.WORKSHOP,
        event_date=datetime.date(2026, 12, 1),
        start_time=datetime.time(14, 0),
        maximum_capacity=50,
        status=EventStatus.PUBLISHED
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    org_headers = {"Authorization": f"Bearer {organizer_token}"}
    att_headers = {"Authorization": f"Bearer {attendee_token}"}

    # Organizer posts announcement
    ann_payload = {
        "title": "Room Changed to Hall B",
        "message": "Please note we have moved to Hall B on the 2nd floor."
    }
    ann_res = await client.post(
        f"/api/events/{event.id}/announcements",
        json=ann_payload,
        headers=org_headers
    )
    assert ann_res.status_code == 201
    assert ann_res.json()["data"]["title"] == "Room Changed to Hall B"

    # Anyone can fetch announcements
    list_res = await client.get(f"/api/events/{event.id}/announcements")
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1

    # Attendee checks notifications
    notif_res = await client.get("/api/notifications", headers=att_headers)
    assert notif_res.status_code == 200
    assert "data" in notif_res.json()
