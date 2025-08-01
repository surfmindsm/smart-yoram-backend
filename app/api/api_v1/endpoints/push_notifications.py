from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.push_notification import (
    UserDevice, PushNotification, NotificationPreference,
    NotificationType, DevicePlatform
)
from app.schemas.push_notification import (
    DeviceRegister, DeviceResponse,
    NotificationSend, NotificationBatchSend,
    NotificationResponse, NotificationHistoryResponse,
    NotificationPreferenceUpdate, NotificationPreferenceResponse
)
from app.services.push_notification import PushNotificationService

router = APIRouter()


@router.post("/devices/register", response_model=DeviceResponse)
async def register_device(
    device_data: DeviceRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """FCM 디바이스 토큰 등록"""
    device = await PushNotificationService.register_device(
        db=db,
        user_id=current_user.id,
        device_token=device_data.device_token,
        platform=device_data.platform,
        device_model=device_data.device_model,
        app_version=device_data.app_version
    )
    return device


@router.post("/devices/unregister")
async def unregister_device(
    device_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """FCM 디바이스 토큰 비활성화"""
    success = await PushNotificationService.unregister_device(
        db=db,
        device_token=device_token
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return {"message": "Device unregistered successfully"}


@router.get("/devices", response_model=List[DeviceResponse])
def get_my_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """내 등록된 디바이스 목록 조회"""
    devices = db.query(UserDevice).filter(
        UserDevice.user_id == current_user.id,
        UserDevice.is_active == True
    ).all()
    return devices


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    notification: NotificationSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """개별 사용자에게 푸시 알림 발송 (관리자/목사만 가능)"""
    if current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    # Check if target user exists and belongs to same church
    target_user = db.query(User).filter(
        User.id == notification.user_id,
        User.church_id == current_user.church_id
    ).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    success = await PushNotificationService.send_to_user(
        db=db,
        user_id=notification.user_id,
        title=notification.title,
        body=notification.body,
        data=notification.data,
        image_url=notification.image_url,
        notification_type=notification.type
    )
    
    return {
        "success": success,
        "message": "알림이 발송되었습니다" if success else "알림 발송에 실패했습니다"
    }


@router.post("/send-batch", response_model=Dict[str, int])
async def send_batch_notification(
    notification: NotificationBatchSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """여러 사용자에게 푸시 알림 발송 (관리자/목사만 가능)"""
    if current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    # Verify all users belong to same church
    users_count = db.query(User).filter(
        User.id.in_(notification.user_ids),
        User.church_id == current_user.church_id
    ).count()
    
    if users_count != len(notification.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="일부 사용자가 교회에 속하지 않습니다"
        )
    
    result = await PushNotificationService.send_to_multiple_users(
        db=db,
        user_ids=notification.user_ids,
        title=notification.title,
        body=notification.body,
        data=notification.data,
        image_url=notification.image_url,
        notification_type=notification.type,
        church_id=current_user.church_id
    )
    
    return result


@router.post("/send-to-church", response_model=Dict[str, int])
async def send_church_notification(
    notification: NotificationSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 전체에 푸시 알림 발송 (관리자/목사만 가능)"""
    if current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    result = await PushNotificationService.send_to_church(
        db=db,
        church_id=current_user.church_id,
        title=notification.title,
        body=notification.body,
        data=notification.data,
        image_url=notification.image_url,
        notification_type=notification.type
    )
    
    return result


@router.get("/history", response_model=List[NotificationHistoryResponse])
def get_notification_history(
    skip: int = 0,
    limit: int = 20,
    notification_type: Optional[NotificationType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """발송한 알림 이력 조회 (관리자/목사만 가능)"""
    if current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    
    query = db.query(PushNotification).filter(
        PushNotification.church_id == current_user.church_id
    )
    
    if notification_type:
        query = query.filter(PushNotification.type == notification_type)
    
    notifications = query.order_by(
        PushNotification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notifications


@router.get("/my-notifications", response_model=List[NotificationHistoryResponse])
def get_my_notifications(
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """내가 받은 알림 목록 조회"""
    from app.models.push_notification import NotificationRecipient
    
    query = db.query(PushNotification).join(
        NotificationRecipient
    ).filter(
        NotificationRecipient.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(NotificationRecipient.read_at.is_(None))
    
    notifications = query.order_by(
        PushNotification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notifications


@router.put("/mark-as-read/{notification_id}")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """알림을 읽음으로 표시"""
    from app.models.push_notification import NotificationRecipient, NotificationStatus
    
    recipient = db.query(NotificationRecipient).filter(
        NotificationRecipient.notification_id == notification_id,
        NotificationRecipient.user_id == current_user.id
    ).first()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="알림을 찾을 수 없습니다"
        )
    
    recipient.read_at = datetime.utcnow()
    recipient.status = NotificationStatus.READ
    
    # Update read count in main notification
    notification = recipient.notification
    notification.read_count = (notification.read_count or 0) + 1
    
    db.commit()
    return {"message": "알림을 읽음으로 표시했습니다"}


@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """알림 설정 조회"""
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        # Create default preferences
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
        db.commit()
        db.refresh(preference)
    
    return preference


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """알림 설정 업데이트"""
    preference = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        preference = NotificationPreference(user_id=current_user.id)
        db.add(preference)
    
    # Update preferences
    for field, value in preferences.dict(exclude_unset=True).items():
        setattr(preference, field, value)
    
    db.commit()
    db.refresh(preference)
    return preference