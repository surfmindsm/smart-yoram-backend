from typing import Optional, Union
from datetime import date as DateType, datetime
from pydantic import BaseModel


class BulletinBase(BaseModel):
    title: str
    date: DateType
    content: Optional[str] = None
    file_url: Optional[str] = None


class BulletinCreate(BulletinBase):
    church_id: int


class BulletinUpdate(BaseModel):
    title: Union[str, None] = None
    date: Union[DateType, None] = None
    content: Union[str, None] = None
    file_url: Union[str, None] = None


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
