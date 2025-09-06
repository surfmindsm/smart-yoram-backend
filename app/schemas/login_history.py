from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class LoginHistoryBase(BaseModel):
    ip_address: str
    user_agent: Optional[str] = None
    device: Optional[str] = None
    location: Optional[str] = None
    status: str = "success"


class LoginHistoryCreate(LoginHistoryBase):
    user_id: int
    session_start: Optional[datetime] = None


class LoginHistoryUpdate(BaseModel):
    session_end: Optional[datetime] = None
    session_duration: Optional[str] = None


class LoginHistory(LoginHistoryBase):
    id: int
    user_id: int
    login_time: datetime
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    session_duration: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginHistoryRecent(BaseModel):
    """Recent login info for header display"""
    last_login: Optional[datetime] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    device: Optional[str] = None

    class Config:
        from_attributes = True


class LoginHistoryDetail(BaseModel):
    """Detailed login history for modal display"""
    id: int
    login_time: datetime
    ip_address: str
    location: Optional[str] = None
    device: Optional[str] = None
    status: str
    session_duration: Optional[str] = None

    class Config:
        from_attributes = True