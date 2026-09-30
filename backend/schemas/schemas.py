"""
Pydantic v2 schemas for request/response validation.
Organized by domain: Auth, User, Event, RSVP, Waitlist, Announcement, Notification.
"""
from __future__ import annotations
from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from backend.models.user import UserRole
from backend.models.event import EventStatus, EventType
from backend.models.rsvp import RSVPStatus
from backend.models.waitlist import WaitlistStatus
from backend.models.notification import NotificationType


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.ATTENDEE

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── User ────────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: UserRole
    profile_picture: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None


# ─── Event ───────────────────────────────────────────────────────────────────

class EventCreateRequest(BaseModel):
    event_name: str
    description: Optional[str] = None
    event_type: EventType = EventType.OTHER
    event_date: date
    start_time: time
    end_time: Optional[time] = None
    venue: Optional[str] = None
    online_link: Optional[str] = None
    maximum_capacity: int = 100
    registration_deadline: Optional[datetime] = None
    is_online: bool = False

    @field_validator("event_name")
    @classmethod
    def name_required(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Event name is required")
        return v.strip()

    @field_validator("maximum_capacity")
    @classmethod
    def positive_capacity(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Capacity must be at least 1")
        return v

    @model_validator(mode="after")
    def validate_times(self) -> EventCreateRequest:
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self


class EventUpdateRequest(BaseModel):
    event_name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    online_link: Optional[str] = None
    maximum_capacity: Optional[int] = None
    registration_deadline: Optional[datetime] = None
    is_online: Optional[bool] = None


class EventResponse(BaseModel):
    id: str
    organizer_id: str
    organizer_name: Optional[str] = None
    event_name: str
    description: Optional[str] = None
    event_type: EventType
    event_date: date
    start_time: time
    end_time: Optional[time] = None
    venue: Optional[str] = None
    online_link: Optional[str] = None
    maximum_capacity: int
    registration_deadline: Optional[datetime] = None
    status: EventStatus
    is_online: bool
    going_count: int = 0
    maybe_count: int = 0
    not_going_count: int = 0
    waitlist_count: int = 0
    available_seats: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── RSVP ────────────────────────────────────────────────────────────────────

class RSVPRequest(BaseModel):
    status: RSVPStatus


class RSVPResponse(BaseModel):
    id: str
    event_id: str
    user_id: str
    user_name: Optional[str] = None
    status: RSVPStatus
    responded_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Waitlist ────────────────────────────────────────────────────────────────

class WaitlistResponse(BaseModel):
    id: str
    event_id: str
    user_id: str
    user_name: Optional[str] = None
    position: int
    status: WaitlistStatus
    joined_at: datetime

    model_config = {"from_attributes": True}


# ─── Announcement ────────────────────────────────────────────────────────────

class AnnouncementCreateRequest(BaseModel):
    title: str
    message: str

    @field_validator("title", "message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class AnnouncementResponse(BaseModel):
    id: str
    event_id: str
    title: str
    message: str
    created_by: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Notification ─────────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    event_id: Optional[str] = None
    type: NotificationType
    message: str
    read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Analytics ────────────────────────────────────────────────────────────────

class EventAnalyticsResponse(BaseModel):
    event_id: str
    event_name: str
    maximum_capacity: int
    going_count: int
    maybe_count: int
    not_going_count: int
    waitlist_count: int
    total_responses: int
    available_seats: int
    response_rate: float
    capacity_utilization: float
    rsvp_timeline: List[dict] = []


# ─── API Envelope ─────────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool = True
    message: str = "OK"
    data: Optional[object] = None
