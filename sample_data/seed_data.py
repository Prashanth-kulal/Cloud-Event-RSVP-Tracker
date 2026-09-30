"""
Sample Data Seeder for Real-Time Cloud-Based Event Planning & RSVP Tracker.
Populates:
  - 5 Users (Organizers and Attendees)
  - 5 Events across multiple categories (Tech Summit, Hackathon, Cloud Workshop, etc.)
  - Realistic RSVPs with varied statuses (GOING, MAYBE, NOT_GOING)
  - Waitlist entries demonstrating FIFO auto-promotion
  - Organizer announcements
  - In-app notifications
"""
import asyncio
import datetime
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from backend.database import AsyncSessionLocal, init_db
from backend.models.user import User, UserRole
from backend.models.event import Event, EventStatus, EventType
from backend.models.rsvp import RSVP, RSVPStatus
from backend.models.waitlist import Waitlist, WaitlistStatus
from backend.models.announcement import Announcement
from backend.models.notification import Notification, NotificationType
from backend.utils.password import hash_password


async def seed():
    print("[Seed] Initializing database tables...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(User))
        if result.scalars().first():
            print("[Seed] Database already contains data. Skipping seed.")
            return

        print("[Seed] Creating users...")
        organizer1 = User(
            name="Sarah Connor",
            email="sarah@cloudnative.io",
            password_hash=hash_password("Password123!"),
            role=UserRole.ORGANIZER,
            profile_picture="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=256&q=80"
        )
        organizer2 = User(
            name="Alex Mercer",
            email="alex@devops.org",
            password_hash=hash_password("Password123!"),
            role=UserRole.ORGANIZER,
            profile_picture="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=256&q=80"
        )
        attendee1 = User(
            name="Elena Rostova",
            email="elena@techflow.dev",
            password_hash=hash_password("Password123!"),
            role=UserRole.ATTENDEE,
            profile_picture="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80"
        )
        attendee2 = User(
            name="David Chen",
            email="david@dataminds.ai",
            password_hash=hash_password("Password123!"),
            role=UserRole.ATTENDEE,
            profile_picture="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=256&q=80"
        )
        attendee3 = User(
            name="Marcus Vance",
            email="marcus@cybersec.co",
            password_hash=hash_password("Password123!"),
            role=UserRole.ATTENDEE,
            profile_picture="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=256&q=80"
        )

        session.add_all([organizer1, organizer2, attendee1, attendee2, attendee3])
        await session.flush()

        print("[Seed] Creating events...")
        today = datetime.date.today()
        event1 = Event(
            organizer_id=organizer1.id,
            event_name="Global Cloud & Kubernetes Summit 2026",
            description="A premier cloud conference bringing together 500+ cloud architects, SREs, and platform engineers. Hands-on labs on distributed tracing, multi-region failover, and serverless architectures.",
            event_type=EventType.CONFERENCE,
            event_date=today + datetime.timedelta(days=14),
            start_time=datetime.time(9, 0),
            end_time=datetime.time(17, 30),
            venue="Moscone Center, San Francisco & Online Virtual Hub",
            maximum_capacity=150,
            status=EventStatus.PUBLISHED,
            is_online=True,
            online_link="https://cloudsummit2026.io/stream"
        )

        event2 = Event(
            organizer_id=organizer1.id,
            event_name="Real-Time Distributed Systems Workshop",
            description="Deep dive into real-time architectures: WebSockets, Redis Pub/Sub, Firestore event streaming, and state synchronization under high concurrency.",
            event_type=EventType.WORKSHOP,
            event_date=today + datetime.timedelta(days=7),
            start_time=datetime.time(14, 0),
            end_time=datetime.time(17, 0),
            venue="Virtual Classroom 1",
            maximum_capacity=2,  # Intentionally small capacity to demonstrate FULL status and Waitlist
            status=EventStatus.FULL,
            is_online=True,
            online_link="https://meet.google.com/cloud-rsvp-workshop"
        )

        event3 = Event(
            organizer_id=organizer2.id,
            event_name="Cloud AI & Agentic Workflows Hackathon",
            description="48-hour challenge building intelligent agentic systems powered by generative AI and cloud serverless compute. Prizes worth $25,000.",
            event_type=EventType.MEETUP,
            event_date=today + datetime.timedelta(days=30),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(20, 0),
            venue="Seattle Tech Center, 400 Pine St, Seattle, WA",
            maximum_capacity=80,
            status=EventStatus.PUBLISHED,
            is_online=False
        )

        event4 = Event(
            organizer_id=organizer2.id,
            event_name="Zero-Trust Cloud Security Masterclass",
            description="Comprehensive guide to securing microservices, IAM fine-grained policies, and automated vulnerability scanning across AWS and GCP environments.",
            event_type=EventType.WEBINAR,
            event_date=today + datetime.timedelta(days=21),
            start_time=datetime.time(18, 0),
            end_time=datetime.time(20, 0),
            venue="Online Webinar Studio",
            maximum_capacity=200,
            status=EventStatus.PUBLISHED,
            is_online=True,
            online_link="https://zoom.us/j/cloud-sec-masterclass"
        )

        event5 = Event(
            organizer_id=organizer1.id,
            event_name="Enterprise Cloud Migration Roundtable (Draft)",
            description="Exclusive invitation-only discussion on legacy monolith decomposition and multi-cloud strategies.",
            event_type=EventType.SEMINAR,
            event_date=today + datetime.timedelta(days=45),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(13, 0),
            venue="Tech Club Lounge, New York, NY",
            maximum_capacity=20,
            status=EventStatus.DRAFT,
            is_online=False
        )

        session.add_all([event1, event2, event3, event4, event5])
        await session.flush()

        print("[Seed] Creating RSVPs...")
        # Event 1: Attendees registering
        rsvp1 = RSVP(event_id=event1.id, user_id=attendee1.id, status=RSVPStatus.GOING)
        rsvp2 = RSVP(event_id=event1.id, user_id=attendee2.id, status=RSVPStatus.GOING)
        rsvp3 = RSVP(event_id=event1.id, user_id=attendee3.id, status=RSVPStatus.MAYBE)

        # Event 2: Capacity is 2. Both spots filled by attendee1 and attendee2
        rsvp4 = RSVP(event_id=event2.id, user_id=attendee1.id, status=RSVPStatus.GOING)
        rsvp5 = RSVP(event_id=event2.id, user_id=attendee2.id, status=RSVPStatus.GOING)

        # Event 3:
        rsvp6 = RSVP(event_id=event3.id, user_id=attendee3.id, status=RSVPStatus.GOING)

        session.add_all([rsvp1, rsvp2, rsvp3, rsvp4, rsvp5, rsvp6])
        await session.flush()

        print("[Seed] Creating waitlist entry...")
        # Attendee 3 joins waitlist for Event 2 since capacity (2) is filled
        wl1 = Waitlist(
            event_id=event2.id,
            user_id=attendee3.id,
            position=1,
            status=WaitlistStatus.WAITING
        )
        session.add(wl1)

        print("[Seed] Creating announcements...")
        ann1 = Announcement(
            event_id=event1.id,
            created_by=organizer1.id,
            title="Keynote Speaker Announced!",
            message="We are thrilled to welcome Kelsey Hightower as our opening keynote speaker! Bring your questions on cloud architectures."
        )
        ann2 = Announcement(
            event_id=event2.id,
            created_by=organizer1.id,
            title="Prerequisite Setup Instructions",
            message="Please ensure you have Docker Desktop and Node.js v18+ installed before joining the live workshop next week."
        )
        session.add_all([ann1, ann2])

        print("[Seed] Creating notifications...")
        notif1 = Notification(
            user_id=attendee1.id,
            event_id=event1.id,
            type=NotificationType.RSVP_CONFIRMATION,
            message="You are confirmed for Global Cloud & Kubernetes Summit 2026.",
            read=False
        )
        notif2 = Notification(
            user_id=attendee3.id,
            event_id=event2.id,
            type=NotificationType.ANNOUNCEMENT,
            message="You are in position #1 on the waitlist for Real-Time Distributed Systems Workshop.",
            read=False
        )
        session.add_all([notif1, notif2])

        await session.commit()
        print("[Seed] Database successfully populated with realistic seed data!")
        print("\nSeed Accounts:")
        print("  Organizer: sarah@cloudnative.io | Password: Password123! (Role: ORGANIZER)")
        print("  Organizer: alex@devops.org      | Password: Password123! (Role: ORGANIZER)")
        print("  Attendee:  elena@techflow.dev   | Password: Password123! (Role: ATTENDEE)")
        print("  Attendee:  david@dataminds.ai   | Password: Password123! (Role: ATTENDEE)")
        print("  Attendee:  marcus@cybersec.co   | Password: Password123! (Role: ATTENDEE)")


if __name__ == "__main__":
    asyncio.run(seed())
