from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: Optional[str] = "general"
    target_user_id: Optional[int] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationInDBBase(NotificationBase):
    id: int
    church_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


class Notification(NotificationInDBBase):
    pass


class NotificationInDB(NotificationInDBBase):
    pass