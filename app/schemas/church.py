from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ChurchBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    pastor_name: Optional[str] = None
    subscription_status: Optional[str] = "trial"
    subscription_end_date: Optional[datetime] = None
    member_limit: Optional[int] = 100


class ChurchCreate(ChurchBase):
    pass


class ChurchUpdate(ChurchBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ChurchInDBBase(ChurchBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Church(ChurchInDBBase):
    pass


class ChurchInDB(ChurchInDBBase):
    pass
