"""
SQLAlchemy ORM model for Events.
Statuses: DRAFT | PUBLISHED | FULL | COMPLETED | CANCELLED
"""
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import (Column, String, Integer, DateTime, Date, Time,
                        ForeignKey, Enum as SAEnum, Text, Boolean)
from sqlalchemy.orm import relationship
from backend.database import Base


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    FULL = "FULL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class EventType(str, enum.Enum):
    WORKSHOP = "WORKSHOP"
    SEMINAR = "SEMINAR"
    CONFERENCE = "CONFERENCE"
    MEETUP = "MEETUP"
    WEBINAR = "WEBINAR"
    TRAINING = "TRAINING"
    NETWORKING = "NETWORKING"
    OTHER = "OTHER"


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organizer_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(SAEnum(EventType), default=EventType.OTHER, nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    venue = Column(String(300), nullable=True)
    online_link = Column(String(500), nullable=True)
    maximum_capacity = Column(Integer, nullable=False, default=100)
    registration_deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(SAEnum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    is_online = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    organizer = relationship("User", back_populates="events", lazy="select")
    rsvps = relationship("RSVP", back_populates="event", lazy="select", cascade="all, delete-orphan")
    waitlist = relationship("Waitlist", back_populates="event", lazy="select", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="event", lazy="select", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="event", lazy="select", cascade="all, delete-orphan")
