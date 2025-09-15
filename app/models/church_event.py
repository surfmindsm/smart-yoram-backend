from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base
from app.models.common import CommonStatus


class EventType(str, enum.Enum):
    """행사 유형"""
    RETREAT = "수련회"
    CONFERENCE = "컨퍼런스"
    CONCERT = "콘서트"
    SEMINAR = "세미나"
    WORKSHOP = "워크샵"
    FESTIVAL = "축제"
    SERVICE = "예배"
    OTHER = "기타"


# EventStatus removed - using CommonStatus instead


class ChurchEvent(Base):
    """교회 행사"""
    
    __tablename__ = "church_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="행사명")
    church_name = Column(String(100), nullable=False, comment="주최 교회")
    event_type = Column(String(20), nullable=False, comment="행사 유형")
    description = Column(Text, nullable=False, comment="행사 설명")
    start_date = Column(DateTime(timezone=True), nullable=False, comment="시작일시")
    end_date = Column(DateTime(timezone=True), nullable=False, comment="종료일시")
    location = Column(String(200), nullable=False, comment="장소명")
    address = Column(Text, nullable=True, comment="상세 주소")
    capacity = Column(Integer, nullable=True, comment="최대 참가자 수")
    current_participants = Column(Integer, default=0, comment="현재 참가자 수")
    fee = Column(Integer, default=0, comment="참가비")
    registration_deadline = Column(DateTime(timezone=True), nullable=True, comment="등록 마감일")
    contact_method = Column(String(20), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처")
    requirements = Column(Text, nullable=True, comment="참가 조건")
    includes = Column(Text, nullable=True, comment="포함 사항")
    images = Column(JSON, nullable=True, comment="행사 이미지 URL 배열")
    status = Column(Enum(CommonStatus), default=CommonStatus.ACTIVE, nullable=False, comment="행사 상태")
    
    # 작성자 정보
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    church_id = Column(Integer, nullable=True, comment="교회 ID (9998=커뮤니티)")
    
    # 통계
    view_count = Column(Integer, default=0, comment="조회수")
    likes = Column(Integer, default=0, comment="좋아요수")
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])