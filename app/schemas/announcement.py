from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel


class AnnouncementBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = "system"  # worship, member_news, event, system
    subcategory: Optional[str] = None
    is_active: Optional[bool] = True
    is_pinned: Optional[bool] = False
    target_audience: Optional[str] = "all"


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(AnnouncementBase):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None


class AnnouncementInDBBase(AnnouncementBase):
    id: int
    church_id: Optional[int] = None
    author_id: int
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Announcement(AnnouncementInDBBase):
    pass


class AnnouncementInDB(AnnouncementInDBBase):
    pass
