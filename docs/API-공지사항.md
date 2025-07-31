# 공지사항 API 문서

## 개요
교회 공지사항을 관리하는 API입니다. 관리자와 교역자가 공지사항을 작성하고 관리할 수 있습니다.

## 엔드포인트

### 1. 공지사항 목록 조회
**GET** `/api/v1/announcements/`

공지사항 목록을 조회합니다. 고정된 공지사항이 먼저 표시되고, 그 다음 최신순으로 정렬됩니다.

**Query Parameters:**
- `skip`: 건너뛸 개수 (기본값: 0)
- `limit`: 조회할 개수 (기본값: 100, 최대: 100)
- `is_active`: 활성 상태 필터 (true/false)
- `is_pinned`: 고정 상태 필터 (true/false)

**Response:**
```json
[
    {
        "id": 1,
        "title": "2025년 신년 예배 안내",
        "content": "새해를 맞이하여...",
        "church_id": 1,
        "author_id": 1,
        "author_name": "홍길동 목사",
        "is_active": true,
        "is_pinned": true,
        "target_audience": "all",
        "created_at": "2025-01-01T00:00:00",
        "updated_at": null
    }
]
```

### 2. 공지사항 상세 조회
**GET** `/api/v1/announcements/{announcement_id}`

특정 공지사항의 상세 정보를 조회합니다.

**Response:**
```json
{
    "id": 1,
    "title": "2025년 신년 예배 안내",
    "content": "새해를 맞이하여 신년 예배를 드립니다.\n\n일시: 2025년 1월 1일(수) 오전 10시\n장소: 본당",
    "church_id": 1,
    "author_id": 1,
    "author_name": "홍길동 목사",
    "is_active": true,
    "is_pinned": true,
    "target_audience": "all",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": null
}
```

### 3. 공지사항 작성
**POST** `/api/v1/announcements/`

새로운 공지사항을 작성합니다. 관리자와 교역자만 작성 가능합니다.

**Request Body:**
```json
{
    "title": "주일학교 겨울 성경학교 등록 안내",
    "content": "2025년 겨울 성경학교 등록을 받습니다...",
    "is_active": true,
    "is_pinned": false,
    "target_audience": "youth"
}
```

**Response:** 생성된 공지사항 정보

### 4. 공지사항 수정
**PUT** `/api/v1/announcements/{announcement_id}`

공지사항을 수정합니다. 작성자 본인 또는 관리자만 수정 가능합니다.

**Request Body:**
```json
{
    "title": "수정된 제목",
    "content": "수정된 내용",
    "is_active": true,
    "is_pinned": false,
    "target_audience": "all"
}
```

### 5. 공지사항 삭제
**DELETE** `/api/v1/announcements/{announcement_id}`

공지사항을 삭제합니다. 작성자 본인 또는 관리자만 삭제 가능합니다.

**Response:**
```json
{
    "message": "Announcement deleted successfully"
}
```

### 6. 공지사항 고정 토글
**PUT** `/api/v1/announcements/{announcement_id}/toggle-pin`

공지사항의 고정 상태를 토글합니다. 관리자만 사용 가능합니다.

**Response:** 업데이트된 공지사항 정보

## 필드 설명

### target_audience (대상)
- `all`: 전체
- `member`: 일반 교인
- `youth`: 청소년부
- `leader`: 리더

### 권한
- **조회**: 모든 로그인 사용자
- **작성**: 관리자(admin), 교역자(minister)
- **수정/삭제**: 작성자 본인 또는 관리자
- **고정**: 관리자만

## 사용 예시

### JavaScript/Fetch
```javascript
// 공지사항 목록 조회
const response = await fetch('/api/v1/announcements/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
const announcements = await response.json();

// 새 공지사항 작성
const response = await fetch('/api/v1/announcements/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        title: '교회 소식',
        content: '이번 주 교회 일정 안내...',
        is_pinned: true,
        target_audience: 'all'
    })
});
```

### Flutter/Dart
```dart
// 공지사항 목록 조회
final response = await http.get(
    Uri.parse('$baseUrl/api/v1/announcements/'),
    headers: {'Authorization': 'Bearer $token'},
);

// 활성 공지사항만 조회
final response = await http.get(
    Uri.parse('$baseUrl/api/v1/announcements/?is_active=true'),
    headers: {'Authorization': 'Bearer $token'},
);
```

## 대시보드 접속

웹 브라우저에서 다음 주소로 접속하여 공지사항을 관리할 수 있습니다:
- 로그인: `http://localhost:8000/login`
- 대시보드: `http://localhost:8000/dashboard`

대시보드에서는 공지사항을 시각적으로 관리할 수 있으며, 다음 기능을 제공합니다:
- 공지사항 목록 보기 (고정/활성 필터)
- 새 공지사항 작성
- 공지사항 수정/삭제
- 공지사항 고정/해제
- 작성자 및 작성 시간 확인