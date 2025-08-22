from typing import Optional, Union
from datetime import date, datetime
from pydantic import BaseModel, field_validator

from app.schemas.enums import Gender


class MemberBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo_url: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[Union[Gender, str]] = None
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

    @field_validator("gender", mode="before")
    def validate_gender(cls, v):
        if v is None:
            return None
        if isinstance(v, Gender):
            return v.value
        if isinstance(v, str):
            v = v.upper().strip()
            if v in ["M", "F"]:
                return v
            # Try to convert Korean labels
            gender_enum = Gender.from_korean(v)
            if gender_enum:
                return gender_enum.value
        raise ValueError("Gender must be M or F (or 남/여 in Korean)")


class MemberCreate(MemberBase):
    church_id: Optional[int] = None


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
