from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel


class AnnouncementBase(BaseModel):
    title: str
    content: str
    category: str  # worship, member_news, event
    subcategory: Optional[str] = None
    priority: Optional[str] = "normal"  # urgent, important, normal
    target_type: Optional[str] = "all"  # all, specific, single
    start_date: date
    end_date: Optional[date] = None
    is_active: Optional[bool] = True
    is_pinned: Optional[bool] = False
    target_audience: Optional[str] = "all"


class AnnouncementCreate(AnnouncementBase):
    church_id: Optional[int] = None  # single target용
    target_church_ids: Optional[List[int]] = []  # specific targets용


class AnnouncementUpdate(AnnouncementBase):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    priority: Optional[str] = None
    target_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_church_ids: Optional[List[int]] = []


class AnnouncementInDBBase(AnnouncementBase):
    id: int
    church_id: Optional[int] = None
    type: str  # system, church
    target_type: str  # all, specific, single
    author_id: int
    author_name: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Announcement(AnnouncementInDBBase):
    pass


class AnnouncementInDB(AnnouncementInDBBase):
    pass
