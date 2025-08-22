from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    Time,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class PastoralCareRequest(Base):
    __tablename__ = "pastoral_care_requests"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(
        Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=False
    )
    member_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    requester_name = Column(String(100), nullable=False)
    requester_phone = Column(String(20), nullable=False)
    request_type = Column(
        String(50), default="general"
    )  # 'general', 'urgent', 'hospital', 'counseling'
    request_content = Column(Text, nullable=False)
    preferred_date = Column(Date, nullable=True)
    preferred_time_start = Column(Time, nullable=True)
    preferred_time_end = Column(Time, nullable=True)
    status = Column(
        String(20), default="pending"
    )  # 'pending', 'approved', 'scheduled', 'completed', 'cancelled'
    priority = Column(String(20), default="normal")  # 'low', 'normal', 'high', 'urgent'
    assigned_pastor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scheduled_date = Column(Date, nullable=True)
    scheduled_time = Column(Time, nullable=True)
    completion_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Location information
    address = Column(
        String(500), nullable=True
    )  # Visit address (basic + detailed combined)
    latitude = Column(Numeric(10, 8), nullable=True)  # Latitude (e.g., 37.5665000)
    longitude = Column(Numeric(11, 8), nullable=True)  # Longitude (e.g., 126.9780000)

    # Additional contact info
    contact_info = Column(String(500), nullable=True)  # Additional contact information

    # Urgency flag
    is_urgent = Column(Boolean, default=False)  # Urgent status

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    church = relationship("Church", back_populates="pastoral_care_requests")
    member = relationship(
        "User", foreign_keys=[member_id], back_populates="pastoral_care_requests"
    )
    assigned_pastor = relationship("User", foreign_keys=[assigned_pastor_id])


class PrayerRequest(Base):
    __tablename__ = "prayer_requests"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(
        Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=False
    )
    member_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    requester_name = Column(String(100), nullable=False)
    requester_phone = Column(String(20), nullable=True)
    prayer_type = Column(
        String(50), default="general"
    )  # 'general', 'healing', 'family', 'work', 'spiritual', 'thanksgiving'
    prayer_content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    status = Column(String(20), default="active")  # 'active', 'answered', 'closed'
    is_public = Column(Boolean, default=True)  # 공개 여부 (주보 게재 등)
    admin_notes = Column(Text, nullable=True)
    answered_testimony = Column(Text, nullable=True)  # 응답받은 간증
    prayer_count = Column(Integer, default=0)  # 기도해준 사람 수
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(
        DateTime(timezone=True), server_default=func.now() + func.interval("30 days")
    )

    # Relationships
    church = relationship("Church", back_populates="prayer_requests")
    member = relationship("User", back_populates="prayer_requests")
    participations = relationship(
        "PrayerParticipation",
        back_populates="prayer_request",
        cascade="all, delete-orphan",
    )


class PrayerParticipation(Base):
    __tablename__ = "prayer_participations"

    id = Column(Integer, primary_key=True, index=True)
    prayer_request_id = Column(
        Integer, ForeignKey("prayer_requests.id", ondelete="CASCADE"), nullable=False
    )
    member_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    church_id = Column(
        Integer, ForeignKey("churches.id", ondelete="CASCADE"), nullable=False
    )
    participated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    prayer_request = relationship("PrayerRequest", back_populates="participations")
    member = relationship("User", back_populates="prayer_participations")
    church = relationship("Church", back_populates="prayer_participations")
