"""
Integration tests for Event CRUD and publishing workflows.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_organizer_create_and_publish_event(client: AsyncClient, organizer_token: str):
    headers = {"Authorization": f"Bearer {organizer_token}"}
    create_payload = {
        "event_name": "Kubernetes Deep Dive",
        "description": "Production grade K8s deployment best practices.",
        "event_type": "WORKSHOP",
        "event_date": "2026-11-20",
        "start_time": "10:00:00",
        "end_time": "16:00:00",
        "venue": "San Francisco Tech Center",
        "maximum_capacity": 50,
        "is_online": False
    }

    # 1. Create event (DRAFT status by default)
    res = await client.post("/api/events", json=create_payload, headers=headers)
    assert res.status_code == 201
    event_id = res.json()["data"]["id"]
    assert res.json()["data"]["status"] == "DRAFT"

    # 2. Publish event (POST)
    pub_res = await client.post(f"/api/events/{event_id}/publish", headers=headers)
    assert pub_res.status_code == 200
    assert pub_res.json()["data"]["status"] == "PUBLISHED"

    # 3. Public list should now show it
    list_res = await client.get("/api/events")
    assert list_res.status_code == 200
    events = list_res.json()["data"]
    assert any(e["id"] == event_id for e in events)


@pytest.mark.asyncio
async def test_attendee_cannot_create_event(client: AsyncClient, attendee_token: str):
    headers = {"Authorization": f"Bearer {attendee_token}"}
    create_payload = {
        "event_name": "Unauthorized Event",
        "event_type": "MEETUP",
        "event_date": "2026-12-01",
        "start_time": "12:00:00",
        "maximum_capacity": 10
    }
    res = await client.post("/api/events", json=create_payload, headers=headers)
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_organizer_cannot_modify_others_event(
    client: AsyncClient, organizer_token: str, db_session
):
    from backend.models.user import User, UserRole
    from backend.models.event import Event, EventStatus, EventType
    from backend.utils.password import hash_password
    import datetime

    # Create another organizer and an event owned by them
    other_org = User(
        name="Other Org",
        email="other_org@test.com",
        password_hash=hash_password("Pass123!"),
        role=UserRole.ORGANIZER
    )
    db_session.add(other_org)
    await db_session.flush()

    other_event = Event(
        organizer_id=other_org.id,
        event_name="Other's Event",
        event_type=EventType.WORKSHOP,
        event_date=datetime.date(2026, 11, 20),
        start_time=datetime.time(10, 0),
        maximum_capacity=20,
        status=EventStatus.PUBLISHED
    )
    db_session.add(other_event)
    await db_session.commit()

    headers = {"Authorization": f"Bearer {organizer_token}"}
    res = await client.post(f"/api/events/{other_event.id}/cancel", headers=headers)
    assert res.status_code == 403
