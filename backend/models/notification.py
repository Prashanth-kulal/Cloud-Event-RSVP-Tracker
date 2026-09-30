"""
SQLAlchemy ORM model for in-app Notifications.
Types: RSVP_CONFIRMATION, EVENT_REMINDER, VENUE_CHANGE, TIME_CHANGE,
       EVENT_CANCELLED, WAITLIST_PROMOTION, ANNOUNCEMENT
"""
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from backend.database import Base


class NotificationType(str, enum.Enum):
    RSVP_CONFIRMATION = "RSVP_CONFIRMATION"
    EVENT_REMINDER = "EVENT_REMINDER"
    VENUE_CHANGE = "VENUE_CHANGE"
    TIME_CHANGE = "TIME_CHANGE"
    EVENT_CANCELLED = "EVENT_CANCELLED"
    WAITLIST_PROMOTION = "WAITLIST_PROMOTION"
    ANNOUNCEMENT = "ANNOUNCEMENT"
    RSVP_UPDATED = "RSVP_UPDATED"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(String, ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(SAEnum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="notifications", lazy="select")
    event = relationship("Event", back_populates="notifications", lazy="select")
