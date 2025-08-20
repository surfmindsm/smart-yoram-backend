from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DailyVerseBase(BaseModel):
    verse: str
    reference: str
    is_active: bool = True


class DailyVerseCreate(DailyVerseBase):
    pass


class DailyVerseUpdate(BaseModel):
    verse: Optional[str] = None
    reference: Optional[str] = None
    is_active: Optional[bool] = None


class DailyVerseInDBBase(DailyVerseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyVerse(DailyVerseInDBBase):
    pass


class DailyVerseInDB(DailyVerseInDBBase):
    pass
