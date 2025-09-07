from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    encrypted_password = Column(String)  # Store encrypted password for admin decryption
    full_name = Column(String)
    phone = Column(String)

    church_id = Column(Integer, ForeignKey("churches.id"))
    role = Column(String, default="member")  # admin, minister, leader, member

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_first = Column(Boolean, default=True)  # First time login flag

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="users")

    # Push notification relationships
    devices = relationship("UserDevice", back_populates="user")
    sent_notifications = relationship("PushNotification", back_populates="sender")
    received_notifications = relationship(
        "NotificationRecipient", back_populates="user"
    )
    notification_preference = relationship(
        "NotificationPreference", back_populates="user", uselist=False
    )

    # Chat relationships
    chat_histories = relationship("ChatHistory", back_populates="user")

    # Pastoral care and prayer relationships
    pastoral_care_requests = relationship(
        "PastoralCareRequest",
        foreign_keys="PastoralCareRequest.member_id",
        back_populates="member",
    )
    prayer_requests = relationship("PrayerRequest", back_populates="member")
    prayer_participations = relationship("PrayerParticipation", back_populates="member")
    sermon_materials = relationship("SermonMaterial", back_populates="user")
    
    # Simple login history relationship
    login_records = relationship("LoginHistory", back_populates="user")
