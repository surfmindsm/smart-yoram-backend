"""
커뮤니티 관련 공통 Pydantic 스키마
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

from app.enums.community import CommunityStatus, ContactMethod, UrgencyLevel


class CommunityBaseRequest(BaseModel):
    """커뮤니티 게시글 기본 요청 스키마"""
    title: str = Field(..., max_length=255, description="제목")
    description: Optional[str] = Field(None, description="상세 설명")
    location: Optional[str] = Field(None, max_length=200, description="위치/지역")
    contact_phone: str = Field(..., max_length=20, description="연락처")
    contact_email: Optional[EmailStr] = Field(None, description="이메일")
    contact_method: Optional[ContactMethod] = Field(ContactMethod.PHONE, description="연락 방법")
    status: Optional[CommunityStatus] = Field(CommunityStatus.ACTIVE, description="상태")
    tags: Optional[List[str]] = Field(None, description="태그 배열")


class CommunityBaseResponse(BaseModel):
    """커뮤니티 게시글 기본 응답 스키마"""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    author_id: int
    author_name: str
    church_id: int
    view_count: int = 0
    likes: int = 0
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class StandardContactInfo(BaseModel):
    """표준 연락처 정보"""
    contact_phone: str = Field(..., max_length=20, description="연락처") 
    contact_email: Optional[EmailStr] = Field(None, description="이메일")
    contact_method: Optional[ContactMethod] = Field(ContactMethod.PHONE, description="선호 연락 방법")


class PaginationResponse(BaseModel):
    """표준 페이지네이션 응답"""
    current_page: int
    total_pages: int
    total_count: int
    per_page: int
    has_next: bool
    has_prev: bool


class StandardListResponse(BaseModel):
    """표준 목록 응답"""
    success: bool = True
    data: List[CommunityBaseResponse]
    pagination: PaginationResponse


class StandardDetailResponse(BaseModel):
    """표준 상세/생성/수정 응답"""
    success: bool = True
    message: str
    data: CommunityBaseResponse


class StandardErrorResponse(BaseModel):
    """표준 오류 응답"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    
    
# 공통 필드 유효성 검사 함수들
def validate_title_length(title: str) -> str:
    """제목 길이 유효성 검사 (255자 제한)"""
    if len(title) > 255:
        raise ValueError("제목은 255자를 초과할 수 없습니다.")
    return title


def validate_phone_format(phone: str) -> str:
    """연락처 형식 유효성 검사 (20자 제한)"""
    if len(phone) > 20:
        raise ValueError("연락처는 20자를 초과할 수 없습니다.")
    return phone


def validate_location_length(location: str) -> str:
    """위치 정보 길이 유효성 검사 (200자 제한)"""
    if len(location) > 200:
        raise ValueError("위치 정보는 200자를 초과할 수 없습니다.")
    return location


# 헬퍼 함수들
def format_contact_info(phone: str, email: Optional[str] = None) -> str:
    """통합 연락처 정보 포맷팅 (하위 호환용)"""
    parts = [f"전화: {phone}"]
    if email:
        parts.append(f"이메일: {email}")
    return " | ".join(parts)