# Push Notifications Implementation Guide

## Backend Implementation Details

### 1. Database Models

#### UserDevice Model
```python
class UserDevice(Base):
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_token = Column(String(255), nullable=False, unique=True, index=True)
    platform = Column(Enum(DevicePlatform), nullable=False)
    device_model = Column(String(100))
    app_version = Column(String(20))
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

#### PushNotification Model
```python
class PushNotification(Base):
    __tablename__ = "push_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    type = Column(Enum(NotificationType), default=NotificationType.CUSTOM)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    data = Column(JSON)
    image_url = Column(String(500))
    target_type = Column(String(20), nullable=False)  # individual, group, church
    target_users = Column(JSON)  # List of user IDs
    target_groups = Column(JSON)  # List of group identifiers
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    read_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

### 2. Service Layer

#### PushNotificationService
주요 메서드:
- `send_to_user()`: 개별 사용자 발송
- `send_to_multiple_users()`: 다중 사용자 발송
- `send_to_church()`: 교회 전체 발송
- `register_device()`: 기기 등록
- `unregister_device()`: 기기 해제
- `mark_notification_read()`: 읽음 처리

#### 핵심 기능 구현

**1. 알림 발송 플로우**
```python
async def send_to_user(db, user_id, title, body, ...):
    # 1. 사용자 정보 확인
    user = db.query(User).filter(User.id == user_id).first()
    
    # 2. 알림 레코드 생성 (항상)
    notification = PushNotification(...)
    db.add(notification)
    db.commit()
    
    # 3. Rate Limiting 체크
    if not redis_client.check_rate_limit(user_id):
        # 실패 기록
        
    # 4. 활성 기기 조회
    devices = get_user_devices(user_id)
    
    # 5. FCM 메시지 발송
    for device in devices:
        try:
            await send_fcm_message(device)
            # 성공 기록
        except Exception as e:
            # 실패 기록
    
    # 6. 통계 업데이트
    notification.sent_count = success_count
    notification.failed_count = failed_count
    
    return result
```

**2. 배치 발송 최적화**
```python
# FCM은 한 번에 최대 500개 메시지 지원
for i in range(0, len(messages), 500):
    batch = messages[i:i + 500]
    batch_response = await send_batch_fcm(batch)
    process_batch_response(batch_response)
```

**3. 에러 처리**
```python
# 모든 실패는 NotificationRecipient에 기록
recipient = NotificationRecipient(
    notification_id=notification.id,
    user_id=user_id,
    device_id=device.id,
    status=NotificationStatus.FAILED,
    error_message=str(error)
)
db.add(recipient)
```

### 3. Redis Integration (Optional)

#### Redis 사용 용도
1. **Device Token Cache**
   ```python
   # 30일 TTL로 토큰 캐싱
   redis_client.store_device_token(user_id, token, platform, ttl=86400*30)
   ```

2. **Rate Limiting**
   ```python
   # 시간당 100건 제한
   def check_rate_limit(user_id, limit=100, window=3600):
       key = f"rate_limit:push:{user_id}"
       count = redis.incr(key)
       if count == 1:
           redis.expire(key, window)
       return count <= limit
   ```

3. **Notification Queue**
   ```python
   # 비동기 처리를 위한 큐
   redis_client.add_to_notification_queue(notification_data)
   ```

### 4. Celery Tasks (Optional)

#### 비동기 작업
```python
@celery_app.task
def send_bulk_notifications(notification_id):
    """대량 알림 비동기 처리"""
    # DB에서 알림 정보 조회
    # 배치로 나누어 발송
    # 진행 상황 업데이트

@celery_app.task
def cleanup_expired_tokens():
    """만료된 토큰 정리"""
    # 90일 이상 사용하지 않은 토큰 비활성화

@celery_app.task
def send_worship_reminders():
    """예배 알림 자동 발송"""
    # 예배 30분 전 알림
```

### 5. Firebase Configuration

#### Firebase Admin SDK 초기화
```python
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
```

