# 공지사항 시스템 변경사항 안내

## 🔄 변경 개요

기존의 통합된 공지사항 시스템을 **시스템 공지사항**과 **교회별 공지사항**으로 분리했습니다.

### 변경 이유
- 시스템 관리자와 교회 관리자의 권한 분리
- 데이터 무결성 향상
- API 구조의 명확화
- 멀티 테넌트 지원 강화

---

## 📋 새로운 구조

### 1. 시스템 공지사항 (SystemAnnouncement)
- **목적**: 모든 교회에 표시되는 시스템 차원의 공지사항
- **관리자**: 시스템 관리자 (church_id = 0)만 관리 가능
- **테이블**: `system_announcements`
- **API 경로**: `/api/v1/system-announcements/`

### 2. 교회별 공지사항 (Announcement)
- **목적**: 특정 교회 내부의 공지사항
- **관리자**: 해당 교회의 관리자만 관리 가능
- **테이블**: `announcements` (기존)
- **API 경로**: `/api/v1/announcements/`

---

## 🔗 API 엔드포인트 변경사항

### 시스템 공지사항 API (새로 추가)

#### 1. 활성 시스템 공지사항 조회 (모든 사용자)
```http
GET /api/v1/system-announcements/
```

**응답 예시:**
```json
[
  {
    "id": 1,
    "title": "시스템 점검 안내",
    "content": "2025년 9월 5일 오전 2시-4시 시스템 점검이 있습니다.",
    "priority": "important",
    "start_date": "2025-09-01",
    "end_date": "2025-09-05",
    "target_churches": null,
    "is_active": true,
    "is_pinned": true,
    "created_by": 1,
    "author_name": "시스템관리자",
    "created_at": "2025-09-01T10:00:00Z",
    "updated_at": null
  }
]
```

#### 2. 시스템 공지사항 관리 (시스템 관리자만)
```http
GET /api/v1/system-announcements/admin
```

**응답 예시:**
```json
{
  "announcements": [...],
  "total": 25
}
```

#### 3. 시스템 공지사항 생성 (시스템 관리자만)
```http
POST /api/v1/system-announcements/
```

**요청 본문:**
```json
{
  "title": "새로운 기능 출시",
  "content": "AI 비서 기능이 업데이트되었습니다.",
  "priority": "normal",
  "start_date": "2025-09-01",
  "end_date": "2025-09-30",
  "target_churches": "[1,2,3]",
  "is_active": true,
  "is_pinned": false
}
```

#### 4. 시스템 공지사항 수정 (시스템 관리자만)
```http
PUT /api/v1/system-announcements/{id}
```

#### 5. 시스템 공지사항 삭제 (시스템 관리자만)
```http
DELETE /api/v1/system-announcements/{id}
```

#### 6. 시스템 공지사항 읽음 처리
```http
POST /api/v1/system-announcements/{id}/read
```

#### 7. 대상 교회 목록 조회 (시스템 관리자만)
```http
GET /api/v1/system-announcements/churches
```

### 교회별 공지사항 API (기존, 단순화)

#### 1. 활성 교회 공지사항 조회
```http
GET /api/v1/announcements/active
```
- 해당 교회의 공지사항만 조회
- 시스템 공지사항은 포함되지 않음

#### 2. 교회 공지사항 관리 (교회 관리자용)
```http
GET /api/v1/announcements/church-admin
```

**응답 구조 변경:**
```json
{
  "announcements": [...],
  "total": 10
}
```

---

## 🚨 중요한 변경사항

### 1. **기존 `/admin` 엔드포인트 변경**
```diff
- GET /api/v1/announcements/admin
+ GET /api/v1/announcements/church-admin
```

### 2. **응답 구조 변경**
기존의 배열 직접 반환에서 객체로 래핑:

**이전:**
```json
[...announcements]
```

**현재:**
```json
{
  "announcements": [...],
  "total": number
}
```

### 3. **권한 체크 변경**
- 시스템 공지사항: `church_id = 0`인 사용자만 관리 가능
- 교회 공지사항: `church_id = 해당 교회 ID`인 사용자만 관리 가능

### 4. **제거된 엔드포인트**
```diff
- GET /api/v1/announcements/churches
```
→ `GET /api/v1/system-announcements/churches`로 이동

---

## 💾 데이터베이스 변경사항

### 새로 추가된 테이블

