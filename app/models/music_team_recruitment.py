from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class RecruitmentType(str, enum.Enum):
    """모집 유형"""
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


class MusicTeamRecruitment(Base):
    """음악팀 모집"""
    
    __tablename__ = "community_music_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="제목")
    team_name = Column(String(100), nullable=False, comment="팀명")
    team_type = Column(String(9), nullable=False, comment="팀 유형")
    instruments_needed = Column(JSON, nullable=True, comment="필요한 악기/포지션 목록")
    positions_needed = Column(Text, nullable=True, comment="필요한 포지션")
    experience_required = Column(String(12), nullable=False, comment="경력 요구사항")
    practice_location = Column(String(200), nullable=False, comment="연습 장소")
    practice_schedule = Column(String(200), nullable=False, comment="연습 일정")
    commitment = Column(String(100), nullable=True, comment="활동 기간")
    description = Column(Text, nullable=False, comment="상세 설명")
    requirements = Column(Text, nullable=True, comment="지원 자격/요구사항")
    benefits = Column(Text, nullable=True, comment="혜택/사례비")
    contact_method = Column(String(7), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처 정보")
    status = Column(String(10), nullable=False, comment="모집 상태")
    current_members = Column(Integer, nullable=True, comment="현재 인원")
    target_members = Column(Integer, nullable=True, comment="목표 인원")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    church_id = Column(Integer, nullable=False, comment="교회 ID")
    views = Column(Integer, nullable=True, default=0, comment="조회수")
    likes = Column(Integer, nullable=True, default=0, comment="좋아요수")
    applicants_count = Column(Integer, nullable=True, default=0, comment="지원자 수")
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), comment="생성일")
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now(), comment="수정일")
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])