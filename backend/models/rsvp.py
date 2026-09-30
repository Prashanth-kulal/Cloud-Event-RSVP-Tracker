"""
SQLAlchemy ORM model for RSVPs.
Unique constraint on (event_id, user_id) prevents duplicate RSVPs.
Statuses: GOING | MAYBE | NOT_GOING
"""
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class RSVPStatus(str, enum.Enum):
    GOING = "GOING"
    MAYBE = "MAYBE"
    NOT_GOING = "NOT_GOING"


class RSVP(Base):
    __tablename__ = "rsvps"
    __table_args__ = (
        # Cloud Computing concept: database-level constraint prevents duplicate RSVPs
        # This ensures idempotency even under concurrent requests
        UniqueConstraint("event_id", "user_id", name="uq_event_user_rsvp"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SAEnum(RSVPStatus), nullable=False)
    responded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    event = relationship("Event", back_populates="rsvps", lazy="select")
    user = relationship("User", back_populates="rsvps", lazy="select")
