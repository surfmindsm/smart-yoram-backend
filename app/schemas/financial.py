from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field


# Offering Schemas
class OfferingBase(BaseModel):
    offered_on: date
    fund_type: str
    amount: Decimal = Field(..., decimal_places=2)
    note: Optional[str] = None


class OfferingCreate(OfferingBase):
    member_id: int
    church_id: int


class OfferingUpdate(BaseModel):
    offered_on: Optional[date] = None
    fund_type: Optional[str] = None
    amount: Optional[Decimal] = None
    note: Optional[str] = None


class Offering(OfferingBase):
    id: int
    member_id: int
    church_id: int
    input_user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Receipt Schemas
class ReceiptBase(BaseModel):
    tax_year: int
    issue_no: str


class ReceiptCreate(ReceiptBase):
    church_id: int
    member_id: int


class ReceiptUpdate(BaseModel):
    canceled_at: Optional[datetime] = None


class Receipt(ReceiptBase):
    id: int
    church_id: int
    member_id: int
    issued_by: int
    issued_at: datetime
    canceled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Receipt Item Schemas
class ReceiptItemBase(BaseModel):
    fund_code: str = "41"
    description: Optional[str] = None
    amount: Decimal = Field(..., decimal_places=2)


class ReceiptItemCreate(ReceiptItemBase):
    receipt_id: int
    offering_id: int


class ReceiptItem(ReceiptItemBase):
    id: int
    receipt_id: int
    offering_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Fund Type Schemas
class FundTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class FundTypeCreate(FundTypeBase):
    church_id: int


class FundTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class FundType(FundTypeBase):
    id: int
    church_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Financial Report Schemas
class FinancialReportBase(BaseModel):
    report_type: str  # monthly, yearly, custom
    period_start: date
    period_end: date
    summary_data: Optional[str] = None  # JSON string


class FinancialReportCreate(FinancialReportBase):
    church_id: int


class FinancialReport(FinancialReportBase):
    id: int
    church_id: int
    generated_by: int
    created_at: datetime

    class Config:
        from_attributes = True


# Summary/Stats Schemas
class OfferingSummary(BaseModel):
    fund_type: str
    total_amount: Decimal
    offering_count: int
    period_start: date
    period_end: date


class MemberOfferingSummary(BaseModel):
    member_id: int
    member_name: str
    total_amount: Decimal
    offering_count: int
    fund_types: List[str]