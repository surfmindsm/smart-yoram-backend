from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class RequestStatus(str, enum.Enum):
    """요청 상태"""
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class RequestCategory(str, enum.Enum):
    """요청 카테고리"""
    ELECTRONICS = "가전제품"
    FURNITURE = "가구"
    CLOTHING = "의류"
    BOOKS = "도서"
    OTHER = "기타"


class UrgencyLevel(str, enum.Enum):
    """긴급도"""
    LOW = "낮음"
    MEDIUM = "보통"
    HIGH = "높음"


class CommunityRequest(Base):
    """커뮤니티 물품 요청"""
    
    __tablename__ = "community_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="제목")
    description = Column(Text, nullable=False, comment="상세 설명")
    category = Column(String(20), nullable=False, comment="카테고리")
    urgency_level = Column(String(10), nullable=False, comment="긴급도")
    needed_by = Column(DateTime(timezone=True), nullable=True, comment="필요한 날짜")
    request_reason = Column(Text, nullable=True, comment="요청 사유")
    images = Column(JSON, nullable=True, comment="참고 이미지 URL 배열")
    location = Column(String(100), nullable=False, comment="지역")
    contact_method = Column(String(20), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처")
    status = Column(String(20), default="active", nullable=False, comment="상태")
    provider_info = Column(String(200), nullable=True, comment="제공자 정보")
    
    # 작성자 정보
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")  # author_id → user_id
    church_id = Column(Integer, nullable=True, comment="교회 ID (9998=커뮤니티)")
    
    # 통계
    view_count = Column(Integer, default=0, comment="조회수")  # views → view_count
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[user_id])  # author_id → user_id