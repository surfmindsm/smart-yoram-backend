from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel


class SystemAnnouncementBase(BaseModel):
    title: str
    content: str
    priority: Optional[str] = "normal"  # urgent, important, normal
    start_date: date
    end_date: Optional[date] = None
    target_churches: Optional[str] = None  # JSON string of church IDs
    is_active: Optional[bool] = True
    is_pinned: Optional[bool] = False


class SystemAnnouncementCreate(SystemAnnouncementBase):
    pass


class SystemAnnouncementUpdate(SystemAnnouncementBase):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_churches: Optional[str] = None


class SystemAnnouncementInDBBase(SystemAnnouncementBase):
    id: int
    created_by: int
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SystemAnnouncement(SystemAnnouncementInDBBase):
    pass


class SystemAnnouncementInDB(SystemAnnouncementInDBBase):
    pass


# 읽음 처리 스키마
class SystemAnnouncementReadCreate(BaseModel):
    system_announcement_id: int


class SystemAnnouncementRead(BaseModel):
    id: int
    system_announcement_id: int
    user_id: int
    church_id: int
    read_at: datetime

    class Config:
        from_attributes = True