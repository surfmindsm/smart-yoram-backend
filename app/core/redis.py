import redis
from typing import Optional, Any, Dict
import json
from datetime import timedelta
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self.client = None
        self.connected = False
        
        try:
            # Check if Retry is available (Redis 4.5.0+)
            redis_params = {
                "decode_responses": True,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
            }
            
            # Try to use newer retry mechanism if available
            if hasattr(redis, 'Retry') and hasattr(redis, 'ExponentialBackoff'):
                redis_params.update({
                    "retry_on_error": [redis.ConnectionError, redis.TimeoutError],
                    "retry": redis.Retry(
                        backoff=redis.ExponentialBackoff(base=0.1, cap=1.0),
                        retries=3
                    )
                })
            else:
                # Fallback for older Redis versions
                logger.warning("Redis.Retry not available, using legacy retry configuration")
                redis_params.update({
                    "retry_on_error": [redis.ConnectionError, redis.TimeoutError],
                    "max_connections": 10,
                })
            
            self.client = redis.Redis.from_url(settings.REDIS_URL, **redis_params)
            self._test_connection()
            self.connected = True
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            logger.warning("Redis is not available. Push notifications and caching will be disabled.")
            self.connected = False
    
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
        if not self.connected:
            logger.warning("Redis not connected, cannot store device token")
            return
            
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
        if not self.connected:
            logger.warning("Redis not connected, returning empty device tokens")
            return []
            
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
        if not self.connected:
            logger.warning("Redis not connected, cannot remove device token")
            return
            
        key = f"device_token:{user_id}:{device_token}"
        self.client.delete(key)
        self.client.srem(f"user_devices:{user_id}", device_token)
    
    # Notification Queue
    def add_to_notification_queue(self, notification_data: Dict[str, Any]):
        """Add notification to processing queue"""
        if not self.connected:
            logger.warning("Redis not connected, cannot add to notification queue")
            return
            
        self.client.lpush("notification_queue", json.dumps(notification_data))
    
    def get_from_notification_queue(self, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Get notification from queue (blocking if timeout > 0)"""
        if not self.connected:
            return None
            
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
        if not self.connected:
            # If Redis is not available, allow all requests
            return True
            
        key = f"rate_limit:push:{user_id}"
        current_count = self.client.incr(key)
        
        if current_count == 1:
            self.client.expire(key, window)
        
        return current_count <= limit
    
    # Notification Status Tracking
    def set_notification_status(self, notification_id: int, status: str, ttl: int = 86400):
        """Track notification delivery status"""
        if not self.connected:
            return
            
        key = f"notification_status:{notification_id}"
        self.client.setex(key, ttl, status)
    
    def get_notification_status(self, notification_id: int) -> Optional[str]:
        """Get notification status"""
        if not self.connected:
            return None
            
        return self.client.get(f"notification_status:{notification_id}")
    
    # Batch Processing
    def add_batch_notification(self, batch_id: str, user_ids: list):
        """Add users to batch notification set"""
        if not self.connected:
            return
            
        key = f"batch:{batch_id}"
        for user_id in user_ids:
            self.client.sadd(key, user_id)
        self.client.expire(key, 3600)  # 1 hour TTL
    
    def get_batch_users(self, batch_id: str, count: int = 100) -> list:
        """Get users from batch (and remove them)"""
        if not self.connected:
            return []
            
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
        if not self.connected:
            return 0
            
        return self.client.scard(f"batch:{batch_id}")
    
    # Caching
    def cache_set(self, key: str, value: Any, ttl: int = 300):
        """Set cache with TTL (default 5 minutes)"""
        if not self.connected:
            return
            
        cache_key = f"cache:{key}"
        self.client.setex(cache_key, ttl, json.dumps(value))
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get from cache"""
        if not self.connected:
            return None
            
        cache_key = f"cache:{key}"
        value = self.client.get(cache_key)
        if value:
            return json.loads(value)
        return None
    
    def cache_delete(self, key: str):
        """Delete from cache"""
        if not self.connected:
            return
            
        cache_key = f"cache:{key}"
        self.client.delete(cache_key)
    
    # Stats
    def increment_stat(self, stat_name: str, date: Optional[str] = None):
        """Increment daily statistics"""
        if not self.connected:
            return
            
        if not date:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
        
        key = f"stats:{stat_name}:{date}"
        self.client.incr(key)
        self.client.expire(key, 86400 * 7)  # Keep for 7 days
    
    def get_stat(self, stat_name: str, date: str) -> int:
        """Get daily statistics"""
        if not self.connected:
            return 0
            
        key = f"stats:{stat_name}:{date}"
        value = self.client.get(key)
        return int(value) if value else 0


# Singleton instance
try:
    redis_client = RedisClient()
except Exception as e:
    logger.error(f"Failed to create Redis client: {e}")
    # Create a dummy client that always returns safe defaults
    class DummyRedisClient:
        def __init__(self):
            self.connected = False
        
        def store_device_token(self, *args, **kwargs):
            pass
        
        def get_user_device_tokens(self, *args, **kwargs):
            return []
        
        def remove_device_token(self, *args, **kwargs):
            pass
        
        def add_to_notification_queue(self, *args, **kwargs):
            pass
        
        def get_from_notification_queue(self, *args, **kwargs):
            return None
        
        def check_rate_limit(self, *args, **kwargs):
            return True
        
        def set_notification_status(self, *args, **kwargs):
            pass
        
        def get_notification_status(self, *args, **kwargs):
            return None
        
        def add_batch_notification(self, *args, **kwargs):
            pass
        
        def get_batch_users(self, *args, **kwargs):
            return []
        
        def get_batch_size(self, *args, **kwargs):
            return 0
        
        def cache_set(self, *args, **kwargs):
            pass
        
        def cache_get(self, *args, **kwargs):
            return None
        
        def cache_delete(self, *args, **kwargs):
            pass
        
        def increment_stat(self, *args, **kwargs):
            pass
        
        def get_stat(self, *args, **kwargs):
            return 0
    
    redis_client = DummyRedisClient()