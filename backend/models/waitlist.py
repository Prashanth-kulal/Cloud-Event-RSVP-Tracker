"""
SQLAlchemy ORM model for Waitlist.
FIFO ordering by position. Promotes attendees when capacity becomes available.
"""
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class WaitlistStatus(str, enum.Enum):
    WAITING = "WAITING"
    PROMOTED = "PROMOTED"
    CANCELLED = "CANCELLED"


class Waitlist(Base):
    __tablename__ = "waitlist"
    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_user_waitlist"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=1)
    status = Column(SAEnum(WaitlistStatus), default=WaitlistStatus.WAITING, nullable=False)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    event = relationship("Event", back_populates="waitlist", lazy="select")
    user = relationship("User", back_populates="waitlist_entries", lazy="select")
