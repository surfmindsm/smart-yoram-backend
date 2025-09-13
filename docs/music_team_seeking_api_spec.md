# 행사팀 지원(Music Team Seeking) API 스펙 문서

## 개요

교회 행사팀(연주팀, 찬양팀 등) 지원 시스템을 위한 백엔드 API 스펙입니다.  
개인 연주자나 팀이 교회 행사에 지원할 수 있는 시스템을 구현합니다.

## 인증 시스템

### JWT 기반 인증
- 모든 API 요청 시 JWT 토큰에서 **자동으로 사용자 정보 추출**
- `author_name`: JWT에서 추출한 사용자 이름 (프론트엔드에서 입력받지 않음)
- `author_id`: JWT에서 추출한 사용자 ID
- `church_id`: JWT에서 추출한 소속 교회 ID (있는 경우)

**중요**: 작성자 정보는 프론트엔드에서 전송하지 않고, 백엔드에서 JWT 토큰을 통해 자동 설정됩니다.

---

## 데이터베이스 스키마

### `music_team_seekers` 테이블

```sql
CREATE TABLE music_team_seekers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,                    -- 지원서 제목
    team_name VARCHAR(100),                         -- 현재 활동 팀명 (선택사항)
    instrument VARCHAR(50) NOT NULL,                -- 팀 형태 (단일 선택)
    experience TEXT,                                -- 연주 경력
    portfolio VARCHAR(500),                         -- 포트폴리오 링크
    preferred_location TEXT[],                      -- 활동 가능 지역 (배열)
    available_days TEXT[],                          -- 활동 가능 요일 (배열)
    available_time VARCHAR(100),                    -- 활동 가능 시간대
    contact_phone VARCHAR(20) NOT NULL,             -- 연락처 (필수)
    contact_email VARCHAR(100),                     -- 이메일 (선택)
    status VARCHAR(20) DEFAULT 'available',         -- 상태 (available, interviewing, inactive)
    
    -- JWT에서 자동 추출되는 필드들
    author_id INTEGER NOT NULL,                     -- 작성자 ID (JWT에서 추출)
    author_name VARCHAR(100) NOT NULL,              -- 작성자 이름 (JWT에서 추출)
    church_id INTEGER,                              -- 소속 교회 ID (JWT에서 추출, 없으면 NULL)
    church_name VARCHAR(100),                       -- 소속 교회명 (JWT에서 추출, 없으면 NULL)
    
    -- 시스템 필드
    views INTEGER DEFAULT 0,                        -- 조회수
    likes INTEGER DEFAULT 0,                        -- 좋아요 수
    matches INTEGER DEFAULT 0,                      -- 매칭 건수
    applications INTEGER DEFAULT 0,                 -- 지원 건수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 수정일시
);
```

### 인덱스

```sql
-- 검색 성능을 위한 인덱스
CREATE INDEX idx_music_seekers_status ON music_team_seekers(status);
CREATE INDEX idx_music_seekers_instrument ON music_team_seekers(instrument);
CREATE INDEX idx_music_seekers_church ON music_team_seekers(church_id);
CREATE INDEX idx_music_seekers_location ON music_team_seekers USING GIN(preferred_location);
CREATE INDEX idx_music_seekers_days ON music_team_seekers USING GIN(available_days);
CREATE INDEX idx_music_seekers_created ON music_team_seekers(created_at DESC);
```

---

## API 엔드포인트

### 1. 지원서 목록 조회

```http
GET /api/v1/music-team-seekers
```

**Query Parameters:**
- `page` (int): 페이지 번호 (기본값: 1)
- `limit` (int): 페이지당 항목 수 (기본값: 20, 최대: 100)
- `status` (string): 상태 필터 (`available`, `interviewing`, `inactive`)
- `instrument` (string): 팀 형태 필터
- `location` (string): 지역 필터 (부분 매칭)
- `day` (string): 요일 필터 (`월요일`, `화요일`, ...)
- `time` (string): 시간대 필터
- `search` (string): 제목/경력 검색

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "피아노 반주 가능한 연주자입니다",
        "team_name": "은혜 찬양팀",
        "instrument": "찬양팀",
        "experience": "15년 경력의 피아노 반주자입니다...",
        "portfolio": "https://youtube.com/watch?v=...",
        "preferred_location": ["서울", "경기도"],
        "available_days": ["일요일", "수요일"],
        "available_time": "오전 (9:00-12:00)",
        "contact_phone": "010-1234-5678",
        "contact_email": "musician@email.com",
        "status": "available",
        "author_id": 123,
        "author_name": "김연주",
        "church_id": 456,
        "church_name": "새생명교회",
        "views": 42,
        "likes": 5,
        "matches": 3,
        "applications": 7,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

### 2. 지원서 상세 조회

