from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class EmploymentType(str, enum.Enum):
    """고용 형태"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class JobStatus(str, enum.Enum):
    """구인 상태"""
    OPEN = "open"
    CLOSED = "closed"
    FILLED = "filled"


class JobPost(Base):
    """구인 공고"""
    
    __tablename__ = "job_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="제목")
    company = Column(String(100), nullable=False, comment="회사명")
    position = Column(String(100), nullable=False, comment="직책/포지션")
    employment_type = Column(String(20), nullable=False, comment="고용 형태")
    location = Column(String(100), nullable=False, comment="근무 지역")
    salary = Column(String(100), nullable=True, comment="급여")
    work_hours = Column(String(100), nullable=True, comment="근무 시간")
    description = Column(Text, nullable=False, comment="상세 설명")
    requirements = Column(Text, nullable=True, comment="자격 요건")
    benefits = Column(Text, nullable=True, comment="복리후생")
    contact_method = Column(String(20), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처")
    deadline = Column(DateTime(timezone=True), nullable=True, comment="마감일")
    status = Column(String(20), default="open", nullable=False, comment="상태")
    
    # 작성자 정보
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    church_id = Column(Integer, nullable=True, comment="교회 ID (9998=커뮤니티)")
    
    # 통계
    views = Column(Integer, default=0, comment="조회수")
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
    title = Column(String(200), nullable=False, comment="제목")
    desired_position = Column(String(100), nullable=False, comment="희망 직책")
    employment_type = Column(String(20), nullable=False, comment="희망 고용 형태")
    desired_location = Column(String(100), nullable=False, comment="희망 근무 지역")
    desired_salary = Column(String(100), nullable=True, comment="희망 급여")
    experience = Column(Text, nullable=True, comment="경력")
    skills = Column(Text, nullable=True, comment="기술/스킬")
    education = Column(String(100), nullable=True, comment="학력")
    introduction = Column(Text, nullable=False, comment="자기소개")
    contact_method = Column(String(20), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처")
    available_from = Column(DateTime(timezone=True), nullable=True, comment="근무 가능 시작일")
    status = Column(String(20), default="active", nullable=False, comment="상태")
    
    # 작성자 정보
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    church_id = Column(Integer, nullable=True, comment="교회 ID (9998=커뮤니티)")
    
    # 통계
    views = Column(Integer, default=0, comment="조회수")
    likes = Column(Integer, default=0, comment="좋아요수")
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])