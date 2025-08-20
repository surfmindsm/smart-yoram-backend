from celery import shared_task
from celery.utils.log import get_task_logger
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio

from app.db.session import SessionLocal
from app.models.user import User
from app.models.member import Member
from app.models.worship_schedule import WorshipService
from app.models.push_notification import (
    PushNotification,
    NotificationType,
    NotificationStatus,
    UserDevice,
    NotificationRecipient,
)
from app.services.push_notification import PushNotificationService
from app.core.redis import redis_client

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def send_push_notification_task(self, notification_id: int):
    """Send push notification with retry logic"""
    db = SessionLocal()
    try:
        notification = (
            db.query(PushNotification)
            .filter(PushNotification.id == notification_id)
            .first()
        )

        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return

        # Use Redis to track processing status
        redis_client.set_notification_status(notification_id, "processing")

        # Get target users
        if notification.target_type == "all":
            user_ids = (
                db.query(User.id)
                .filter(
                    User.church_id == notification.church_id, User.is_active == True
                )
                .all()
            )
            user_ids = [uid[0] for uid in user_ids]
        else:
            user_ids = notification.target_users

        # Process in batches using Redis
        batch_id = f"notification_{notification_id}"
        redis_client.add_batch_notification(batch_id, user_ids)

        total_sent = 0
        total_failed = 0

        while redis_client.get_batch_size(batch_id) > 0:
            batch_users = redis_client.get_batch_users(batch_id, count=50)

            # Send notifications asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                PushNotificationService.send_to_multiple_users(
                    db=db,
                    user_ids=batch_users,
                    title=notification.title,
                    body=notification.body,
                    data=notification.data,
                    image_url=notification.image_url,
                    notification_type=notification.type,
                    church_id=notification.church_id,
                )
            )

            total_sent += result.get("success", 0)
            total_failed += result.get("failed", 0)

        # Update notification status
        notification.sent_count = total_sent
        notification.failed_count = total_failed
        notification.sent_at = datetime.utcnow()
        db.commit()

        redis_client.set_notification_status(notification_id, "completed")
        logger.info(
            f"Notification {notification_id} sent: {total_sent} success, {total_failed} failed"
        )

    except Exception as e:
        logger.error(f"Error sending notification {notification_id}: {e}")
        redis_client.set_notification_status(notification_id, "failed")

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))
    finally:
        db.close()


@shared_task
def send_worship_reminders():
    """Send worship reminder notifications"""
    db = SessionLocal()
    try:
        # Get all churches
        from app.models.church import Church

        churches = db.query(Church).filter(Church.is_active == True).all()

        for church in churches:
            # Get Sunday worship services
            services = (
                db.query(WorshipService)
                .filter(
                    WorshipService.church_id == church.id,
                    WorshipService.day_of_week == 6,  # Sunday
                    WorshipService.is_active == True,
                )
                .all()
            )

            if not services:
                continue

            # Create reminder message
            service_times = []
            for service in services:
                service_times.append(
                    f"{service.name}: {service.start_time.strftime('%H:%M')}"
                )

            title = "주일예배 안내"
            body = f"오늘의 예배 시간입니다.\n" + "\n".join(service_times)

            # Create notification
            notification = PushNotification(
                church_id=church.id,
                type=NotificationType.WORSHIP_REMINDER,
                title=title,
                body=body,
                target_type="all",
                data={
                    "type": "worship_reminder",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                },
            )
            db.add(notification)
            db.commit()

            # Send async
            send_push_notification_task.delay(notification.id)

    except Exception as e:
        logger.error(f"Error sending worship reminders: {e}")
    finally:
        db.close()


@shared_task
def send_birthday_notifications():
    """Send birthday notifications"""
    db = SessionLocal()
    try:
        today = datetime.now().date()

        # Get all members with birthday today
        members = (
            db.query(Member)
            .filter(
                db.extract("month", Member.birth_date) == today.month,
                db.extract("day", Member.birth_date) == today.day,
                Member.is_active == True,
            )
            .all()
        )

        for member in members:
            # Get church members to notify (department members, leaders, etc.)
            church_id = member.church_id

            # Create birthday notification
            title = "생일 축하"
            body = f"오늘은 {member.name}님의 생일입니다. 축하 인사를 전해주세요!"

            notification = PushNotification(
                church_id=church_id,
                type=NotificationType.BIRTHDAY,
                title=title,
                body=body,
                target_type="all",
                data={
                    "type": "birthday",
                    "member_id": member.id,
                    "member_name": member.name,
                },
            )
            db.add(notification)
            db.commit()

            # Send async
            send_push_notification_task.delay(notification.id)

    except Exception as e:
        logger.error(f"Error sending birthday notifications: {e}")
    finally:
        db.close()


@shared_task
def process_notification_queue():
    """Process notifications from Redis queue"""
    max_processing = 10
    processed = 0

    while processed < max_processing:
        notification_data = redis_client.get_from_notification_queue()
        if not notification_data:
            break

        try:
            # Process notification
            notification_id = notification_data.get("notification_id")
            if notification_id:
                send_push_notification_task.delay(notification_id)
                processed += 1
        except Exception as e:
            logger.error(f"Error processing queued notification: {e}")

    if processed > 0:
        logger.info(f"Processed {processed} notifications from queue")


@shared_task
def cleanup_expired_tokens():
    """Clean up expired device tokens"""
    db = SessionLocal()
    try:
        # Find tokens not used in 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)

        expired_devices = (
            db.query(UserDevice).filter(UserDevice.last_used_at < cutoff_date).all()
        )

        for device in expired_devices:
            # Remove from Redis
            redis_client.remove_device_token(device.user_id, device.device_token)

            # Mark as inactive in DB
            device.is_active = False

        db.commit()
        logger.info(f"Cleaned up {len(expired_devices)} expired device tokens")

    except Exception as e:
        logger.error(f"Error cleaning up tokens: {e}")
    finally:
        db.close()


@shared_task(bind=True, max_retries=3)
def retry_failed_notification(self, recipient_id: int):
    """Retry failed notification delivery"""
    db = SessionLocal()
    try:
        recipient = (
            db.query(NotificationRecipient)
            .filter(NotificationRecipient.id == recipient_id)
            .first()
        )

        if not recipient or recipient.status != NotificationStatus.FAILED:
            return

        notification = recipient.notification
        device = recipient.device

        if not device or not device.is_active:
            return

        # Retry sending
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                PushNotificationService._send_fcm_message(
                    device_token=device.device_token,
                    title=notification.title,
                    body=notification.body,
                    data=notification.data,
                    image_url=notification.image_url,
                    platform=device.platform,
                )
            )

            # Update status
            recipient.status = NotificationStatus.SENT
            recipient.sent_at = datetime.utcnow()
            db.commit()

            logger.info(
                f"Successfully retried notification for recipient {recipient_id}"
            )

        except Exception as e:
            logger.error(f"Retry failed for recipient {recipient_id}: {e}")
            raise self.retry(exc=e, countdown=300 * (2**self.request.retries))

    finally:
        db.close()
