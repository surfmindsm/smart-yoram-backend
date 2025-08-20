import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Dict, Optional
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.push_notification import (
    UserDevice,
    PushNotification,
    NotificationRecipient,
    NotificationStatus,
    NotificationType,
)
from app.models.user import User
from app.core.config import settings
from app.core.redis import redis_client
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
    logger.warning("Push notifications will be disabled")

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
        notification_type: NotificationType = NotificationType.CUSTOM,
    ) -> Dict[str, any]:
        """단일 사용자에게 푸시 알림 발송"""
        result = {
            "success": False,
            "message": "",
            "notification_id": None,
            "sent_count": 0,
            "failed_count": 0,
            "no_device_count": 0,
        }

        # Get user info
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            result["message"] = "사용자를 찾을 수 없습니다"
            return result

        # Create notification record first (always save history)
        notification = PushNotification(
            church_id=user.church_id,
            type=notification_type,
            title=title,
            body=body,
            data=data,
            image_url=image_url,
            target_type="individual",
            target_users=[user_id],
            total_recipients=1,
            sent_count=0,
            failed_count=0,
        )
        db.add(notification)
        db.commit()
        result["notification_id"] = notification.id

        # Check rate limit
        if not redis_client.check_rate_limit(user_id):
            notification.failed_count = 1
            db.commit()
            result["message"] = "발송 한도를 초과했습니다"
            result["failed_count"] = 1
            # Add recipient record with rate limit status
            recipient = NotificationRecipient(
                notification_id=notification.id,
                user_id=user_id,
                status=NotificationStatus.FAILED,
                error_message="Rate limit exceeded",
            )
            db.add(recipient)
            db.commit()
            return result

        # Get user's active devices
        device_tokens = redis_client.get_user_device_tokens(user_id)

        if not device_tokens:
            # Fallback to database
            devices = (
                db.query(UserDevice)
                .filter(UserDevice.user_id == user_id, UserDevice.is_active == True)
                .all()
            )
        else:
            # Get device details from DB using tokens
            devices = (
                db.query(UserDevice)
                .filter(
                    UserDevice.device_token.in_(device_tokens),
                    UserDevice.is_active == True,
                )
                .all()
            )

        if not devices:
            notification.failed_count = 1
            db.commit()
            result["message"] = "등록된 기기가 없습니다"
            result["no_device_count"] = 1
            # Add recipient record with no device status
            recipient = NotificationRecipient(
                notification_id=notification.id,
                user_id=user_id,
                status=NotificationStatus.FAILED,
                error_message="No active devices",
            )
            db.add(recipient)
            db.commit()
            return result

        # Send to all user devices
        success_count = 0
        failed_count = 0

        for device in devices:
            try:
                await PushNotificationService._send_fcm_message(
                    device_token=device.device_token,
                    title=title,
                    body=body,
                    data=data,
                    image_url=image_url,
                    platform=device.platform,
                )

                # Record success
                recipient = NotificationRecipient(
                    notification_id=notification.id,
                    user_id=user_id,
                    device_id=device.id,
                    status=NotificationStatus.SENT,
                    sent_at=datetime.now(timezone.utc),
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
                    error_message=str(e),
                )
                db.add(recipient)
                failed_count += 1

        # Update notification stats
        notification.sent_count = success_count
        notification.failed_count = failed_count
        notification.sent_at = datetime.now(timezone.utc)
        db.commit()

        result["success"] = success_count > 0
        result["sent_count"] = success_count
        result["failed_count"] = failed_count
        result["message"] = f"성공: {success_count}개, 실패: {failed_count}개"

        return result

    @staticmethod
    async def send_to_multiple_users(
        db: Session,
        user_ids: List[int],
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        notification_type: NotificationType = NotificationType.CUSTOM,
        church_id: Optional[int] = None,
    ) -> Dict[str, any]:
        """여러 사용자에게 푸시 알림 발송"""
        result = {
            "success": False,
            "message": "",
            "notification_id": None,
            "total_users": len(user_ids),
            "sent_count": 0,
            "failed_count": 0,
            "no_device_users": [],
        }

        # Get church_id if not provided
        if not church_id and user_ids:
            first_user = db.query(User).filter(User.id == user_ids[0]).first()
            if first_user:
                church_id = first_user.church_id

        # Create notification record first (always save history)
        notification = PushNotification(
            church_id=church_id,
            type=notification_type,
            title=title,
            body=body,
            data=data,
            image_url=image_url,
            target_type="group",
            target_users=user_ids,
            total_recipients=len(user_ids),
            sent_count=0,
            failed_count=0,
        )
        db.add(notification)
        db.commit()
        result["notification_id"] = notification.id

        # Get all active devices for users
        devices = (
            db.query(UserDevice)
            .join(User)
            .filter(UserDevice.user_id.in_(user_ids), UserDevice.is_active == True)
            .all()
        )

        # Track users without devices
        users_with_devices = set()
        for device in devices:
            users_with_devices.add(device.user_id)

        users_without_devices = set(user_ids) - users_with_devices
        result["no_device_users"] = list(users_without_devices)

        # Add recipient records for users without devices
        for user_id in users_without_devices:
            recipient = NotificationRecipient(
                notification_id=notification.id,
                user_id=user_id,
                status=NotificationStatus.FAILED,
                error_message="No active devices",
            )
            db.add(recipient)

        if not devices:
            notification.failed_count = len(user_ids)
            db.commit()
            result["message"] = "등록된 기기가 있는 사용자가 없습니다"
            result["failed_count"] = len(user_ids)
            return result

        # Group devices by user
        user_devices = {}
        for device in devices:
            if device.user_id not in user_devices:
                user_devices[device.user_id] = []
            user_devices[device.user_id].append(device)

        # Send notifications in batches
        messages = []
        device_map = {}

        for user_id, user_devices_list in user_devices.items():
            # Check rate limit per user
            if not redis_client.check_rate_limit(user_id):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                recipient = NotificationRecipient(
                    notification_id=notification.id,
                    user_id=user_id,
                    status=NotificationStatus.FAILED,
                    error_message="Rate limit exceeded",
                )
                db.add(recipient)
                continue

            for device in user_devices_list:
                message = PushNotificationService._create_fcm_message(
                    device_token=device.device_token,
                    title=title,
                    body=body,
                    data=data,
                    image_url=image_url,
                    platform=device.platform,
                )
                messages.append(message)
                device_map[device.device_token] = (user_id, device.id)

        # Send batch (FCM supports up to 500 messages per batch)
        success_count = 0
        failed_count = 0

        if messages:
            for i in range(0, len(messages), 500):
                batch = messages[i : i + 500]
                try:
                    batch_response = await PushNotificationService._send_batch_fcm(
                        batch
                    )

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
                                sent_at=datetime.now(timezone.utc),
                            )
                            success_count += 1
                        else:
                            recipient = NotificationRecipient(
                                notification_id=notification.id,
                                user_id=user_id,
                                device_id=device_id,
                                status=NotificationStatus.FAILED,
                                error_message=str(response.exception),
                            )
                            failed_count += 1

                        db.add(recipient)
                except Exception as e:
                    logger.error(f"Batch send failed: {e}")
                    # Mark all in batch as failed
                    for message in batch:
                        user_id, device_id = device_map[message.token]
                        recipient = NotificationRecipient(
                            notification_id=notification.id,
                            user_id=user_id,
                            device_id=device_id,
                            status=NotificationStatus.FAILED,
                            error_message=str(e),
                        )
                        db.add(recipient)
                        failed_count += 1

        # Update notification stats
        notification.sent_count = success_count
        notification.failed_count = failed_count + len(users_without_devices)
        notification.sent_at = datetime.now(timezone.utc)
        db.commit()

        result["success"] = success_count > 0
        result["sent_count"] = success_count
        result["failed_count"] = failed_count + len(users_without_devices)

        if users_without_devices:
            result["message"] = (
                f"성공: {success_count}명, 실패: {failed_count}명, 기기 없음: {len(users_without_devices)}명"
            )
        else:
            result["message"] = f"성공: {success_count}명, 실패: {failed_count}명"

        return result

    @staticmethod
    async def send_to_church(
        db: Session,
        church_id: int,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        notification_type: NotificationType = NotificationType.ANNOUNCEMENT,
    ) -> Dict[str, any]:
        """교회 전체 구성원에게 푸시 알림 발송"""
        # Get all active users in church
        user_ids = (
            db.query(User.id)
            .filter(User.church_id == church_id, User.is_active == True)
            .all()
        )
        user_ids = [user_id[0] for user_id in user_ids]

        if not user_ids:
            # Still create notification record for history
            notification = PushNotification(
                church_id=church_id,
                type=notification_type,
                title=title,
                body=body,
                data=data,
                image_url=image_url,
                target_type="church",
                target_users=[],
                total_recipients=0,
                sent_count=0,
                failed_count=0,
            )
            db.add(notification)
            db.commit()

            return {
                "success": False,
                "message": "활성 사용자가 없습니다",
                "notification_id": notification.id,
                "total_users": 0,
                "sent_count": 0,
                "failed_count": 0,
            }

        # Update target type to church
        result = await PushNotificationService.send_to_multiple_users(
            db=db,
            user_ids=user_ids,
            title=title,
            body=body,
            data=data,
            image_url=image_url,
            notification_type=notification_type,
            church_id=church_id,
        )

        # Update target type
        if result.get("notification_id"):
            notification = (
                db.query(PushNotification)
                .filter(PushNotification.id == result["notification_id"])
                .first()
            )
            if notification:
                notification.target_type = "church"
                db.commit()

        return result

    @staticmethod
    def _create_fcm_message(
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        platform: str = "android",
    ) -> messaging.Message:
        """FCM 메시지 생성"""
        notification = messaging.Notification(title=title, body=body, image=image_url)

        # Platform specific configuration
        android_config = None
        apns_config = None

        if platform == "android":
            android_config = messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    click_action="FLUTTER_NOTIFICATION_CLICK",
                    channel_id="default_channel",
                ),
            )
        else:  # iOS
            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(badge=1, sound="default")
                )
            )

        return messaging.Message(
            notification=notification,
            data=data or {},
            token=device_token,
            android=android_config,
            apns=apns_config,
        )

    @staticmethod
    async def _send_fcm_message(
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        image_url: Optional[str] = None,
        platform: str = "android",
    ):
        """단일 FCM 메시지 발송"""
        message = PushNotificationService._create_fcm_message(
            device_token, title, body, data, image_url, platform
        )

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, messaging.send, message)

    @staticmethod
    async def _send_batch_fcm(messages: List[messaging.Message]):
        """배치 FCM 메시지 발송"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, messaging.send_all, messages)

    @staticmethod
    def register_device(
        db: Session,
        user_id: int,
        device_token: str,
        platform: str,
        device_model: Optional[str] = None,
        app_version: Optional[str] = None,
    ) -> UserDevice:
        """기기 토큰 등록"""
        # Check if device already exists
        existing_device = (
            db.query(UserDevice).filter(UserDevice.device_token == device_token).first()
        )

        if existing_device:
            # Update existing device
            existing_device.user_id = user_id
            existing_device.platform = platform
            existing_device.device_model = device_model
            existing_device.app_version = app_version
            existing_device.is_active = True
            existing_device.last_used_at = datetime.now(timezone.utc)
        else:
            # Create new device
            existing_device = UserDevice(
                user_id=user_id,
                device_token=device_token,
                platform=platform,
                device_model=device_model,
                app_version=app_version,
                is_active=True,
                last_used_at=datetime.now(timezone.utc),
            )
            db.add(existing_device)

        db.commit()

        # Store in Redis cache
        redis_client.store_device_token(user_id, device_token, platform)

        return existing_device

    @staticmethod
    def unregister_device(db: Session, device_token: str):
        """기기 토큰 등록 해제"""
        device = (
            db.query(UserDevice).filter(UserDevice.device_token == device_token).first()
        )

        if device:
            device.is_active = False
            db.commit()

            # Remove from Redis cache
            redis_client.remove_device_token(device.user_id, device_token)

    @staticmethod
    def mark_notification_read(db: Session, notification_id: int, user_id: int):
        """알림 읽음 처리"""
        recipient = (
            db.query(NotificationRecipient)
            .filter(
                NotificationRecipient.notification_id == notification_id,
                NotificationRecipient.user_id == user_id,
            )
            .first()
        )

        if recipient and recipient.status == NotificationStatus.SENT:
            recipient.status = NotificationStatus.READ
            recipient.read_at = datetime.now(timezone.utc)

            # Update notification read count
            notification = (
                db.query(PushNotification)
                .filter(PushNotification.id == notification_id)
                .first()
            )
            if notification:
                notification.read_count = (notification.read_count or 0) + 1

            db.commit()
