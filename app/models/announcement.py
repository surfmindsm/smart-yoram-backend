from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


# 기존 교회 공지사항 테이블 (원본 복원)
class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    # Author information
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String)  # Denormalized for performance

    # Visibility and status
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)  # Pin important announcements

    # Category fields
    category = Column(String, nullable=False)  # worship, member_news, event
    subcategory = Column(String)  # Optional subcategory

    # Target audience
    target_audience = Column(String, default="all")  # all, member, youth, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", backref="announcements")
    author = relationship("User", backref="announcements")


# 새로운 시스템 공지사항 테이블
class SystemAnnouncement(Base):
    __tablename__ = "system_announcements"

    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # 우선순위
    priority = Column(String(50), nullable=False, default='normal')  # urgent, important, normal
    
    # 게시 기간
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # NULL이면 무제한
    
    # 대상 교회들 (NULL이면 전체 교회)
    target_churches = Column(Text, nullable=True)  # JSON string of church IDs
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_pinned = Column(Boolean, default=False)
    
    # 작성자 (시스템 관리자)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String)  # Denormalized for performance
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 제약 조건
    __table_args__ = (
        CheckConstraint("priority IN ('urgent', 'important', 'normal')", name='check_system_priority'),
    )
    
    # Relationships
    creator = relationship("User", backref="system_announcements")


# 시스템 공지사항 읽음 처리
class SystemAnnouncementRead(Base):
    __tablename__ = "system_announcement_reads"
    
    id = Column(Integer, primary_key=True, index=True)
    system_announcement_id = Column(Integer, ForeignKey("system_announcements.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    church_id = Column(Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=False)  # 어느 교회에서 읽었는지
    read_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 제약 조건: 같은 사용자가 같은 시스템 공지사항을 중복해서 읽음 처리할 수 없음
    __table_args__ = (
        CheckConstraint('system_announcement_id IS NOT NULL AND user_id IS NOT NULL AND church_id IS NOT NULL', 
                       name='check_system_announcement_read_not_null'),
    )
    
    # Relationships  
    system_announcement = relationship("SystemAnnouncement", backref="reads")
    user = relationship("User", backref="system_announcement_reads")
    church = relationship("Church", backref="system_announcement_reads")
