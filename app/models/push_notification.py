from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class DevicePlatform(str, enum.Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class NotificationType(str, enum.Enum):
    ANNOUNCEMENT = "announcement"
    WORSHIP_REMINDER = "worship_reminder"
    ATTENDANCE = "attendance"
    BIRTHDAY = "birthday"
    PRAYER_REQUEST = "prayer_request"
    SYSTEM = "system"
    CUSTOM = "custom"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    READ = "read"


class UserDevice(Base):
    """사용자 디바이스 정보 (FCM 토큰 관리)"""

    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_token = Column(String(255), nullable=False, unique=True, index=True)
    platform = Column(Enum(DevicePlatform), nullable=False)
    device_model = Column(String(100))
    app_version = Column(String(20))
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="devices")


class NotificationTemplate(Base):
    """알림 템플릿"""

    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title_template = Column(String(200), nullable=False)
    body_template = Column(Text, nullable=False)
    data_schema = Column(JSON)  # JSON schema for template variables
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="notification_templates")


class PushNotification(Base):
    """푸시 알림 기록"""

    __tablename__ = "push_notifications"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"))  # 발신자 (관리자/목사)
    template_id = Column(Integer, ForeignKey("notification_templates.id"))

    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(JSON)  # 추가 데이터 (deeplink, action 등)
    image_url = Column(String(500))

    # 타겟팅
    target_type = Column(String(50))  # all, group, individual
    target_users = Column(JSON)  # user_ids list
    target_groups = Column(JSON)  # department_ids, role list 등

    # 스케줄링
    scheduled_at = Column(DateTime(timezone=True))  # None이면 즉시 발송
    sent_at = Column(DateTime(timezone=True))

    # 통계
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="push_notifications")
    sender = relationship("User", back_populates="sent_notifications")
    recipients = relationship("NotificationRecipient", back_populates="notification")


class NotificationRecipient(Base):
    """알림 수신자별 상태"""

    __tablename__ = "notification_recipients"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(
        Integer, ForeignKey("push_notifications.id"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("user_devices.id"))

    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    notification = relationship("PushNotification", back_populates="recipients")
    user = relationship("User", back_populates="received_notifications")
    device = relationship("UserDevice")


class NotificationPreference(Base):
    """사용자별 알림 설정"""

    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # 알림 종류별 수신 설정
    announcement = Column(Boolean, default=True)
    worship_reminder = Column(Boolean, default=True)
    attendance = Column(Boolean, default=True)
    birthday = Column(Boolean, default=True)
    prayer_request = Column(Boolean, default=True)
    system = Column(Boolean, default=True)

    # 수신 시간 설정
    do_not_disturb = Column(Boolean, default=False)
    dnd_start_time = Column(String(5))  # "HH:MM"
    dnd_end_time = Column(String(5))  # "HH:MM"

    # 알림 채널 설정
    push_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=False)
    sms_enabled = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notification_preference")
