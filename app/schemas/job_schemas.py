from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class JobPost:
    """구인 공고 스키마"""
    
    class Create(BaseModel):
        title: str = Field(..., max_length=255, description="제목")
        company: str = Field(..., max_length=100, description="회사명")
        position: str = Field(..., max_length=100, description="직책/포지션")
        employment_type: str = Field(..., description="고용 형태")
        location: str = Field(..., max_length=100, description="근무 지역")
        salary: Optional[str] = Field(None, max_length=100, description="급여")
        work_hours: Optional[str] = Field(None, max_length=100, description="근무 시간")
        description: str = Field(..., description="상세 설명")
        requirements: Optional[str] = Field(None, description="자격 요건")
        benefits: Optional[str] = Field(None, description="복리후생")
        contact_method: str = Field(..., description="연락 방법")
        contact_phone: str = Field(..., max_length=20, description="연락처")
        contact_email: Optional[str] = Field(None, max_length=100, description="이메일")
        deadline: Optional[datetime] = Field(None, description="마감일")
        
    class Update(BaseModel):
        title: Optional[str] = None
        company: Optional[str] = None
        position: Optional[str] = None
        employment_type: Optional[str] = None
        location: Optional[str] = None
        salary: Optional[str] = None
        work_hours: Optional[str] = None
        description: Optional[str] = None
        requirements: Optional[str] = None
        benefits: Optional[str] = None
        contact_method: Optional[str] = None
        contact_phone: Optional[str] = None
        contact_email: Optional[str] = None
        deadline: Optional[datetime] = None
        
    class Response(BaseModel):
        id: int
        title: str
        company: str
        position: str
        employment_type: str
        location: str
        salary: Optional[str]
        work_hours: Optional[str]
        description: str
        requirements: Optional[str]
        benefits: Optional[str]
        contact_method: str
        contact_phone: Optional[str]
        contact_email: Optional[str]
        deadline: Optional[datetime]
        status: str
        author_id: int
        church_id: Optional[int]
        view_count: int
        likes: int
        created_at: datetime
        updated_at: datetime
        
        class Config:
            from_attributes = True


class JobSeeker:
    """구직 신청 스키마"""
    
    class Create(BaseModel):
        title: str = Field(..., max_length=255, description="제목")
        desired_position: str = Field(..., max_length=100, description="희망 직책")
        employment_type: str = Field(..., description="희망 고용 형태")
        desired_location: str = Field(..., max_length=100, description="희망 근무 지역")
        desired_salary: Optional[str] = Field(None, max_length=100, description="희망 급여")
        experience: Optional[str] = Field(None, description="경력")
        skills: Optional[str] = Field(None, description="기술/스킬")
        education: Optional[str] = Field(None, max_length=100, description="학력")
        introduction: str = Field(..., description="자기소개")
        contact_method: str = Field(..., description="연락 방법")
        contact_phone: str = Field(..., max_length=20, description="연락처")
        contact_email: Optional[str] = Field(None, max_length=100, description="이메일")
        available_from: Optional[datetime] = Field(None, description="근무 가능 시작일")
        
    class Response(BaseModel):
        id: int
        title: str
        desired_position: str
        employment_type: str
        desired_location: str
        desired_salary: Optional[str]
        experience: Optional[str]
        skills: Optional[str]
        education: Optional[str]
        introduction: str
        contact_method: str
        contact_phone: Optional[str]
        contact_email: Optional[str]
        available_from: Optional[datetime]
        status: str
        author_id: int
        church_id: Optional[int]
        view_count: int
        likes: int
        created_at: datetime
        updated_at: datetime
        
        class Config:
            from_attributes = True