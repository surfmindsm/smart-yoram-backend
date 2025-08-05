from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


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