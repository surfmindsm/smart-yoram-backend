from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class InstrumentType(str, enum.Enum):
    """팀 형태/악기 유형"""
    SOLO = "현재 솔로 활동"
    PRAISE_TEAM = "찬양팀"
    WORSHIP_TEAM = "워십팀"
    ACOUSTIC_TEAM = "어쿠스틱 팀"
    BAND = "밴드"
    ORCHESTRA = "오케스트라"
    CHOIR = "합창단"
    DANCE_TEAM = "무용팀"
    OTHER = "기타"


class AvailableDay(str, enum.Enum):
    """활동 가능 요일"""
    MONDAY = "월요일"
    TUESDAY = "화요일"
    WEDNESDAY = "수요일"
    THURSDAY = "목요일"
    FRIDAY = "금요일"
    SATURDAY = "토요일"
    SUNDAY = "일요일"


class AvailableTime(str, enum.Enum):
    """활동 가능 시간대"""
    MORNING = "오전 (9:00-12:00)"
    AFTERNOON = "오후 (13:00-18:00)"
    EVENING = "저녁 (18:00-21:00)"
    NIGHT = "야간 (21:00-23:00)"
    ANYTIME = "상시 가능"
    NEGOTIABLE = "협의 후 결정"


class SeekerStatus(str, enum.Enum):
    """지원자 상태"""
    AVAILABLE = "available"
    INTERVIEWING = "interviewing"
    INACTIVE = "inactive"


class MusicTeamSeeker(Base):
    """음악팀 지원자"""
    
    __tablename__ = "music_team_seekers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="지원서 제목")
    team_name = Column(String(100), nullable=True, comment="현재 활동 팀명")
    instrument = Column(String(50), nullable=False, comment="팀 형태")
    experience = Column(Text, nullable=True, comment="연주 경력")
    portfolio = Column(String(500), nullable=True, comment="포트폴리오 링크")
    preferred_location = Column(ARRAY(String), nullable=True, comment="활동 가능 지역")
    available_days = Column(ARRAY(String), nullable=True, comment="활동 가능 요일")
    available_time = Column(String(100), nullable=True, comment="활동 가능 시간대")
    contact_phone = Column(String(20), nullable=False, comment="연락처")
    contact_email = Column(String(100), nullable=True, comment="이메일")
    status = Column(String(20), nullable=False, default="available", comment="상태")
    
    # JWT에서 자동 추출되는 필드들
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    author_name = Column(String(100), nullable=False, comment="작성자 이름")
    church_id = Column(Integer, nullable=True, comment="소속 교회 ID")
    church_name = Column(String(100), nullable=True, comment="소속 교회명")
    
    # 시스템 필드
    view_count = Column(Integer, nullable=True, default=0, comment="조회수")
    likes = Column(Integer, nullable=True, default=0, comment="좋아요수")
    matches = Column(Integer, nullable=True, default=0, comment="매칭 건수")
    applications = Column(Integer, nullable=True, default=0, comment="지원 건수")
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), comment="생성일")
    updated_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now(), comment="수정일")
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])