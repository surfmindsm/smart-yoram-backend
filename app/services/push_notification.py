import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.push_notification import (
    UserDevice, PushNotification, NotificationRecipient,
    NotificationStatus, NotificationType
)
from app.models.user import User
from app.core.config import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

executor = ThreadPoolExecutor(max_workers=10)


class PushNotificationService:
    @staticmethod
    async def send_to_user(
        db: Session,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        notification_type: NotificationType = NotificationType.CUSTOM
    ) -> bool:
        """단일 사용자에게 푸시 알림 발송"""
        # Get user's active devices
        devices = db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.is_active == True
        ).all()
        
        if not devices:
            logger.warning(f"No active devices found for user {user_id}")
            return False
        
        # Create notification record
        notification = PushNotification(
            church_id=db.query(User).filter(User.id == user_id).first().church_id,
            type=notification_type,
            title=title,
            body=body,
            data=data,
            image_url=image_url,
            target_type="individual",
            target_users=[user_id],
            total_recipients=1
        )
        db.add(notification)
        db.commit()
        
        # Send to all user devices
        success_count = 0
        for device in devices:
            try:
                await PushNotificationService._send_fcm_message(
                    device_token=device.device_token,
                    title=title,
                    body=body,
                    data=data,
                    image_url=image_url,
                    platform=device.platform
                )
                
                # Record success
                recipient = NotificationRecipient(
                    notification_id=notification.id,
                    user_id=user_id,
                    device_id=device.id,
                    status=NotificationStatus.SENT,
                    sent_at=datetime.utcnow()
                )
                db.add(recipient)
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send to device {device.id}: {e}")
                # Record failure
                recipient = NotificationRecipient(
                    notification_id=notification.id,
                    user_id=user_id,
                    device_id=device.id,
                    status=NotificationStatus.FAILED,
                    error_message=str(e)
                )
                db.add(recipient)
        
        # Update notification stats
        notification.sent_count = success_count
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        return success_count > 0
    
    @staticmethod
    async def send_to_multiple_users(
        db: Session,
        user_ids: List[int],
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        notification_type: NotificationType = NotificationType.CUSTOM,
        church_id: Optional[int] = None
    ) -> Dict[str, int]:
        """여러 사용자에게 푸시 알림 발송"""
        # Get all active devices for users
        devices = db.query(UserDevice).join(User).filter(
            UserDevice.user_id.in_(user_ids),
            UserDevice.is_active == True
        ).all()
        
        if not devices:
            logger.warning("No active devices found for specified users")
            return {"total": 0, "success": 0, "failed": 0}
        
        # Group devices by user
        user_devices = {}
        for device in devices:
            if device.user_id not in user_devices:
                user_devices[device.user_id] = []
            user_devices[device.user_id].append(device)
        
        # Create notification record
        if not church_id and user_ids:
            church_id = db.query(User).filter(User.id == user_ids[0]).first().church_id
            
        notification = PushNotification(
            church_id=church_id,
            type=notification_type,
            title=title,
            body=body,
            data=data,
            image_url=image_url,
            target_type="group",
            target_users=user_ids,
            total_recipients=len(user_ids)
        )
        db.add(notification)
        db.commit()
        
        # Send notifications in batches
        messages = []
        device_map = {}
        
        for user_id, user_devices_list in user_devices.items():
            for device in user_devices_list:
                message = PushNotificationService._create_fcm_message(
                    device_token=device.device_token,
                    title=title,
                    body=body,
                    data=data,
                    image_url=image_url,
                    platform=device.platform
                )
                messages.append(message)
                device_map[device.device_token] = (user_id, device.id)
        
        # Send batch (FCM supports up to 500 messages per batch)
        results = {"total": len(messages), "success": 0, "failed": 0}
        
        for i in range(0, len(messages), 500):
            batch = messages[i:i + 500]
            batch_response = await PushNotificationService._send_batch_fcm(batch)
            
            # Process responses
            for idx, response in enumerate(batch_response.responses):
                token = batch[idx].token
                user_id, device_id = device_map[token]
                
                if response.success:
                    recipient = NotificationRecipient(
                        notification_id=notification.id,
                        user_id=user_id,
                        device_id=device_id,
                        status=NotificationStatus.SENT,
                        sent_at=datetime.utcnow()
                    )
                    results["success"] += 1
                else:
                    recipient = NotificationRecipient(
                        notification_id=notification.id,
                        user_id=user_id,
                        device_id=device_id,
                        status=NotificationStatus.FAILED,
                        error_message=response.exception.message
                    )
                    results["failed"] += 1
                
                db.add(recipient)
        
        # Update notification stats
        notification.sent_count = results["success"]
        notification.failed_count = results["failed"]
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        return results
    
    @staticmethod
    async def send_to_church(
        db: Session,
        church_id: int,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        notification_type: NotificationType = NotificationType.ANNOUNCEMENT
    ) -> Dict[str, int]:
        """교회 전체 구성원에게 푸시 알림 발송"""
        # Get all active users in church
        user_ids = db.query(User.id).filter(
            User.church_id == church_id,
            User.is_active == True
        ).all()
        user_ids = [user_id[0] for user_id in user_ids]
        
        return await PushNotificationService.send_to_multiple_users(
            db=db,
            user_ids=user_ids,
            title=title,
            body=body,
            data=data,
            image_url=image_url,
            notification_type=notification_type,
            church_id=church_id
        )
    
    @staticmethod
    def _create_fcm_message(
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        platform: str = "android"
    ) -> messaging.Message:
        """FCM 메시지 생성"""
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url
        )
        
        # Platform-specific configurations
        android_config = messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default',
                click_action='FLUTTER_NOTIFICATION_CLICK',
                channel_id='default_channel'
            )
        )
        
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    badge=1
                )
            )
        )
        
        # Add custom data
        if data is None:
            data = {}
        data['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
        
        return messaging.Message(
            token=device_token,
            notification=notification,
            data=data,
            android=android_config,
            apns=apns_config
        )
    
    @staticmethod
    async def _send_fcm_message(
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        platform: str = "android"
    ):
        """단일 FCM 메시지 발송"""
        message = PushNotificationService._create_fcm_message(
            device_token, title, body, data, image_url, platform
        )
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor,
            messaging.send,
            message
        )
        return response
    
    @staticmethod
    async def _send_batch_fcm(messages: List[messaging.Message]):
        """배치 FCM 메시지 발송"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor,
            messaging.send_all,
            messages
        )
        return response
    
    @staticmethod
    async def register_device(
        db: Session,
        user_id: int,
        device_token: str,
        platform: str,
        device_model: Optional[str] = None,
        app_version: Optional[str] = None
    ) -> UserDevice:
        """디바이스 토큰 등록/업데이트"""
        # Check if device already exists
        device = db.query(UserDevice).filter(
            UserDevice.device_token == device_token
        ).first()
        
        if device:
            # Update existing device
            device.user_id = user_id
            device.platform = platform
            device.device_model = device_model
            device.app_version = app_version
            device.is_active = True
            device.last_used_at = datetime.utcnow()
        else:
            # Create new device
            device = UserDevice(
                user_id=user_id,
                device_token=device_token,
                platform=platform,
                device_model=device_model,
                app_version=app_version
            )
            db.add(device)
        
        db.commit()
        db.refresh(device)
        return device
    
    @staticmethod
    async def unregister_device(
        db: Session,
        device_token: str
    ) -> bool:
        """디바이스 토큰 비활성화"""
        device = db.query(UserDevice).filter(
            UserDevice.device_token == device_token
        ).first()
        
        if device:
            device.is_active = False
            db.commit()
            return True
        return False