from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class SharingStatus(str, enum.Enum):
    """나눔 상태"""
    AVAILABLE = "available"
    RESERVED = "reserved"
    COMPLETED = "completed"


class SharingCategory(str, enum.Enum):
    """나눔 카테고리"""
    ELECTRONICS = "가전제품"
    FURNITURE = "가구"
    CLOTHING = "의류"
    BOOKS = "도서"
    OTHER = "기타"


class ContactMethod(str, enum.Enum):
    """연락 방법"""
    PHONE = "phone"
    EMAIL = "email"
    KAKAO = "kakao"


class CommunitySharing(Base):
    """커뮤니티 무료 나눔"""
    
    __tablename__ = "community_sharing"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="제목")
    description = Column(Text, nullable=False, comment="상세 설명")
    category = Column(String(20), nullable=False, comment="카테고리")
    condition = Column(String(50), nullable=True, comment="상태 (양호, 보통, 나쁨)")
    images = Column(JSON, nullable=True, comment="이미지 URL 배열")
    location = Column(String(100), nullable=False, comment="지역")
    contact_method = Column(String(20), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처")
    pickup_location = Column(String(200), nullable=True, comment="픽업 장소")
    available_times = Column(Text, nullable=True, comment="가능한 시간")
    status = Column(String(20), default="available", nullable=False, comment="상태")
    recipient_info = Column(String(200), nullable=True, comment="수령자 정보")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="만료일시")
    
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