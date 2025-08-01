import redis
from typing import Optional, Any, Dict
import json
from datetime import timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            retry_on_error=[redis.ConnectionError, redis.TimeoutError],
            retry=redis.Retry(
                backoff=redis.ExponentialBackoff(base=0.1, cap=1.0),
                retries=3
            )
        )
        self._test_connection()
    
    def _test_connection(self):
        """Test Redis connection"""
        try:
            self.client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    # Token Management
    def store_device_token(self, user_id: int, device_token: str, platform: str, ttl: int = 86400 * 30):
        """Store device token with 30 days TTL"""
        key = f"device_token:{user_id}:{device_token}"
        value = {
            "platform": platform,
            "user_id": user_id,
            "device_token": device_token
        }
        self.client.setex(key, ttl, json.dumps(value))
        
        # Add to user's device set
        self.client.sadd(f"user_devices:{user_id}", device_token)
    
    def get_user_device_tokens(self, user_id: int) -> list:
        """Get all active device tokens for a user"""
        device_tokens = self.client.smembers(f"user_devices:{user_id}")
        active_tokens = []
        
        for token in device_tokens:
            key = f"device_token:{user_id}:{token}"
            if self.client.exists(key):
                active_tokens.append(token)
            else:
                # Clean up expired token from set
                self.client.srem(f"user_devices:{user_id}", token)
        
        return active_tokens
    
    def remove_device_token(self, user_id: int, device_token: str):
        """Remove device token"""
        key = f"device_token:{user_id}:{device_token}"
        self.client.delete(key)
        self.client.srem(f"user_devices:{user_id}", device_token)
    
    # Notification Queue
    def add_to_notification_queue(self, notification_data: Dict[str, Any]):
        """Add notification to processing queue"""
        self.client.lpush("notification_queue", json.dumps(notification_data))
    
    def get_from_notification_queue(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Get notification from queue (blocking if timeout > 0)"""
        if timeout > 0:
            result = self.client.brpop("notification_queue", timeout=timeout)
            if result:
                return json.loads(result[1])
        else:
            result = self.client.rpop("notification_queue")
            if result:
                return json.loads(result)
        return None
    
    # Rate Limiting
    def check_rate_limit(self, user_id: int, limit: int = 100, window: int = 3600) -> bool:
        """Check if user has exceeded rate limit"""
        key = f"rate_limit:push:{user_id}"
        current_count = self.client.incr(key)
        
        if current_count == 1:
            self.client.expire(key, window)
        
        return current_count <= limit
    
    # Notification Status Tracking
    def set_notification_status(self, notification_id: int, status: str, ttl: int = 86400):
        """Track notification delivery status"""
        key = f"notification_status:{notification_id}"
        self.client.setex(key, ttl, status)
    
    def get_notification_status(self, notification_id: int) -> Optional[str]:
        """Get notification status"""
        return self.client.get(f"notification_status:{notification_id}")
    
    # Batch Processing
    def add_batch_notification(self, batch_id: str, user_ids: list):
        """Add users to batch notification set"""
        key = f"batch:{batch_id}"
        for user_id in user_ids:
            self.client.sadd(key, user_id)
        self.client.expire(key, 3600)  # 1 hour TTL
    
    def get_batch_users(self, batch_id: str, count: int = 100) -> list:
        """Get users from batch (and remove them)"""
        key = f"batch:{batch_id}"
        users = []
        for _ in range(count):
            user_id = self.client.spop(key)
            if user_id:
                users.append(int(user_id))
            else:
                break
        return users
    
    def get_batch_size(self, batch_id: str) -> int:
        """Get remaining batch size"""
        return self.client.scard(f"batch:{batch_id}")
    
    # Caching
    def cache_set(self, key: str, value: Any, ttl: int = 300):
        """Set cache with TTL (default 5 minutes)"""
        cache_key = f"cache:{key}"
        self.client.setex(cache_key, ttl, json.dumps(value))
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        cache_key = f"cache:{key}"
        value = self.client.get(cache_key)
        if value:
            return json.loads(value)
        return None
    
    def cache_delete(self, key: str):
        """Delete from cache"""
        cache_key = f"cache:{key}"
        self.client.delete(cache_key)
    
    # Stats
    def increment_stat(self, stat_name: str, date: Optional[str] = None):
        """Increment daily statistics"""
        if not date:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
        
        key = f"stats:{stat_name}:{date}"
        self.client.incr(key)
        self.client.expire(key, 86400 * 7)  # Keep for 7 days
    
    def get_stat(self, stat_name: str, date: str) -> int:
        """Get daily statistics"""
        key = f"stats:{stat_name}:{date}"
        value = self.client.get(key)
        return int(value) if value else 0


# Singleton instance
redis_client = RedisClient()