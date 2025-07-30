from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: Optional[str] = None
    event_date: date
    event_time: Optional[str] = None
    is_recurring: Optional[bool] = False
    recurrence_pattern: Optional[str] = None
    related_member_id: Optional[int] = None


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    related_member_id: Optional[int] = None


class CalendarEventInDBBase(CalendarEventBase):
    id: int
    church_id: int
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarEvent(CalendarEventInDBBase):
    pass


class CalendarEventInDB(CalendarEventInDBBase):
    pass