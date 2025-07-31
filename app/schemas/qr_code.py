from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class QRCodeBase(BaseModel):
    qr_type: Optional[str] = "attendance"


class QRCodeCreate(QRCodeBase):
    expires_at: Optional[datetime] = None


class QRCodeUpdate(BaseModel):
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class QRCodeInDBBase(QRCodeBase):
    id: int
    church_id: int
    member_id: int
    code: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QRCode(QRCodeInDBBase):
    pass


class QRCodeInDB(QRCodeInDBBase):
    pass