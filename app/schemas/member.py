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
    
    # Enhanced fields from requirements (레퍼런스 요구사항)
    member_type: Optional[str] = None  # 교인구분
    confirmation_date: Optional[date] = None  # 입교일
    sub_district: Optional[str] = None  # 부구역
    age_group: Optional[str] = None  # 나이그룹
    region_1: Optional[str] = None  # 안도구1
    region_2: Optional[str] = None  # 안도구2
    region_3: Optional[str] = None  # 안도구3
    inviter3_member_id: Optional[int] = None  # 입도자3
    postal_code: Optional[str] = None  # 우편번호
    last_contact_date: Optional[date] = None  # 통화일
    spiritual_grade: Optional[str] = None  # 신급
    job_category: Optional[str] = None  # 직업분류
    job_detail: Optional[str] = None  # 구체적 업무
    job_position: Optional[str] = None  # 직책/직위
    ministry_start_date: Optional[date] = None  # 장업일
    neighboring_church: Optional[str] = None  # 이웃교회
    position_decision: Optional[str] = None  # 직관결정
    daily_activity: Optional[str] = None  # 매일활동
    
    # Custom fields (자유필드 1~12)
    custom_field_1: Optional[str] = None
    custom_field_2: Optional[str] = None
    custom_field_3: Optional[str] = None
    custom_field_4: Optional[str] = None
    custom_field_5: Optional[str] = None
    custom_field_6: Optional[str] = None
    custom_field_7: Optional[str] = None
    custom_field_8: Optional[str] = None
    custom_field_9: Optional[str] = None
    custom_field_10: Optional[str] = None
    custom_field_11: Optional[str] = None
    custom_field_12: Optional[str] = None
    
    # Special notes
    special_notes: Optional[str] = None  # 개인 특별 사항
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
