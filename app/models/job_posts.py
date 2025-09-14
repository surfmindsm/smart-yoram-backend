from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class JobStatus(str, enum.Enum):
    """구인공고 상태"""
    ACTIVE = "active"
    CLOSED = "closed"
    FILLED = "filled"


class EmploymentType(str, enum.Enum):
    """고용 형태"""
    FULL_TIME = "정규직"
    PART_TIME = "계약직"
    CONTRACT = "아르바이트"
    FREELANCE = "프리랜서"
    INTERN = "인턴"


class JobPost(Base):
    """구인 공고"""
    
    __tablename__ = "job_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, nullable=False, default=9998, comment="교회 ID (9998=커뮤니티)")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    
    # 기본 정보
    title = Column(String, nullable=False, comment="제목")
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
    status = Column(String, default="active", comment="상태")
    
    # 통계 (실제 테이블에 both view_count, views 존재)
    view_count = Column(Integer, default=0, comment="조회수")
    likes = Column(Integer, default=0, comment="좋아요수")
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])


class JobSeeker(Base):
    """구직 신청"""
    
    __tablename__ = "job_seekers"
    
    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, nullable=False, default=9998, comment="교회 ID (9998=커뮤니티)")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    
    # 기본 정보
    title = Column(String, nullable=False, comment="제목")
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
    status = Column(String, default="active", comment="상태")
    
    # 통계
    view_count = Column(Integer, default=0, comment="조회수")
    likes = Column(Integer, default=0, comment="좋아요수")
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])