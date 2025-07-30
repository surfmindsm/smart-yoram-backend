from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class BulletinBase(BaseModel):
    title: str
    date: date
    content: Optional[str] = None
    file_url: Optional[str] = None


class BulletinCreate(BulletinBase):
    church_id: int


class BulletinUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[date] = None
    content: Optional[str] = None
    file_url: Optional[str] = None


class BulletinInDBBase(BulletinBase):
    id: int
    church_id: int
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Bulletin(BulletinInDBBase):
    pass


class BulletinInDB(BulletinInDBBase):
    pass
