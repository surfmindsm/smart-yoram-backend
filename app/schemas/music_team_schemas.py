from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.common import CommonStatus


class MusicTeamRecruitment:
    """음악팀 모집 스키마"""
    
    class Create(BaseModel):
        title: str = Field(..., max_length=255, description="제목")
        team_name: str = Field(..., max_length=100, description="팀명")
        team_type: str = Field(..., description="팀 유형")
        instruments_needed: List[str] = Field(..., description="필요한 악기/포지션 목록")
        experience_level: str = Field(..., description="요구 실력 수준")
        practice_location: str = Field(..., max_length=200, description="연습 장소")
        practice_schedule: str = Field(..., description="연습 일정")
        description: str = Field(..., description="상세 설명")
        requirements: Optional[str] = Field(None, description="지원 자격")
        benefits: Optional[str] = Field(None, description="혜택")
        contact_method: str = Field(..., description="연락 방법")
        contact_phone: str = Field(..., max_length=20, description="연락처")
        contact_email: Optional[str] = Field(None, max_length=100, description="이메일")
        deadline: Optional[datetime] = Field(None, description="모집 마감일")
        
    class Update(BaseModel):
        title: Optional[str] = None
        team_name: Optional[str] = None
        team_type: Optional[str] = None
        instruments_needed: Optional[List[str]] = None
        experience_level: Optional[str] = None
        practice_location: Optional[str] = None
        practice_schedule: Optional[str] = None
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
        team_name: str
        team_type: str
        instruments_needed: List[str]
        experience_level: str
        practice_location: str
        practice_schedule: str
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


class MusicTeamSeeker:
    """음악팀 참여 신청 스키마"""
    
    class Create(BaseModel):
        title: str = Field(..., max_length=255, description="지원서 제목")
        desired_team_type: str = Field(..., description="희망 팀 유형")
        instruments: List[str] = Field(..., description="연주 가능 악기")
        experience_level: str = Field(..., description="실력 수준")
        experience_description: Optional[str] = Field(None, description="경력 설명")
        preferred_location: Optional[List[str]] = Field(None, description="활동 가능 지역")
        available_days: Optional[List[str]] = Field(None, description="활동 가능 요일")
        introduction: str = Field(..., description="자기소개")
        portfolio_links: Optional[List[str]] = Field(None, description="포트폴리오 링크")
        contact_method: str = Field(..., description="연락 방법")
        contact_phone: str = Field(..., max_length=20, description="연락처")
        contact_email: Optional[str] = Field(None, max_length=100, description="이메일")
        
    class Response(BaseModel):
        id: int
        title: str
        desired_team_type: str
        instruments: List[str]
        experience_level: str
        experience_description: Optional[str]
        preferred_location: Optional[List[str]]
        available_days: Optional[List[str]]
        introduction: str
        portfolio_links: Optional[List[str]]
        contact_method: str
        contact_phone: Optional[str]
        contact_email: Optional[str]
        status: str
        author_id: int
        church_id: Optional[int]
        view_count: int
        likes: int
        created_at: datetime
        updated_at: datetime
        
        class Config:
            from_attributes = True