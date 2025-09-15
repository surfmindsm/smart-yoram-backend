from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CommunityRequest:
    """커뮤니티 요청 관련 스키마"""
    
    class Create(BaseModel):
        title: str = Field(..., max_length=255, description="제목")
        description: str = Field(..., description="상세 설명")
        category: str = Field(..., description="카테고리")
        urgency: str = Field(..., description="긴급도")
        needed_by: Optional[datetime] = Field(None, description="필요한 날짜")
        request_reason: Optional[str] = Field(None, description="요청 사유")
        location: str = Field(..., max_length=100, description="지역")
        contact_method: str = Field(..., description="연락 방법")
        contact_phone: str = Field(..., max_length=20, description="연락처")
        contact_email: Optional[str] = Field(None, max_length=100, description="이메일")
        
    class Update(BaseModel):
        title: Optional[str] = None
        description: Optional[str] = None
        category: Optional[str] = None
        urgency: Optional[str] = None
        needed_by: Optional[datetime] = None
        request_reason: Optional[str] = None
        location: Optional[str] = None
        contact_method: Optional[str] = None
        contact_phone: Optional[str] = None
        contact_email: Optional[str] = None
        
    class StatusUpdate(BaseModel):
        status: str = Field(..., description="상태 (active, fulfilled, cancelled)")
        provider_info: Optional[str] = Field(None, description="제공자 정보")
        
    class Response(BaseModel):
        id: int
        title: str
        description: str
        category: str
        urgency: str
        needed_by: Optional[datetime]
        request_reason: Optional[str]
        images: Optional[List[str]]
        location: str
        contact_method: str
        contact_phone: Optional[str]
        contact_email: Optional[str]
        status: str
        provider_info: Optional[str]
        author_id: int
        church_id: Optional[int]
        view_count: int
        likes: int
        created_at: datetime
        updated_at: datetime
        
        class Config:
            from_attributes = True