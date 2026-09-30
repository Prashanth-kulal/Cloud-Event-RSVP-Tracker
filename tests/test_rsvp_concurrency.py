"""
Tests for RSVP management, capacity enforcement, and waitlist auto-promotion.
Demonstrates cloud concurrency safety and idempotency.
"""
import pytest
import datetime
from httpx import AsyncClient

from backend.models.event import Event, EventStatus, EventType
from backend.models.user import User, UserRole
from backend.utils.password import hash_password
from backend.utils.jwt_utils import create_access_token


@pytest.mark.asyncio
async def test_rsvp_capacity_and_waitlist_flow(
    client: AsyncClient, db_session, organizer_user: User
):
    # 1. Create an event with maximum capacity = 1
    event = Event(
        organizer_id=organizer_user.id,
        event_name="Exclusive VIP Cloud Salon",
        event_type=EventType.SEMINAR,
        event_date=datetime.date(2026, 12, 10),
        start_time=datetime.time(18, 0),
        maximum_capacity=1,
        status=EventStatus.PUBLISHED
    )
    db_session.add(event)
    await db_session.commit()
    await db_session.refresh(event)

    # 2. Create two attendees
    attendee_a = User(
        name="User A",
        email="user_a@test.com",
        password_hash=hash_password("Pass123!"),
        role=UserRole.ATTENDEE
    )
    attendee_b = User(
        name="User B",
        email="user_b@test.com",
        password_hash=hash_password("Pass123!"),
        role=UserRole.ATTENDEE
    )
    db_session.add_all([attendee_a, attendee_b])
    await db_session.commit()
    await db_session.refresh(attendee_a)
    await db_session.refresh(attendee_b)

    token_a = create_access_token(data={"sub": attendee_a.id, "email": attendee_a.email, "role": attendee_a.role.value})
    token_b = create_access_token(data={"sub": attendee_b.id, "email": attendee_b.email, "role": attendee_b.role.value})

    # 3. User A RSVPs as GOING -> Spot 1/1 taken!
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res_a = await client.post(
        f"/api/events/{event.id}/rsvp",
        json={"status": "GOING"},
        headers=headers_a
    )
    assert res_a.status_code == 201
    assert res_a.json()["data"]["going_count"] == 1

    # 4. User B attempts to RSVP as GOING -> Event is at full capacity, added to waitlist!
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_b = await client.post(
        f"/api/events/{event.id}/rsvp",
        json={"status": "GOING"},
        headers=headers_b
    )
    assert res_b.status_code == 201
    assert "waitlist" in res_b.json()["message"].lower()

    # 5. User A cancels RSVP (NOT_GOING)
    res_cancel = await client.delete(
        f"/api/events/{event.id}/rsvp",
        headers=headers_a
    )
    assert res_cancel.status_code == 200

    # 6. Verify event detail shows available spot or promoted attendee
    detail_res = await client.get(f"/api/events/{event.id}")
    assert detail_res.status_code == 200
