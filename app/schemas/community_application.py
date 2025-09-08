from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class ApplicantType(str, Enum):
    company = "company"
    individual = "individual"
    musician = "musician"
    minister = "minister"
    organization = "organization"
    other = "other"


class ApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class AttachmentInfo(BaseModel):
    filename: str
    path: str
    size: int


# 신청서 제출용 스키마
class CommunityApplicationCreate(BaseModel):
    applicant_type: ApplicantType
    organization_name: str = Field(..., max_length=200, description="단체/회사명")
    contact_person: str = Field(..., max_length=100, description="담당자명")
    email: EmailStr = Field(..., description="이메일")
    phone: str = Field(..., max_length=50, description="연락처")
    business_number: Optional[str] = Field(None, max_length=50, description="사업자등록번호")
    address: Optional[str] = Field(None, description="주소")
    description: str = Field(..., description="상세 소개 및 신청 사유")
    service_area: Optional[str] = Field(None, max_length=200, description="서비스 지역")
    website: Optional[str] = Field(None, max_length=500, description="웹사이트/SNS")


# 응답용 스키마
class CommunityApplicationResponse(BaseModel):
    id: int
    applicant_type: str
    organization_name: str
    contact_person: str
    email: str
    phone: str
    business_number: Optional[str] = None
    address: Optional[str] = None
    description: str
    service_area: Optional[str] = None
    website: Optional[str] = None
    attachments: Optional[List[AttachmentInfo]] = None
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 목록 조회용 스키마 (간소화)
class CommunityApplicationList(BaseModel):
    id: int
    applicant_type: str
    organization_name: str
    contact_person: str
    email: str
    phone: str
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 페이지네이션
class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    total_count: int
    per_page: int


# 통계 정보
class ApplicationStatistics(BaseModel):
    pending: int
    approved: int
    rejected: int
    total: int


# 목록 조회 응답
class CommunityApplicationsListResponse(BaseModel):
    applications: List[CommunityApplicationList]
    pagination: PaginationInfo
    statistics: ApplicationStatistics


# 승인/반려 요청 스키마
class ApplicationApproval(BaseModel):
    notes: Optional[str] = Field(None, description="검토 메모")


class ApplicationRejection(BaseModel):
    rejection_reason: str = Field(..., description="반려 사유")
    notes: Optional[str] = Field(None, description="검토 메모")


# 신청서 제출 응답
class ApplicationSubmissionResponse(BaseModel):
    success: bool = True
    message: str
    data: dict


# 승인 후 계정 정보
class UserAccountInfo(BaseModel):
    username: str
    temporary_password: str
    login_url: str


class ApplicationApprovalResponse(BaseModel):
    success: bool = True
    message: str
    data: dict