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
    
    __tablename__ = "church_events"
    
    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, nullable=False, default=9998, comment="교회 ID (9998=커뮤니티)")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    author_id = Column(Integer, nullable=True, comment="작성자 ID (중복)")
    
    # 기본 정보
    title = Column(String, nullable=False, comment="모집 제목")
    church_name = Column(String, nullable=False, comment="교회명")
    recruitment_type = Column(String, nullable=False, comment="행사 유형")
    
    # 모집 상세
    instruments = Column(JSON, nullable=False, comment="모집 악기/포지션 배열")
    schedule = Column(Text, nullable=True, comment="일정 정보")
    location = Column(String, nullable=True, comment="장소 정보")
    
    # 상세 내용
    description = Column(Text, nullable=True, comment="상세 설명")
    requirements = Column(Text, nullable=True, comment="자격 요건")
    compensation = Column(String, nullable=True, comment="보상/사례비")
    
    # 연락처 정보
    contact_info = Column(String, nullable=True, comment="연락처 정보 (조합)")
    contact_phone = Column(String, nullable=True, comment="전화번호")
    contact_email = Column(String, nullable=True, comment="이메일")
    
    # 상태 및 통계
    status = Column(String, default="open", comment="모집 상태")
    applications = Column(Integer, default=0, comment="지원자 수")
    view_count = Column(Integer, default=0, comment="조회수")
    views = Column(Integer, default=0, comment="조회수 (중복)")
    likes = Column(Integer, default=0, comment="좋아요수")
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[user_id])