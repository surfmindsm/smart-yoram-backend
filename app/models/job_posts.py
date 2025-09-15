from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base
from app.models.common import CommonStatus, CommunityBaseMixin


# JobStatus removed - using CommonStatus instead
# EmploymentType moved to app/enums/community.py for consistency


class JobPost(Base, CommunityBaseMixin):
    """구인 공고"""
    
    __tablename__ = "job_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    title = Column(String(255), nullable=False, comment="제목")
    description = Column(Text, nullable=True, comment="상세 설명")
    company_name = Column(String, nullable=True, comment="회사명")
    job_type = Column(String, nullable=True, comment="직무 유형")
    employment_type = Column(String, nullable=True, comment="고용 형태")
    location = Column(String, nullable=True, comment="근무 지역")
    salary_range = Column(String, nullable=True, comment="급여 범위")
    requirements = Column(Text, nullable=True, comment="지원 자격")
    contact_info = Column(String, nullable=True, comment="연락처")
    
    # 마감일 및 상태
    application_deadline = Column(Date, nullable=True, comment="지원 마감일")
    
    # Relationships
    author = relationship("User")


class JobSeeker(Base, CommunityBaseMixin):
    """구직 신청"""
    
    __tablename__ = "job_seekers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 기본 정보
    title = Column(String(255), nullable=False, comment="제목")
    desired_position = Column(String, nullable=True, comment="희망 직무")
    employment_type = Column(String, nullable=True, comment="희망 고용 형태")
    desired_location = Column(String, nullable=True, comment="희망 근무 지역")
    salary_expectation = Column(String, nullable=True, comment="희망 급여")
    experience_summary = Column(Text, nullable=True, comment="경력 요약")
    education_background = Column(String, nullable=True, comment="학력")
    skills = Column(String, nullable=True, comment="보유 기술")
    portfolio_url = Column(String, nullable=True, comment="포트폴리오 URL")
    contact_info = Column(String, nullable=True, comment="연락처")
    
    # 상태 및 기타
    available_start_date = Column(Date, nullable=True, comment="입사 가능일")
    
    # Relationships
    author = relationship("User")