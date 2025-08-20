from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String)  # birthday, event, announcement, reminder

    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    church = relationship("Church", backref="notifications")
    user = relationship("User", backref="notifications")
    member = relationship("Member", backref="notifications")
