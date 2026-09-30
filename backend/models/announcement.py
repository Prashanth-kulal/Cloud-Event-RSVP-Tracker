"""
SQLAlchemy ORM model for Event Announcements.
Only organizers with permission can create announcements.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    event = relationship("Event", back_populates="announcements", lazy="select")
    author = relationship("User", foreign_keys=[created_by], lazy="select")
