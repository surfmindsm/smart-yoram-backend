# Push Notifications API Documentation

## Base URL
```
https://your-domain.com/api/v1/notifications
```

## Authentication
모든 API 요청은 Bearer Token 인증이 필요합니다.
```
Authorization: Bearer {access_token}
```

## API Endpoints

### 1. 기기 등록
사용자의 모바일 기기를 푸시 알림 수신용으로 등록합니다.

**Endpoint:** `POST /devices`

**Request Body:**
```json
{
  "device_token": "string",  // FCM 토큰
  "platform": "android",     // android | ios
  "device_model": "string",  // 선택사항
  "app_version": "string"    // 선택사항
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 123,
  "device_token": "string",
  "platform": "android",
  "device_model": "Galaxy S21",
  "app_version": "1.0.0",
  "is_active": true,
  "last_used_at": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. 개별 알림 발송
특정 사용자에게 푸시 알림을 발송합니다.

**Endpoint:** `POST /send`

**권한:** admin, pastor

**Request Body:**
```json
{
  "user_id": 123,
  "title": "알림 제목",
  "body": "알림 내용",
  "type": "announcement",
  "data": {
    "key": "value"
  },
  "image_url": "https://example.com/image.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "message": "성공: 1개, 실패: 0개",
  "notification_id": 456,
  "sent_count": 1,
  "failed_count": 0,
  "no_device_count": 0
}
```

### 3. 다중 사용자 알림 발송
여러 사용자에게 동시에 푸시 알림을 발송합니다.

**Endpoint:** `POST /send-batch`

**권한:** admin, pastor

**Request Body:**
```json
{
  "user_ids": [1, 2, 3, 4, 5],
  "title": "단체 알림",
  "body": "알림 내용",
  "type": "announcement",
  "data": {},
  "image_url": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "성공: 3명, 실패: 1명, 기기 없음: 1명",
  "notification_id": 457,
  "total_users": 5,
  "sent_count": 3,
  "failed_count": 2,
  "no_device_users": [4]
}
```

### 4. 교회 전체 알림 발송
교회의 모든 활성 사용자에게 알림을 발송합니다.

**Endpoint:** `POST /send-to-church`

**권한:** admin, pastor

**Request Body:**
```json
{
  "title": "주일예배 안내",
  "body": "오전 9시 본당에서 예배가 있습니다.",
  "type": "worship_reminder",
  "data": {
    "worship_id": 123
  },
  "image_url": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "성공: 150명, 실패: 5명, 기기 없음: 20명",
  "notification_id": 458,
  "total_users": 175,
  "sent_count": 150,
  "failed_count": 25
}
```

### 5. 발송 이력 조회
알림 발송 이력을 조회합니다.

**Endpoint:** `GET /history`

**권한:** admin, pastor

**Query Parameters:**
- `skip`: 건너뛸 개수 (기본값: 0)
- `limit`: 조회할 개수 (기본값: 20)
- `notification_type`: 알림 유형 필터

**Response:**
```json
[
  {
    "id": 458,
    "type": "worship_reminder",
    "title": "주일예배 안내",
    "body": "오전 9시 본당에서 예배가 있습니다.",
    "target_type": "church",
    "total_recipients": 175,
    "sent_count": 150,
    "delivered_count": 145,
    "read_count": 120,
    "failed_count": 25,
    "sent_at": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "status": "partial"
  }
]
```

### 6. 내 알림 조회
현재 사용자가 받은 알림을 조회합니다.

**Endpoint:** `GET /my-notifications`

**Query Parameters:**
- `skip`: 건너뛸 개수 (기본값: 0)
- `limit`: 조회할 개수 (기본값: 20)
- `unread_only`: 읽지 않은 알림만 (기본값: false)

**Response:**
```json
{
  "items": [
    {
      "id": 789,
      "notification": {
        "id": 458,
        "title": "주일예배 안내",
        "body": "오전 9시 본당에서 예배가 있습니다.",
        "type": "worship_reminder",
        "image_url": null,
        "sent_at": "2024-01-01T00:00:00Z"
      },
      "status": "read",
      "sent_at": "2024-01-01T00:00:00Z",
      "delivered_at": "2024-01-01T00:01:00Z",
      "read_at": "2024-01-01T00:05:00Z"
    }
  ],
  "total": 50,
  "unread_count": 5
}
```

### 7. 알림 읽음 처리
알림을 읽음으로 표시합니다.

**Endpoint:** `PUT /{notification_id}/read`

**Response:**
```json
{
  "message": "알림을 읽음으로 표시했습니다"
}
```

### 8. 알림 설정 조회
사용자의 알림 수신 설정을 조회합니다.

**Endpoint:** `GET /preferences`

**Response:**
```json
{
  "id": 1,
  "user_id": 123,
  "announcement": true,
  "worship_reminder": true,
  "attendance": true,
  "birthday": true,
  "prayer_request": true,
  "system": true,
  "do_not_disturb": false,
  "dnd_start_time": "22:00",
  "dnd_end_time": "07:00",
  "push_enabled": true,
  "email_enabled": false,
  "sms_enabled": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 9. 알림 설정 변경
사용자의 알림 수신 설정을 변경합니다.

**Endpoint:** `PUT /preferences`

**Request Body:**
```json
{
  "announcement": false,
  "worship_reminder": true,
  "do_not_disturb": true,
  "dnd_start_time": "21:00",
  "dnd_end_time": "08:00"
}
```

**Response:**
```json
{
  // 업데이트된 설정 정보
}
```

### 10. 테스트 기기 등록
개발/테스트용 가상 기기를 등록합니다.

**Endpoint:** `POST /test/register-device`

**Response:**
```json
{
  "message": "Test device registered",
  "device_token": "test_token_a1b2c3d4",
  "user_id": 123
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "일부 사용자가 교회에 속하지 않습니다"
}
```

### 403 Forbidden
```json
{
  "detail": "권한이 없습니다"
}
```

### 404 Not Found
```json
{
  "detail": "알림을 찾을 수 없습니다"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Status Codes
- `200 OK`: 성공
- `201 Created`: 생성 성공
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 필요
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `500 Internal Server Error`: 서버 오류

## Rate Limiting
- 사용자당 시간당 100건 제한
- 초과 시 실패 응답과 함께 이력에 기록

## Webhook Events (Future)
알림 상태 변경 시 웹훅 이벤트 발송 예정
- `notification.sent`
- `notification.delivered`
- `notification.read`
- `notification.failed`