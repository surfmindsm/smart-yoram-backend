from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class SMSBase(BaseModel):
    recipient_phone: str
    message: str
    sms_type: Optional[str] = "general"


class SMSCreate(SMSBase):
    recipient_member_id: Optional[int] = None


class SMSBulkCreate(BaseModel):
    recipient_member_ids: List[int]
    message: str
    sms_type: Optional[str] = "general"


class SMSUpdate(BaseModel):
    status: Optional[str] = None
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None


class SMSInDBBase(SMSBase):
    id: int
    church_id: int
    sender_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SMS(SMSInDBBase):
    pass


class SMSInDB(SMSInDBBase):
    pass
