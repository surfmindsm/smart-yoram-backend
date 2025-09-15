from sqlalchemy import Column, Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base
from app.models.common import CommonStatus, ContactMethod, CommunityBaseMixin, ContactFieldsMixin


# 통일된 상태 사용 - CommonStatus 활용
# available → active, reserved → paused, completed → completed


class SharingCategory(str, enum.Enum):
    """나눔 카테고리"""
    ELECTRONICS = "가전제품"
    FURNITURE = "가구"
    CLOTHING = "의류"
    BOOKS = "도서"
    OTHER = "기타"


# ContactMethod는 common.py에서 import


class CommunitySharing(Base, CommunityBaseMixin, ContactFieldsMixin):
    """커뮤니티 무료 나눔"""
    
    __tablename__ = "community_sharing"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="제목")
    description = Column(Text, nullable=True, comment="상세 설명")
    category = Column(String, nullable=True, comment="카테고리")
    condition = Column(String, nullable=True, default="good", comment="상태")
    price = Column(Integer, nullable=True, default=0, comment="가격")
    is_free = Column(Boolean, nullable=True, default=True, comment="무료 여부")
    location = Column(String, nullable=True, comment="지역")
    images = Column(JSON, nullable=True, comment="이미지 URL 배열")
    
    # Relationships
    author = relationship("User", foreign_keys=["author_id"])