from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel


# Code Schemas
class CodeBase(BaseModel):
    type: str  # position, department, district, visit_type, marital_status
    code: str
    label: str


class CodeCreate(CodeBase):
    church_id: int


class CodeUpdate(BaseModel):
    label: Optional[str] = None


class Code(CodeBase):
    id: int
    church_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Address Schemas
class AddressBase(BaseModel):
    postal_code: Optional[str] = None
    address1: Optional[str] = None  # 기본주소
    address2: Optional[str] = None  # 상세주소
    sido: Optional[str] = None  # 시/도
    sigungu: Optional[str] = None  # 시/군/구
    eupmyeondong: Optional[str] = None  # 읍/면/동


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AddressBase):
    pass


class Address(AddressBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Member Contact Schemas
class MemberContactBase(BaseModel):
    type: str  # phone, mobile, email
    value: str


class MemberContactCreate(MemberContactBase):
    member_id: int


class MemberContactUpdate(BaseModel):
    value: Optional[str] = None


class MemberContact(MemberContactBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Member Address Schemas
class MemberAddressBase(BaseModel):
    is_primary: bool = False


class MemberAddressCreate(MemberAddressBase):
    member_id: int
    address_id: int


class MemberAddress(MemberAddressBase):
    id: int
    member_id: int
    address_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Member Vehicle Schemas
class MemberVehicleBase(BaseModel):
    car_type: Optional[str] = None
    plate_no: Optional[str] = None


class MemberVehicleCreate(MemberVehicleBase):
    member_id: int


class MemberVehicleUpdate(MemberVehicleBase):
    pass


class MemberVehicle(MemberVehicleBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Member Status History Schemas
class MemberStatusHistoryBase(BaseModel):
    status: str
    started_at: date
    ended_at: Optional[date] = None


class MemberStatusHistoryCreate(MemberStatusHistoryBase):
    member_id: int


class MemberStatusHistory(MemberStatusHistoryBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Member Ministry Schemas
class MemberMinistryBase(BaseModel):
    department_code: Optional[str] = None
    position_code: Optional[str] = None
    appointed_on: Optional[date] = None
    ordination_church: Optional[str] = None
    job_title: Optional[str] = None
    workplace: Optional[str] = None
    workplace_phone: Optional[str] = None
    resign_on: Optional[date] = None


class MemberMinistryCreate(MemberMinistryBase):
    member_id: int


class MemberMinistryUpdate(MemberMinistryBase):
    pass


class MemberMinistry(MemberMinistryBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sacrament Schemas
class SacramentBase(BaseModel):
    type: str  # 세례, 입교, 유아세례, 성찬
    date: Optional[date] = None
    church_name: Optional[str] = None


class SacramentCreate(SacramentBase):
    member_id: int


class SacramentUpdate(SacramentBase):
    pass


class Sacrament(SacramentBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Marriage Schemas
class MarriageBase(BaseModel):
    status: Optional[str] = None  # 미혼, 기혼, 사별, 이혼
    spouse_member_id: Optional[int] = None
    married_on: Optional[date] = None


class MarriageCreate(MarriageBase):
    member_id: int


class MarriageUpdate(MarriageBase):
    pass


class Marriage(MarriageBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Transfer Schemas
class TransferBase(BaseModel):
    type: str  # in, out
    church_name: Optional[str] = None
    date: Optional[date] = None


class TransferCreate(TransferBase):
    member_id: int


class Transfer(TransferBase):
    id: int
    member_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enhanced Member Schema with all related data
class MemberEnhanced(BaseModel):
    id: int
    church_id: int
    code: Optional[str] = None
    name: str
    name_eng: Optional[str] = None
    contacts: List[MemberContact] = []
    addresses: List[MemberAddress] = []
    vehicles: List[MemberVehicle] = []
    ministries: List[MemberMinistry] = []
    sacraments: List[Sacrament] = []
    marriages: List[Marriage] = []
    transfers: List[Transfer] = []
    status_history: List[MemberStatusHistory] = []

    class Config:
        from_attributes = True