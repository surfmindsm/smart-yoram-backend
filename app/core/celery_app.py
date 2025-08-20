from celery import Celery
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    celery_app = Celery(
        "smart_yoram",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=["app.tasks.notifications"],
    )

    # Configure Celery
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Seoul",
        enable_utc=True,
        result_expires=3600,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes
        task_soft_time_limit=240,  # 4 minutes
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
    )

    # Beat schedule for periodic tasks
    from celery.schedules import crontab

    celery_app.conf.beat_schedule = {
        # Send worship reminders every Sunday at 8 AM
        "worship-reminder-sunday": {
            "task": "app.tasks.notifications.send_worship_reminders",
            "schedule": crontab(hour=8, minute=0, day_of_week=0),  # Sunday
        },
        # Send birthday notifications daily at 9 AM
        "birthday-notifications": {
            "task": "app.tasks.notifications.send_birthday_notifications",
            "schedule": crontab(hour=9, minute=0),
        },
        # Process notification queue every minute
        "process-notification-queue": {
            "task": "app.tasks.notifications.process_notification_queue",
            "schedule": 60.0,  # Every 60 seconds
        },
        # Cleanup expired tokens daily at 2 AM
        "cleanup-expired-tokens": {
            "task": "app.tasks.notifications.cleanup_expired_tokens",
            "schedule": crontab(hour=2, minute=0),
        },
    }
    logger.info("Celery app initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Celery: {e}")
    logger.warning("Background tasks will be disabled")

    # Create a dummy Celery app that does nothing
    class DummyCelery:
        def task(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def delay(self, *args, **kwargs):
            pass

        def apply_async(self, *args, **kwargs):
            pass

        conf = type(
            "conf",
            (),
            {"beat_schedule": {}, "update": lambda self, *args, **kwargs: None},
        )()

    celery_app = DummyCelery()
