from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CommunitySharing:
    """커뮤니티 나눔 관련 스키마"""
    
    class Create(BaseModel):
        title: str = Field(..., max_length=200, description="제목")
        description: str = Field(..., description="상세 설명")
        category: str = Field(..., description="카테고리")
        condition: Optional[str] = Field(None, max_length=50, description="상태")
        location: str = Field(..., max_length=100, description="지역")
        contact_method: str = Field(..., description="연락 방법")
        contact_info: str = Field(..., max_length=100, description="연락처")
        pickup_location: Optional[str] = Field(None, max_length=200, description="픽업 장소")
        available_times: Optional[str] = Field(None, description="가능한 시간")
        expires_at: Optional[datetime] = Field(None, description="만료일시")
        
    class Update(BaseModel):
        title: Optional[str] = None
        description: Optional[str] = None
        category: Optional[str] = None
        condition: Optional[str] = None
        location: Optional[str] = None
        contact_method: Optional[str] = None
        contact_info: Optional[str] = None
        pickup_location: Optional[str] = None
        available_times: Optional[str] = None
        expires_at: Optional[datetime] = None
        
    class StatusUpdate(BaseModel):
        status: str = Field(..., description="상태 (available, reserved, completed)")
        recipient_info: Optional[str] = Field(None, description="수령자 정보")
        
    class Response(BaseModel):
        id: int
        title: str
        description: str
        category: str
        condition: Optional[str]
        images: Optional[List[str]]
        location: str
        contact_method: str
        contact_info: str
        pickup_location: Optional[str]
        available_times: Optional[str]
        status: str
        recipient_info: Optional[str]
        expires_at: Optional[datetime]
        author_id: int
        church_id: Optional[int]
        views: int
        likes: int
        created_at: datetime
        updated_at: datetime
        
        class Config:
            from_attributes = True