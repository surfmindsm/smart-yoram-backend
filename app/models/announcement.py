from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    
    # 명세서 요구사항: church_id NULL 허용 (시스템 공지의 경우)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=True)

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # 명세서 요구사항: type과 priority 추가
    type = Column(String(50), nullable=False, default='church')  # 'system' or 'church'
    priority = Column(String(50), nullable=False, default='normal')  # 'urgent', 'important', 'normal'
    
    # 명세서 요구사항: 기간 설정
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # NULL이면 무제한

    # Author information (명세서의 created_by와 매핑)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 기존 호환성
    author_name = Column(String)  # Denormalized for performance

    # Visibility and status
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)  # Pin important announcements

    # Category fields (기존 기능 유지)
    category = Column(String, nullable=False)  # worship, member_news, event
    subcategory = Column(String)  # Optional subcategory

    # Target audience (기존 기능 유지)
    target_audience = Column(String, default="all")  # all, member, youth, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 제약 조건
    __table_args__ = (
        CheckConstraint("type IN ('system', 'church')", name='check_type'),
        CheckConstraint("priority IN ('urgent', 'important', 'normal')", name='check_priority'),
        CheckConstraint("(type = 'system' AND church_id IS NULL) OR (type = 'church' AND church_id IS NOT NULL)", 
                       name='check_system_church_consistency'),
    )

    # Relationships
    church = relationship("Church", backref="announcements")
    creator = relationship("User", foreign_keys=[created_by], backref="created_announcements")
    author = relationship("User", foreign_keys=[author_id], backref="announcements")


class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"
    
    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 제약 조건: 같은 사용자가 같은 공지사항을 중복해서 읽음 처리할 수 없음
    __table_args__ = (
        CheckConstraint('announcement_id IS NOT NULL AND user_id IS NOT NULL', 
                       name='check_announcement_read_not_null'),
    )
    
    # Relationships  
    announcement = relationship("Announcement", backref="reads")
    user = relationship("User", backref="announcement_reads")
