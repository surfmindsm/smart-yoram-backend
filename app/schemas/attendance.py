from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class AttendanceBase(BaseModel):
    member_id: int
    service_date: date
    service_type: str
    present: Optional[bool] = True
    check_in_method: Optional[str] = "manual"
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    church_id: int


class AttendanceUpdate(BaseModel):
    present: Optional[bool] = None
    notes: Optional[str] = None


class AttendanceInDBBase(AttendanceBase):
    id: int
    church_id: int
    check_in_time: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class Attendance(AttendanceInDBBase):
    pass


class AttendanceInDB(AttendanceInDBBase):
    pass