```http
GET /api/v1/music-team-seekers/{id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "피아노 반주 가능한 연주자입니다",
    "team_name": "은혜 찬양팀",
    "instrument": "찬양팀",
    "experience": "15년 경력의 피아노 반주자입니다...",
    "portfolio": "https://youtube.com/watch?v=...",
    "preferred_location": ["서울", "경기도"],
    "available_days": ["일요일", "수요일"],
    "available_time": "오전 (9:00-12:00)",
    "contact_phone": "010-1234-5678",
    "contact_email": "musician@email.com",
    "status": "available",
    "author_id": 123,
    "author_name": "김연주",
    "church_id": 456,
    "church_name": "새생명교회",
    "views": 43,
    "likes": 5,
    "matches": 3,
    "applications": 7,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**참고**: 조회 시 `views` 카운트 자동 증가

### 3. 지원서 등록

```http
POST /api/v1/music-team-seekers
```

**Headers:**
- `Authorization: Bearer {JWT_TOKEN}` (필수)
- `Content-Type: application/json`

**Request Body:**
```json
{
  "title": "피아노 반주 가능한 연주자입니다",
  "team_name": "은혜 찬양팀",
  "instrument": "찬양팀",
  "experience": "15년 경력의 피아노 반주자입니다...",
  "portfolio": "https://youtube.com/watch?v=...",
  "preferred_location": ["서울", "경기도"],
  "available_days": ["일요일", "수요일"],
  "available_time": "오전 (9:00-12:00)",
  "contact_phone": "010-1234-5678",
  "contact_email": "musician@email.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "지원서가 성공적으로 등록되었습니다",
  "data": {
    "id": 1,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 4. 지원서 수정

```http
PUT /api/v1/music-team-seekers/{id}
```

**권한**: 작성자만 수정 가능 (`author_id` 검증)

**Request Body:** (등록과 동일한 구조)

### 5. 지원서 삭제

```http
DELETE /api/v1/music-team-seekers/{id}
```

**권한**: 작성자만 삭제 가능 (`author_id` 검증)

---

## 데이터 유효성 검증

### 필수 필드
- `title`: 최대 200자
- `instrument`: 아래 옵션 중 하나 필수
- `contact_phone`: 전화번호 형식 검증

### 팀 형태 옵션 (instrument)
```json
[
  "현재 솔로 활동",
  "찬양팀", 
  "워십팀", 
  "어쿠스틱 팀",
  "밴드", 
  "오케스트라", 
  "합창단", 
  "무용팀", 
  "기타"
]
```

### 요일 옵션 (available_days)
```json
["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
```

### 시간대 옵션 (available_time)
```json
[
  "오전 (9:00-12:00)",
  "오후 (13:00-18:00)", 
  "저녁 (18:00-21:00)",
  "야간 (21:00-23:00)",
  "상시 가능",
  "협의 후 결정"
]
```

### 상태 옵션 (status)
```json
["available", "interviewing", "inactive"]
```

---

## 에러 응답 형식

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력 데이터가 올바르지 않습니다",
    "details": {
      "title": "제목은 필수 항목입니다",
      "instrument": "유효한 팀 형태를 선택해주세요"
    }
  }
}
```

## 공통 에러 코드
- `VALIDATION_ERROR`: 입력 데이터 검증 실패
- `UNAUTHORIZED`: 인증 실패 (JWT 토큰 없음/만료)
- `FORBIDDEN`: 권한 없음 (타인의 게시물 수정/삭제 시도)
- `NOT_FOUND`: 리소스 없음
- `INTERNAL_ERROR`: 서버 내부 오류

---

## 특이사항

### 1. JWT 기반 자동 작성자 정보 설정
- 프론트엔드에서 작성자 이름을 입력받지 않음
- JWT 토큰에서 `author_name`, `author_id`, `church_id`, `church_name` 자동 추출
- 교회 소속이 없는 사용자의 경우 `church_id`, `church_name`은 `null`

### 2. 날짜 처리
- `created_at`, `updated_at`이 `null`인 경우 대비
- 프론트엔드에서 "등록일 없음" 텍스트로 표시

### 3. 배열 필드 처리
- `preferred_location`, `available_days`는 PostgreSQL의 TEXT 배열
- JSON 형태로 직렬화하여 API 응답

### 4. 검색 및 필터링
- 지역 검색: `preferred_location` 배열에서 부분 매칭
- 요일 필터: `available_days` 배열에 해당 요일 포함 여부
- 제목/경력 검색: `title`, `experience` 필드에서 부분 매칭

---

## 구현 우선순위

1. **Phase 1**: 기본 CRUD API 구현 (목록, 상세, 등록, 수정, 삭제)
2. **Phase 2**: 검색 및 필터링 기능 추가
3. **Phase 3**: 조회수, 좋아요, 매칭 기능 구현

---

## 참고사항

이 API 스펙은 기존 커뮤니티 시스템(`job_postings`, `free_sharing` 등)과 일관된 구조를 유지합니다.  
JWT 기반 인증 시스템과 snake_case → camelCase 변환 로직을 동일하게 적용해주세요.