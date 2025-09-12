from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class RecruitmentType(str, enum.Enum):
    """행사 유형"""
    SUNDAY_SERVICE = "주일예배"
    WEDNESDAY_SERVICE = "수요예배"
    DAWN_SERVICE = "새벽예배"
    SPECIAL_SERVICE = "특별예배"
    REVIVAL = "부흥회"
    PRAISE_MEETING = "찬양집회"
    WEDDING = "결혼식"
    FUNERAL = "장례식"
    RETREAT = "수련회"
    CONCERT = "콘서트"
    OTHER = "기타"


class InstrumentType(str, enum.Enum):
    """악기/포지션 유형"""
    PIANO = "피아노"
    KEYBOARD = "키보드"
    ORGAN = "오르간"
    GUITAR = "기타"
    ELECTRIC_GUITAR = "일렉기타"
    BASS = "베이스"
    DRUMS = "드럼"
    VIOLIN = "바이올린"
    CELLO = "첼로"
    FLUTE = "플룻"
    SAXOPHONE = "색소폰"
    TRUMPET = "트럼펫"
    VOCAL = "보컬"
    OTHER = "기타"


class RecruitmentStatus(str, enum.Enum):
    """모집 상태"""
    OPEN = "open"
    CLOSED = "closed"
    COMPLETED = "completed"


class ChurchEvent(Base):
    """교회 행사팀 모집"""
    
    __tablename__ = "community_church_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="모집 제목")
    event_type = Column(String(10), nullable=True, comment="행사 유형")
    description = Column(Text, nullable=True, comment="상세 설명")
    start_date = Column(DateTime, nullable=True, comment="시작일")
    end_date = Column(DateTime, nullable=True, comment="종료일")
    registration_deadline = Column(DateTime, nullable=True, comment="등록 마감일")
    location = Column(String(200), nullable=True, comment="장소")
    address = Column(String(300), nullable=True, comment="주소")
    venue_details = Column(Text, nullable=True, comment="장소 상세")
    capacity = Column(Integer, nullable=True, comment="정원")
    current_participants = Column(Integer, default=0, comment="현재 참가자")
    min_participants = Column(Integer, nullable=True, comment="최소 참가자")
    fee = Column(String, nullable=True, comment="참가비")
    fee_description = Column(String(200), nullable=True, comment="참가비 설명")
    target_audience = Column(String(100), nullable=True, comment="대상")
    requirements = Column(Text, nullable=True, comment="요구사항")
    includes = Column(Text, nullable=True, comment="포함사항")
    contact_method = Column(String(7), nullable=True, comment="연락 방법")
    contact_info = Column(String(100), nullable=True, comment="연락처")
    organizer = Column(String(100), nullable=True, comment="주최자")
    status = Column(String(9), default="active", comment="상태")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    church_id = Column(Integer, nullable=False, default=9998, comment="교회 ID")
    views = Column(Integer, default=0, comment="조회수")
    likes = Column(Integer, default=0, comment="좋아요")
    created_at = Column(DateTime, nullable=True, comment="생성일")
    updated_at = Column(DateTime, nullable=True, comment="수정일")
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])