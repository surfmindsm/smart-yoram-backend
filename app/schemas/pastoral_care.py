from typing import Optional, List
from datetime import datetime, date, time
from pydantic import BaseModel


# Pastoral Care Request Schemas
class PastoralCareRequestBase(BaseModel):
    requester_name: str
    requester_phone: str
    request_type: Optional[str] = "general"
    request_content: str
    preferred_date: Optional[date] = None
    preferred_time_start: Optional[time] = None
    preferred_time_end: Optional[time] = None
    priority: Optional[str] = "normal"


class PastoralCareRequestCreate(PastoralCareRequestBase):
    pass


class PastoralCareRequestUpdate(BaseModel):
    request_content: Optional[str] = None
    preferred_date: Optional[date] = None
    preferred_time_start: Optional[time] = None
    preferred_time_end: Optional[time] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class PastoralCareRequestAdminUpdate(PastoralCareRequestUpdate):
    status: Optional[str] = None
    assigned_pastor_id: Optional[int] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    admin_notes: Optional[str] = None


class PastoralCareRequestComplete(BaseModel):
    completion_notes: str


class PastoralCareRequest(PastoralCareRequestBase):
    id: int
    church_id: int
    member_id: Optional[int] = None
    status: str
    assigned_pastor_id: Optional[int] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    completion_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Prayer Request Schemas
class PrayerRequestBase(BaseModel):
    requester_name: str
    requester_phone: Optional[str] = None
    prayer_type: Optional[str] = "general"
    prayer_content: str
    is_anonymous: Optional[bool] = False
    is_urgent: Optional[bool] = False
    is_public: Optional[bool] = True


class PrayerRequestCreate(PrayerRequestBase):
    pass


class PrayerRequestUpdate(BaseModel):
    prayer_content: Optional[str] = None
    is_urgent: Optional[bool] = None
    is_public: Optional[bool] = None


class PrayerRequestTestimony(BaseModel):
    answered_testimony: str


class PrayerRequestAdminUpdate(PrayerRequestUpdate):
    status: Optional[str] = None
    admin_notes: Optional[str] = None
    is_public: Optional[bool] = None


class PrayerRequest(PrayerRequestBase):
    id: int
    church_id: int
    member_id: Optional[int] = None
    status: str
    admin_notes: Optional[str] = None
    answered_testimony: Optional[str] = None
    prayer_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    expires_at: datetime

    class Config:
        from_attributes = True


# Prayer Participation Schemas
class PrayerParticipationCreate(BaseModel):
    prayer_request_id: int


class PrayerParticipation(BaseModel):
    id: int
    prayer_request_id: int
    member_id: int
    church_id: int
    participated_at: datetime

    class Config:
        from_attributes = True


# Statistics Schemas
class PastoralCareStats(BaseModel):
    total_requests: int
    pending_count: int
    scheduled_count: int
    completed_count: int
    completed_this_month: int
    urgent_count: int
    average_completion_days: float


class PrayerRequestStats(BaseModel):
    total_requests: int
    active_count: int
    answered_count: int
    closed_count: int
    urgent_count: int
    public_count: int
    total_prayers: int
    answered_this_month: int


# List Response Schemas
class PastoralCareRequestList(BaseModel):
    items: List[PastoralCareRequest]
    total: int
    page: int
    per_page: int


class PrayerRequestList(BaseModel):
    items: List[PrayerRequest]
    total: int
    page: int
    per_page: int
