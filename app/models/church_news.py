from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Date, Time, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class NewsPriority(str, enum.Enum):
    """행사 소식 우선순위"""
    URGENT = "urgent"
    IMPORTANT = "important"
    NORMAL = "normal"


class NewsStatus(str, enum.Enum):
    """행사 소식 상태"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ChurchNews(Base):
    """교회 행사 소식"""
    
    __tablename__ = "church_news"
    
    # 기본 정보
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True, comment="제목")
    content = Column(Text, nullable=False, comment="내용")
    category = Column(String(50), nullable=False, index=True, comment="카테고리")
    priority = Column(String(20), default="normal", index=True, comment="우선순위")
    
    # 행사 정보
    event_date = Column(Date, nullable=True, comment="행사일")
    event_time = Column(Time, nullable=True, comment="행사 시간")
    location = Column(String(255), nullable=True, comment="장소")
    organizer = Column(String(100), nullable=False, comment="주최자/부서")
    target_audience = Column(String(100), nullable=True, comment="대상")
    participation_fee = Column(String(50), nullable=True, comment="참가비")
    
    # 신청 관련
    registration_required = Column(Boolean, default=False, comment="사전 신청 필요 여부")
    registration_deadline = Column(Date, nullable=True, comment="신청 마감일")
    
    # 연락처 정보 (다른 커뮤니티 API와 일관성 유지)
    contact_person = Column(String(100), nullable=True, comment="담당자")
    contact_phone = Column(String(20), nullable=True, comment="연락처")
    contact_email = Column(String(100), nullable=True, comment="이메일")
    
    # 상태 관리
    status = Column(String(20), default="active", index=True, comment="상태")
    
    # 메타데이터 (다른 API와 일관성: view_count 사용)
    view_count = Column(Integer, default=0, comment="조회수")
    likes = Column(Integer, default=0, comment="좋아요")
    comments_count = Column(Integer, default=0, comment="댓글 수")
    
    # 태그 및 이미지 (JSON 배열)
    tags = Column(JSON, nullable=True, comment="태그 배열")
    images = Column(JSON, nullable=True, comment="이미지 배열")
    
    # 공통 필드 (다른 API와 일관성)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), comment="생성일")
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now(), comment="수정일")
    
    # 작성자 정보 (다른 커뮤니티 API와 일관성: author_id 사용)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    church_id = Column(Integer, nullable=True, comment="교회 ID")
    
    # 관계
    author = relationship("User", foreign_keys=[author_id])