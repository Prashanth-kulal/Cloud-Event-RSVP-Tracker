"""
Models package — imports all ORM models so SQLAlchemy
metadata is populated before init_db() creates tables.
"""
from backend.models.user import User, UserRole  # noqa: F401
from backend.models.event import Event, EventStatus, EventType  # noqa: F401
from backend.models.rsvp import RSVP, RSVPStatus  # noqa: F401
from backend.models.waitlist import Waitlist, WaitlistStatus  # noqa: F401
from backend.models.announcement import Announcement  # noqa: F401
from backend.models.notification import Notification, NotificationType  # noqa: F401
