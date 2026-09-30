"""
SQLAlchemy ORM model for Users.
Roles: ATTENDEE | ORGANIZER | ADMIN
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from backend.database import Base


class UserRole(str, enum.Enum):
    ATTENDEE = "ATTENDEE"
    ORGANIZER = "ORGANIZER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.ATTENDEE, nullable=False)
    profile_picture = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    events = relationship("Event", back_populates="organizer", lazy="select")
    rsvps = relationship("RSVP", back_populates="user", lazy="select")
    waitlist_entries = relationship("Waitlist", back_populates="user", lazy="select")
    notifications = relationship("Notification", back_populates="user", lazy="select")
