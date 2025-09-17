from sqlalchemy import Column, Integer, String, Text, JSON, Boolean
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base
from app.models.common import CommonStatus, CommunityBaseMixin


# RecruitmentType and InstrumentType moved to app/enums/community.py for consistency


class MusicTeamRecruitment(Base, CommunityBaseMixin):
    """음악팀 모집"""
    
    __tablename__ = "community_music_teams"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, comment="제목")
    team_name = Column(String(100), nullable=False, comment="팀명")
    worship_type = Column(String(50), nullable=False, comment="예배 형태 (주일예배, 수요예배, 특별예배 등)")
    team_types = Column(JSON, nullable=True, comment="팀 유형 배열 (솔로, 찬양팀, 워십팀, 밴드 등)")
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
    current_members = Column(Integer, nullable=True, comment="현재 인원")
    target_members = Column(Integer, nullable=True, comment="목표 인원")
    applicants_count = Column(Integer, nullable=True, default=0, comment="지원자 수")
    
    # Relationships
    author = relationship("User")