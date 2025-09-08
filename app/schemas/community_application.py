"""
커뮤니티 회원 신청 스키마
API 요청/응답용 Pydantic 모델
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
import json


# 기본 스키마들
class AttachmentInfo(BaseModel):
    """첨부파일 정보"""
    filename: str
    path: str
    size: int
    mimetype: str


class CommunityApplicationCreate(BaseModel):
    """커뮤니티 회원 신청서 제출"""
    applicant_type: Literal["company", "individual", "musician", "minister", "organization", "other"]
    organization_name: str
    contact_person: str
    email: EmailStr
    phone: str
    business_number: Optional[str] = None
    address: Optional[str] = None
    description: str
    service_area: Optional[str] = None
    website: Optional[str] = None
    
    @validator('organization_name', 'contact_person', 'description')
    def validate_required_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('필수 입력 항목입니다')
        return v.strip()
    
    @validator('email')
    def validate_email_format(cls, v):
        return v.lower().strip()
    
    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v


class CommunityApplicationResponse(BaseModel):
    """커뮤니티 회원 신청서 응답"""
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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # 추가 표시용 필드들
    applicant_type_display: Optional[str] = None
    status_display: Optional[str] = None
    reviewer_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        
    @validator('attachments', pre=True)
    def parse_attachments(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return None
        return v


class CommunityApplicationList(BaseModel):
    """커뮤니티 회원 신청서 목록 응답"""
    applications: List[CommunityApplicationResponse]
    pagination: Dict[str, Any]
    statistics: Dict[str, int]


class CommunityApplicationSubmitResponse(BaseModel):
    """신청서 제출 성공 응답"""
    success: bool
    message: str
    data: Dict[str, Any]


# 관리자용 스키마들
class ApplicationReview(BaseModel):
    """신청서 검토 (승인/반려)"""
    notes: Optional[str] = None


class ApplicationApproval(ApplicationReview):
    """신청서 승인"""
    pass


class ApplicationRejection(ApplicationReview):
    """신청서 반려"""
    rejection_reason: str
    
    @validator('rejection_reason')
    def validate_rejection_reason(cls, v):
        if not v or not v.strip():
            raise ValueError('반려 사유는 필수입니다')
        return v.strip()


class ApplicationApprovalResponse(BaseModel):
    """승인 처리 응답"""
    success: bool
    message: str
    data: Dict[str, Any]  # application_id, status, reviewed_at, user_account 정보


class ApplicationRejectionResponse(BaseModel):
    """반려 처리 응답"""
    success: bool
    message: str
    data: Dict[str, Any]  # application_id, status, reviewed_at


# 쿼리 파라미터 스키마
class ApplicationQueryParams(BaseModel):
    """신청서 목록 조회 파라미터"""
    page: int = 1
    limit: int = 20
    status: Optional[Literal["pending", "approved", "rejected", "all"]] = "all"
    applicant_type: Optional[Literal["company", "individual", "musician", "minister", "organization", "other", "all"]] = "all"
    search: Optional[str] = None  # 조직명, 담당자명, 이메일 검색
    sort_by: Optional[Literal["submitted_at", "reviewed_at", "organization_name"]] = "submitted_at"
    sort_order: Optional[Literal["asc", "desc"]] = "desc"
    
    @validator('page')
    def validate_page(cls, v):
        return max(1, v)
    
    @validator('limit')
    def validate_limit(cls, v):
        return min(100, max(1, v))


# 통계 스키마
class ApplicationStatistics(BaseModel):
    """신청서 통계"""
    pending: int
    approved: int
    rejected: int
    total: int
    
    @property
    def approval_rate(self) -> float:
        """승인율 계산"""
        reviewed = self.approved + self.rejected
        if reviewed == 0:
            return 0.0
        return round((self.approved / reviewed) * 100, 1)


# 에러 응답 스키마
class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    detail: Optional[Dict[str, Any]] = None


# 파일 업로드 관련
class FileUploadResponse(BaseModel):
    """파일 업로드 응답"""
    success: bool
    filename: str
    path: str
    size: int
    mimetype: str


# 이메일 알림 관련
class EmailNotificationData(BaseModel):
    """이메일 알림 데이터"""
    email: str
    organization_name: str
    contact_person: str
    application_id: int
    
    # 승인용
    username: Optional[str] = None
    temporary_password: Optional[str] = None
    login_url: Optional[str] = None
    
    # 반려용
    rejection_reason: Optional[str] = None


# API 응답 공통 스키마
class SuccessResponse(BaseModel):
    """성공 응답 공통 스키마"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    
    
class PaginationInfo(BaseModel):
    """페이지네이션 정보"""
    current_page: int
    total_pages: int
    total_count: int
    per_page: int
    has_next: bool
    has_prev: bool