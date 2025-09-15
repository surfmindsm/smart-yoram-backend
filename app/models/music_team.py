from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class TeamType(str, enum.Enum):
    """팀 유형"""
    WORSHIP = "찬양팀"
    PRAISE = "경배팀"
    CHOIR = "성가대"
    BAND = "밴드"
    OTHER = "기타"


class ExperienceLevel(str, enum.Enum):
    """실력 수준"""
    BEGINNER = "초급"
    INTERMEDIATE = "중급"
    ADVANCED = "고급"
    PROFESSIONAL = "전문"


class MusicTeamRecruit(Base):
    """음악팀 모집"""
    
    __tablename__ = "music_team_recruits"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="제목")
    team_name = Column(String(100), nullable=False, comment="팀명")
    church_name = Column(String(100), nullable=False, comment="교회명")
    instruments_needed = Column(JSON, nullable=False, comment="필요한 악기 목록")
    team_type = Column(String(20), nullable=False, comment="팀 유형")
    experience_required = Column(String(20), nullable=False, comment="요구 실력")
    practice_location = Column(String(200), nullable=False, comment="연습 장소")
    practice_schedule = Column(Text, nullable=False, comment="연습 일정")
    commitment = Column(String(100), nullable=True, comment="최소 활동 기간")
    description = Column(Text, nullable=False, comment="상세 설명")
    requirements = Column(Text, nullable=True, comment="지원 자격")
    benefits = Column(Text, nullable=True, comment="혜택")
    contact_method = Column(String(20), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처")
    deadline = Column(DateTime(timezone=True), nullable=True, comment="모집 마감일")
    status = Column(String(20), default="open", nullable=False, comment="모집 상태")
    
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


class MusicTeamApplication(Base):
    """음악팀 참여 신청"""
    
    __tablename__ = "music_team_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="제목")
    desired_team_type = Column(String(20), nullable=False, comment="희망 팀 유형")
    instruments = Column(JSON, nullable=False, comment="연주 가능 악기")
    experience_level = Column(String(20), nullable=False, comment="실력 수준")
    experience_description = Column(Text, nullable=True, comment="경력 설명")
    desired_location = Column(String(100), nullable=False, comment="희망 활동 지역")
    available_schedule = Column(Text, nullable=False, comment="가능한 일정")
    introduction = Column(Text, nullable=False, comment="자기소개")
    portfolio_links = Column(JSON, nullable=True, comment="포트폴리오 링크")
    contact_method = Column(String(20), nullable=False, comment="연락 방법")
    contact_info = Column(String(100), nullable=False, comment="연락처")
    available_from = Column(DateTime(timezone=True), nullable=True, comment="활동 가능 시작일")
    status = Column(String(20), default="active", nullable=False, comment="상태")
    
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