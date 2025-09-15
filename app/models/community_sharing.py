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
    church_id = Column(Integer, nullable=False, default=9998, comment="교회 ID (9998=커뮤니티)")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")  # 실제 컬럼명
    title = Column(String, nullable=False, comment="제목")
    description = Column(Text, nullable=True, comment="상세 설명")
    category = Column(String, nullable=True, comment="카테고리")
    condition = Column(String, nullable=True, default="good", comment="상태")
    price = Column(Integer, nullable=True, default=0, comment="가격")
    is_free = Column(Boolean, nullable=True, default=True, comment="무료 여부")
    location = Column(String, nullable=True, comment="지역")
    contact_phone = Column(String(20), nullable=True, comment="연락처")
    contact_email = Column(String(100), nullable=True, comment="이메일")
    images = Column(JSON, nullable=True, comment="이미지 URL 배열")  # 실제로 존재함!
    status = Column(String, nullable=True, default="available", comment="상태")
    view_count = Column(Integer, nullable=True, default=0, comment="조회수")  # 실제 컬럼명
    likes = Column(Integer, nullable=True, default=0, comment="좋아요 수")
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])  # 실제 컬럼명 사용