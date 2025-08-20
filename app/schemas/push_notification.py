from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DevicePlatform(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class NotificationType(str, Enum):
    ANNOUNCEMENT = "announcement"
    WORSHIP_REMINDER = "worship_reminder"
    ATTENDANCE = "attendance"
    BIRTHDAY = "birthday"
    PRAYER_REQUEST = "prayer_request"
    SYSTEM = "system"
    CUSTOM = "custom"


class DeviceRegister(BaseModel):
    device_token: str = Field(..., description="FCM device token")
    platform: DevicePlatform
    device_model: Optional[str] = None
    app_version: Optional[str] = None


class DeviceResponse(BaseModel):
    id: int
    user_id: int
    device_token: str
    platform: DevicePlatform
    device_model: Optional[str]
    app_version: Optional[str]
    is_active: bool
    last_used_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationSend(BaseModel):
    title: str = Field(..., max_length=200)
    body: str = Field(...)
    type: NotificationType = NotificationType.CUSTOM
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    user_id: Optional[int] = None  # For individual send


class NotificationBatchSend(BaseModel):
    title: str = Field(..., max_length=200)
    body: str = Field(...)
    type: NotificationType = NotificationType.CUSTOM
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    user_ids: List[int] = Field(..., min_items=1)


class NotificationResponse(BaseModel):
    success: bool
    message: str


class NotificationHistoryResponse(BaseModel):
    id: int
    type: NotificationType
    title: str
    body: str
    data: Optional[Dict]
    image_url: Optional[str]
    target_type: str
    total_recipients: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    sent_at: Optional[datetime]
    created_at: datetime
    status: str = Field(default="pending")

    class Config:
        from_attributes = True

    @property
    def calculated_status(self) -> str:
        """Calculate status based on counts"""
        if self.total_recipients == 0:
            return "no_recipients"
        elif self.sent_count == 0 and self.failed_count == 0:
            return "pending"
        elif self.sent_count > 0 and self.failed_count == 0:
            return "success"
        elif self.sent_count == 0 and self.failed_count > 0:
            return "failed"
        else:
            return "partial"

    def model_post_init(self, __context):
        """Set status after initialization"""
        self.status = self.calculated_status


class NotificationPreferenceUpdate(BaseModel):
    announcement: Optional[bool] = None
    worship_reminder: Optional[bool] = None
    attendance: Optional[bool] = None
    birthday: Optional[bool] = None
    prayer_request: Optional[bool] = None
    system: Optional[bool] = None
    do_not_disturb: Optional[bool] = None
    dnd_start_time: Optional[str] = Field(
        None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    dnd_end_time: Optional[str] = Field(
        None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None


class NotificationPreferenceResponse(BaseModel):
    id: int
    user_id: int
    announcement: bool
    worship_reminder: bool
    attendance: bool
    birthday: bool
    prayer_request: bool
    system: bool
    do_not_disturb: bool
    dnd_start_time: Optional[str]
    dnd_end_time: Optional[str]
    push_enabled: bool
    email_enabled: bool
    sms_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