#### `system_announcements`
```sql
- id: INTEGER (Primary Key)
- title: VARCHAR(255)
- content: TEXT
- priority: VARCHAR(50) - 'urgent', 'important', 'normal'
- start_date: DATE
- end_date: DATE (nullable)
- target_churches: TEXT (JSON string of church IDs)
- is_active: BOOLEAN
- is_pinned: BOOLEAN
- created_by: INTEGER (Foreign Key to users)
- author_name: VARCHAR
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### `system_announcement_reads`
```sql
- id: INTEGER (Primary Key)
- system_announcement_id: INTEGER (Foreign Key)
- user_id: INTEGER (Foreign Key)
- church_id: INTEGER (Foreign Key)
- read_at: TIMESTAMP
```

### 기존 테이블 복원
`announcements` 테이블이 원래 구조로 복원:
- `church_id`는 NULL 불허 (필수)
- 시스템 공지 관련 필드들 제거

---

## 🔐 인증 정보

### 시스템 관리자 계정
```
Username: system_superadmin
Password: admin123!
Church ID: 0
```

---

## 🛠 프론트엔드 구현 가이드

### 1. 공지사항 목록 페이지

**시스템 공지사항과 교회 공지사항을 분리해서 표시:**

```javascript
// 시스템 공지사항 조회
const fetchSystemAnnouncements = async () => {
  const response = await api.get('/system-announcements/');
  return response.data; // 배열 직접 반환
};

// 교회 공지사항 조회  
const fetchChurchAnnouncements = async () => {
  const response = await api.get('/announcements/active');
  return response.data; // 배열 직접 반환
};
```

### 2. 관리자 페이지

**시스템 관리자와 교회 관리자 구분:**

```javascript
const isSystemAdmin = user.church_id === 0;

if (isSystemAdmin) {
  // 시스템 공지사항 관리
  const response = await api.get('/system-announcements/admin');
  const { announcements, total } = response.data;
} else {
  // 교회 공지사항 관리
  const response = await api.get('/announcements/church-admin');
  const { announcements, total } = response.data;
}
```

### 3. 공지사항 생성/수정

**시스템 공지사항:**
```javascript
const createSystemAnnouncement = async (data) => {
  return await api.post('/system-announcements/', {
    title: data.title,
    content: data.content,
    priority: data.priority, // 'urgent', 'important', 'normal'
    start_date: data.start_date, // YYYY-MM-DD
    end_date: data.end_date,     // YYYY-MM-DD or null
    target_churches: JSON.stringify(data.target_church_ids), // "[1,2,3]" or null
    is_active: true,
    is_pinned: data.is_pinned || false
  });
};
```

**교회 공지사항:**
```javascript
const createChurchAnnouncement = async (data) => {
  return await api.post('/announcements/', {
    title: data.title,
    content: data.content,
    category: data.category,
    subcategory: data.subcategory,
    is_active: true,
    is_pinned: data.is_pinned || false,
    target_audience: data.target_audience || 'all'
  });
};
```

### 4. 읽음 처리

```javascript
// 시스템 공지사항 읽음 처리
const markSystemAnnouncementRead = async (id) => {
  return await api.post(`/system-announcements/${id}/read`);
};

// 교회 공지사항 읽음 처리 (현재 제거됨, 필요시 구현)
const markChurchAnnouncementRead = async (id) => {
  return await api.post(`/announcements/${id}/read`);
};
```

### 5. 대상 교회 선택 (시스템 관리자용)

```javascript
const fetchChurchesForTargeting = async () => {
  const response = await api.get('/system-announcements/churches');
  return response.data; // [{id, name, address, phone}, ...]
};
```

---

## 📱 UI/UX 권장사항

### 1. 공지사항 구분 표시
- 시스템 공지사항: 특별한 아이콘/색상으로 구분
- 우선순위 표시: urgent(빨강), important(주황), normal(기본)

### 2. 관리 화면 분리
- 시스템 관리자: 시스템 공지사항 탭만 표시
- 교회 관리자: 교회 공지사항 탭만 표시

### 3. 대상 교회 선택 UI
- 다중 선택 체크박스
- "전체 교회" 옵션

---

## 🐛 마이그레이션 필요

배포 후 다음 명령어 실행:
```bash
alembic upgrade head
```

---

## ❓ 문의사항

구현 중 문의사항이 있으시면 백엔드 팀에게 연락해주세요.

**주요 확인사항:**
1. 기존 공지사항 목록이 비어있는지 확인 (API 경로 변경으로 인해)
2. 관리자 권한이 올바르게 작동하는지 확인
3. 읽음 처리 기능이 필요한지 확인

---

*최종 업데이트: 2025-09-01*