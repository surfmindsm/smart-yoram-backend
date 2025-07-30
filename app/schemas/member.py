from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class MemberBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    position: Optional[str] = "member"
    department: Optional[str] = None
    district: Optional[str] = None
    baptism_date: Optional[date] = None
    baptism_church: Optional[str] = None
    registration_date: Optional[date] = None
    family_id: Optional[int] = None
    family_role: Optional[str] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None
    # New fields for enhanced features
    profile_photo_url: Optional[str] = None
    member_status: Optional[str] = "active"
    transfer_church: Optional[str] = None
    transfer_date: Optional[date] = None
    memo: Optional[str] = None
    invitation_sent: Optional[bool] = False
    invitation_sent_at: Optional[datetime] = None


class MemberCreate(MemberBase):
    church_id: int


class MemberUpdate(MemberBase):
    name: Optional[str] = None


class MemberInDBBase(MemberBase):
    id: int
    church_id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class Member(MemberInDBBase):
    pass


class MemberInDB(MemberInDBBase):
    pass
