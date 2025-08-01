# Smart Yoram API 추가 엔드포인트 문서

## 📋 목차
1. [교인 인증](#교인-인증)
2. [교회 관리](#교회-관리)
3. [주보 관리](#주보-관리)
4. [공지사항 관리](#공지사항-관리)
5. [오늘의 말씀](#오늘의-말씀)

---

## 🔐 교인 인증

교인들이 자신의 계정으로 로그인할 수 있는 인증 시스템입니다.

### 교인 로그인
```http
POST /auth/member/login
Content-Type: application/x-www-form-urlencoded

username={phone_number}&password={password}
```

**응답**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "010-1234-5678",
    "email": "member@church.com",
    "full_name": "김철수",
    "role": "member",
    "member_id": 123,
    "is_first_login": false
  }
}
```

### 교인 첫 로그인 설정
```http
POST /auth/member/first-login
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_password": "newSecurePassword",
  "confirm_password": "newSecurePassword"
}
```

**응답**:
```json
{
  "message": "First login setup completed successfully",
  "user": {
    "id": 1,
    "username": "010-1234-5678",
    "is_first_login": false
  }
}
```

---

## ⛪ 교회 관리

교회 정보를 관리하는 엔드포인트입니다.

### 교회 목록 조회 (슈퍼관리자만)
```http
GET /churches/?skip=0&limit=100
Authorization: Bearer {token}
```

### 교회 상세 조회
```http
GET /churches/{church_id}
Authorization: Bearer {token}
```

**응답**:
```json
{
  "id": 1,
  "name": "성광교회",
  "address": "서울시 강남구 논현동 123-45",
  "phone": "02-1234-5678",
  "email": "info@sungkwang.church",
  "pastor_name": "홍길동",
  "founding_date": "1985-03-15",
  "website": "https://sungkwang.church",
  "subscription_status": "active",
  "subscription_plan": "premium",
  "subscription_expires_at": "2024-12-31T23:59:59Z",
  "member_count": 350,
  "max_members": 500,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 교회 생성 (슈퍼관리자만)
```http
POST /churches/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "새교회",
  "address": "서울시 강북구",
  "phone": "02-9876-5432",
  "email": "new@church.com",
  "pastor_name": "김목사",
  "founding_date": "2024-01-01"
}
```

### 교회 정보 수정
```http
PUT /churches/{church_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "수정된 교회명",
  "address": "새로운 주소",
  "phone": "02-1111-2222"
}
```

---

## 📋 주보 관리

교회 주보를 관리하는 엔드포인트입니다.

### 주보 목록 조회
```http
GET /bulletins/?skip=0&limit=100&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

**응답**:
```json
[
  {
    "id": 1,
    "church_id": 1,
    "title": "2024년 1월 첫째주 주보",
    "content": "주일예배 순서...",
    "bulletin_date": "2024-01-07",
    "file_url": "/static/bulletins/2024-01-07.pdf",
    "created_by": 1,
    "created_at": "2024-01-05T10:00:00Z",
    "updated_at": "2024-01-05T10:00:00Z"
  }
]
```

### 주보 생성
```http
POST /bulletins/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "2024년 1월 둘째주 주보",
  "content": "주일예배 순서\n1. 묵도\n2. 찬송...",
  "bulletin_date": "2024-01-14"
}
```

### 주보 파일 업로드
```http
POST /bulletins/{bulletin_id}/upload-file
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (PDF 파일)
```

### 주보 수정
```http
PUT /bulletins/{bulletin_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "수정된 제목",
  "content": "수정된 내용"
}
```

### 주보 삭제
```http
DELETE /bulletins/{bulletin_id}
Authorization: Bearer {token}
```

---

## 📢 공지사항 관리

교회 공지사항을 관리하는 엔드포인트입니다.

### 공지사항 목록 조회
```http
GET /announcements/?skip=0&limit=100&is_active=true
Authorization: Bearer {token}
```

**응답**:
```json
[
  {
    "id": 1,
    "church_id": 1,
    "title": "2024년 신년 감사예배 안내",
    "content": "2024년 1월 1일 오전 11시에 신년 감사예배가 있습니다.",
    "priority": "high",
    "is_active": true,
    "start_date": "2023-12-25",
    "end_date": "2024-01-01",
    "created_by": 1,
    "created_at": "2023-12-20T10:00:00Z",
    "updated_at": "2023-12-20T10:00:00Z",
    "views": 125
  }
]
```

### 공지사항 상세 조회
```http
GET /announcements/{announcement_id}
Authorization: Bearer {token}
```

### 공지사항 생성 (관리자만)
```http
POST /announcements/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "주일학교 교사 모집",
  "content": "2024년 주일학교 교사를 모집합니다. 관심있으신 분은...",
  "priority": "medium",
  "is_active": true,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**우선순위**: high (높음), medium (중간), low (낮음)

### 공지사항 수정 (관리자만)
```http
PUT /announcements/{announcement_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "수정된 제목",
  "content": "수정된 내용",
  "priority": "high"
}
```

### 공지사항 삭제 (관리자만)
```http
DELETE /announcements/{announcement_id}
Authorization: Bearer {token}
```

### 공지사항 조회수 증가
```http
POST /announcements/{announcement_id}/view
Authorization: Bearer {token}
```

---

## 📖 오늘의 말씀

매일 다른 성경 말씀을 제공하는 엔드포인트입니다.

### 랜덤 말씀 조회 (인증 불필요)
```http
GET /daily-verses/random
```

**응답**:
```json
{
  "id": 1,
  "verse": "여호와는 나의 목자시니 내게 부족함이 없으리로다",
  "reference": "시편 23:1",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 말씀 목록 조회 (관리자만)
```http
GET /daily-verses/?skip=0&limit=100
Authorization: Bearer {token}
```

**응답**:
```json
[
  {
    "id": 1,
    "verse": "여호와는 나의 목자시니 내게 부족함이 없으리로다",
    "reference": "시편 23:1",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "verse": "하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 이는 그를 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라",
    "reference": "요한복음 3:16",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 새 말씀 추가 (관리자만)
```http
POST /daily-verses/
Authorization: Bearer {token}
Content-Type: application/json

{
  "verse": "내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라",
  "reference": "빌립보서 4:13",
  "is_active": true
}
```

### 말씀 수정 (관리자만)
```http
PUT /daily-verses/{verse_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "verse": "수정된 말씀 내용",
  "reference": "수정된 출처",
  "is_active": false
}
```

### 말씀 삭제 (관리자만)
```http
DELETE /daily-verses/{verse_id}
Authorization: Bearer {token}
```

### 말씀 통계 조회 (관리자만)
```http
GET /daily-verses/stats
Authorization: Bearer {token}
```

**응답**:
```json
{
  "total_verses": 50,
  "active_verses": 45,
  "inactive_verses": 5
}
```

---

## 📚 참고 사항

### 공통 응답 코드
- `200`: 성공
- `201`: 생성 성공
- `400`: 잘못된 요청
- `401`: 인증 필요
- `403`: 권한 없음
- `404`: 리소스 없음
- `422`: 유효성 검사 실패
- `500`: 서버 오류

### 페이지네이션
대부분의 목록 API는 다음 매개변수를 지원합니다:
- `skip`: 건너뛸 항목 수 (기본값: 0)
- `limit`: 반환할 최대 항목 수 (기본값: 100)

### 날짜 형식
- 날짜: `YYYY-MM-DD` (예: `2024-01-15`)
- 날짜+시간: `YYYY-MM-DDTHH:MM:SSZ` (예: `2024-01-15T14:30:00Z`)

---

**문서 작성일**: 2024년 8월 1일  
**API 버전**: v1.0  
**문서 버전**: 1.0