from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text)
    event_type = Column(String)  # birthday, anniversary, service, meeting, etc
    event_date = Column(Date, nullable=False, index=True)
    event_time = Column(String)  # HH:MM format

    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String)  # yearly, monthly, weekly

    related_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", backref="calendar_events")
    related_member = relationship("Member", backref="related_events")
    creator = relationship("User", backref="created_events")
