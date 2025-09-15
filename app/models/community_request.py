from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base
from app.models.common import CommonStatus, CommunityBaseMixin


# 통일된 상태 사용 - CommonStatus 활용
# active → active, fulfilled → completed, cancelled → cancelled


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


class CommunityRequest(Base, CommunityBaseMixin):
    """커뮤니티 물품 요청"""
    
    __tablename__ = "community_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="제목")
    description = Column(Text, nullable=True, comment="상세 설명")
    category = Column(String, nullable=True, comment="카테고리")
    urgency = Column(String, nullable=True, default="normal", comment="긴급도")
    images = Column(JSON, nullable=True, comment="참고 이미지 URL 배열")
    location = Column(String, nullable=True, comment="지역")
    contact_info = Column(String, nullable=True, comment="연락처")
    reward_type = Column(String, nullable=True, default="none", comment="보상 유형")
    reward_amount = Column(Integer, nullable=True, comment="보상 금액")
    
    # Relationships
    author = relationship("User", foreign_keys=["author_id"])