#### FCM 메시지 구성
```python
def create_fcm_message(token, title, body, data=None, image_url=None, platform="android"):
    notification = messaging.Notification(
        title=title,
        body=body,
        image=image_url
    )
    
    # Android 설정
    android_config = messaging.AndroidConfig(
        priority="high",
        notification=messaging.AndroidNotification(
            click_action="FLUTTER_NOTIFICATION_CLICK",
            channel_id="default_channel"
        )
    )
    
    # iOS 설정
    apns_config = messaging.APNSConfig(
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                badge=1,
                sound="default"
            )
        )
    )
    
    return messaging.Message(
        notification=notification,
        data=data or {},
        token=token,
        android=android_config if platform == "android" else None,
        apns=apns_config if platform == "ios" else None
    )
```

### 6. Error Handling & Fallback

#### Redis 연결 실패 처리
```python
class RedisClient:
    def __init__(self):
        try:
            self.client = redis.Redis.from_url(settings.REDIS_URL)
            self._test_connection()
            self.connected = True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.connected = False
    
    def check_rate_limit(self, user_id):
        if not self.connected:
            return True  # Redis 없으면 모두 허용
        # ...
```

#### Firebase 초기화 실패 처리
```python
try:
    firebase_admin.initialize_app(cred)
except Exception as e:
    logger.error(f"Firebase init failed: {e}")
    logger.warning("Push notifications will be disabled")
```

### 7. Performance Considerations

1. **Database Indexes**
   ```sql
   CREATE INDEX idx_user_devices_token ON user_devices(device_token);
   CREATE INDEX idx_user_devices_user_active ON user_devices(user_id, is_active);
   CREATE INDEX idx_notifications_church_created ON push_notifications(church_id, created_at DESC);
   ```

2. **Async Processing**
   ```python
   # ThreadPoolExecutor for FCM calls
   executor = ThreadPoolExecutor(max_workers=10)
   
   async def _send_fcm_message(...):
       loop = asyncio.get_event_loop()
       return await loop.run_in_executor(executor, messaging.send, message)
   ```

3. **Batch Operations**
   ```python
   # Bulk insert for recipients
   db.bulk_insert_mappings(NotificationRecipient, recipient_data)
   ```

### 8. Security Measures

1. **Permission Checks**
   ```python
   if current_user.role not in ["admin", "pastor"]:
       raise HTTPException(status_code=403, detail="권한이 없습니다")
   ```

2. **Church Isolation**
   ```python
   # 교회별 데이터 격리
   query = query.filter(PushNotification.church_id == current_user.church_id)
   ```

3. **Token Validation**
   ```python
   # FCM 토큰 형식 검증
   if not is_valid_fcm_token(device_token):
       raise ValueError("Invalid FCM token")
   ```

### 9. Monitoring & Logging

1. **Structured Logging**
   ```python
   logger.info("Notification sent", extra={
       "notification_id": notification.id,
       "user_id": user_id,
       "success": success_count,
       "failed": failed_count
   })
   ```

2. **Metrics Collection**
   ```python
   redis_client.increment_stat("push_sent", date)
   redis_client.increment_stat(f"push_type_{notification_type}", date)
   ```

### 10. Testing

1. **Test Device Registration**
   ```python
   @router.post("/test/register-device")
   def test_register_device(...):
       test_token = f"test_token_{uuid.uuid4().hex[:8]}"
       # 테스트 기기 등록
   ```

2. **Mock FCM for Testing**
   ```python
   if settings.TESTING:
       messaging.send = mock_send_function
   ```

## Deployment Considerations

1. **Environment Variables**
   ```env
   FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
   REDIS_URL=redis://localhost:6379/0
   ```

2. **Docker Configuration**
   ```dockerfile
   # Redis optional
   RUN pip install redis || true
   ```

3. **Health Checks**
   ```python
   @router.get("/health")
   def health_check():
       return {
           "firebase": firebase_connected,
           "redis": redis_client.connected,
           "celery": celery_connected
       }
   ```