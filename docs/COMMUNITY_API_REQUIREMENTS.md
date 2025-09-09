# 커뮤니티 플랫폼 API 요구사항

## 개요

교회 관리 시스템의 커뮤니티 플랫폼을 위한 백엔드 API 구현 요구사항입니다. 
이 시스템은 다음 사용자 유형을 지원합니다:
- 커뮤니티 사용자 (church_id: 9998) - 커뮤니티 기능만 접근
- 교회 관리자 (church_id: 1~9997) - 전체 교회 관리 기능 접근
- 수퍼어드민 (church_id: 0) - 전체 시스템 관리 및 커뮤니티 관리

## 인증 및 권한

### JWT 토큰 구조
```json
{
  "user": {
    "id": 1,
    "name": "사용자이름",
    "email": "user@example.com",
    "church_id": 9998,
    "role": "community_user"
  }
}
```

### 권한 체계
- `community_user`: 커뮤니티 게시글 작성/수정/삭제 (본인 글만)
- `church_admin`: 교회 관리 기능
- `super_admin`: 전체 시스템 관리 + 커뮤니티 모든 글 관리

## 1. 커뮤니티 가입 신청 API

### 1.1 가입 신청 등록
```
POST /api/community/applications
Content-Type: multipart/form-data
```

**요청 필드:**
```javascript
{
  // 기본 정보
  name: "홍길동",                    // 필수
  email: "hong@example.com",         // 필수, 유니크
  password: "password123",           // 필수, 8자 이상
  phone: "010-1234-5678",           // 필수
  birth_date: "1990-01-01",         // 필수, YYYY-MM-DD
  
  // 교회 정보
  church_name: "은혜교회",           // 필수
  church_location: "서울시 강남구",  // 필수
  position: "청년부 리더",          // 선택
  
  // 목적 및 기대 (배열로 전송)
  purposes: ["나눔", "구인구직"],     // 필수
  expectations: "커뮤니티 활동",      // 선택
  
  // 약관 동의
  agree_terms: true,                // 필수
  agree_privacy: true,              // 필수
  agree_marketing: false,           // 선택
  
  // 첨부파일 (선택)
  church_certificate: File,         // 교회 증명서 이미지
  
  // 추천인 (선택)
  referrer: "김목사"
}
```

**응답:**
```json
{
  "success": true,
  "message": "가입 신청이 완료되었습니다. 승인까지 1-2일 소요됩니다.",
  "application_id": 123
}
```

### 1.2 가입 신청 목록 조회 (관리자용)
```
GET /api/admin/community/applications
Authorization: Bearer <token>
```

**쿼리 파라미터:**
- `status`: pending, approved, rejected
- `page`: 페이지 번호 (기본: 1)
- `limit`: 페이지당 항목 수 (기본: 10)
- `search`: 이름/이메일 검색

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "홍길동",
      "email": "hong@example.com",
      "phone": "010-1234-5678",
      "birth_date": "1990-01-01",
      "church_name": "은혜교회",
      "church_location": "서울시 강남구",
      "position": "청년부 리더",
      "purposes": ["나눔", "구인구직"],
      "expectations": "커뮤니티 활동",
      "church_certificate": "https://storage.../certificate.jpg",
      "referrer": "김목사",
      "status": "pending",
      "applied_at": "2024-01-15T09:30:00Z",
      "processed_at": null,
      "processed_by": null,
      "rejection_reason": null
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 50,
    "per_page": 10
  }
}
```

### 1.3 가입 신청 승인/거부
```
POST /api/admin/community/applications/{id}/approve
POST /api/admin/community/applications/{id}/reject
Authorization: Bearer <token>
```

**요청 (거부시):**
```json
{
  "rejection_reason": "교회 정보 확인 불가"
}
```

**응답:**
```json
{
  "success": true,
  "message": "가입 신청이 승인되었습니다."
}
```

## 2. 커뮤니티 홈 API

### 2.1 홈 통계 조회
```
GET /api/community/stats
Authorization: Bearer <token>
```

**응답:**
```json
{
  "success": true,
  "data": {
    "total_posts": 1234,
    "active_sharing": 45,
    "active_requests": 23,
    "job_posts": 12,
    "music_teams": 8,
    "events_this_month": 15,
    "total_members": 450
  }
}
```

### 2.2 최근 게시글 조회
```
GET /api/community/recent-posts
Authorization: Bearer <token>
```

**쿼리 파라미터:**
- `limit`: 조회할 게시글 수 (기본: 10)

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "type": "free-sharing",
      "title": "냉장고 무료 나눔",
      "author": "홍길동",
      "church": "은혜교회",
      "created_at": "2024-01-15T14:30:00Z",
      "status": "available",
      "views": 45,
      "likes": 8
    }
  ]
}
```

## 3. 무료 나눔 API

### 3.1 나눔 목록 조회
```
GET /api/community/sharing
Authorization: Bearer <token>
```

**쿼리 파라미터:**
- `status`: available, reserved, completed
- `category`: 가전제품, 가구, 의류, 도서, 기타
- `location`: 지역 필터
- `search`: 제목/내용 검색
- `page`, `limit`

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "title": "냉장고 무료 나눔",
      "description": "이사가면서 냉장고를 나눔합니다",
      "category": "가전제품",
      "condition": "양호",
      "images": ["https://storage.../image1.jpg"],
      "location": "서울시 강남구",
      "contact_method": "phone",
      "contact_info": "010-1234-5678",
      "pickup_location": "강남역 근처",
      "available_times": "평일 저녁, 주말 언제나",
      "author": "홍길동",
      "church": "은혜교회",
      "status": "available",
      "created_at": "2024-01-15T14:30:00Z",
      "views": 45,
      "likes": 8,
      "expires_at": "2024-02-15T14:30:00Z"
    }
  ],
  "pagination": {...}
}
```

### 3.2 나눔 등록
```
POST /api/community/sharing
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**요청:**
```javascript
{
  title: "냉장고 무료 나눔",
  description: "이사가면서 냉장고를 나눔합니다",
  category: "가전제품",
  condition: "양호",
  images: [File, File, ...],  // 최대 5개
  location: "서울시 강남구",
  contact_method: "phone",
  contact_info: "010-1234-5678",
  pickup_location: "강남역 근처",
  available_times: "평일 저녁, 주말 언제나",
  expires_at: "2024-02-15T14:30:00Z"
}
```

### 3.3 나눔 상세 조회
```
GET /api/community/sharing/{id}
Authorization: Bearer <token>
```

### 3.4 나눔 수정
```
PUT /api/community/sharing/{id}
Authorization: Bearer <token>
```

### 3.5 나눔 삭제
```
DELETE /api/community/sharing/{id}
Authorization: Bearer <token>
```

### 3.6 나눔 상태 변경
```
PATCH /api/community/sharing/{id}/status
Authorization: Bearer <token>
```

**요청:**
```json
{
  "status": "reserved",
  "recipient_info": "김철수 (010-9876-5432)"
}
```

## 4. 물품 요청 API

### 4.1 요청 목록 조회
```
GET /api/community/requests
Authorization: Bearer <token>
```

**응답 구조는 나눔과 유사하되, 추가 필드:**
```json
{
  "urgency_level": "높음",
  "needed_by": "2024-02-01T00:00:00Z",
  "request_reason": "신혼집 꾸미기"
}
```

### 4.2-4.6 요청 등록/조회/수정/삭제/상태변경
(나눔 API와 동일한 패턴)

## 5. 나눔 제공 API

### 5.1-5.6 제공 관련 API
(나눔 API와 유사한 구조)

## 6. 구인 공고 API

### 6.1 구인 목록 조회
```
GET /api/community/job-posts
Authorization: Bearer <token>
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "title": "카페 아르바이트 모집",
      "company": "커피숍 은혜",
      "position": "바리스타",
      "employment_type": "part_time",
      "location": "서울시 강남구",
      "salary": "시급 10,000원",
      "work_hours": "주 20시간",
      "requirements": "커피에 대한 관심",
      "benefits": "식사 제공, 커피 교육",
      "contact_method": "email",
      "contact_info": "hr@coffee.com",
      "deadline": "2024-02-15T23:59:59Z",
      "status": "open"
    }
  ]
}
```

## 7. 구직 신청 API

### 7.1 구직 목록 조회
```
GET /api/community/job-seekers
Authorization: Bearer <token>
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "title": "마케팅 분야 구직합니다",
      "desired_position": "마케팅 담당자",
      "employment_type": "full_time",
      "desired_location": "서울시 전체",
      "desired_salary": "연봉 3000만원 이상",
      "experience": "마케팅 3년 경력",
      "skills": "디지털 마케팅, SNS 운영",
      "education": "대학교 졸업",
      "introduction": "성실하고 책임감 있는...",
      "contact_method": "email",
      "contact_info": "job@example.com",
      "available_from": "2024-02-01T00:00:00Z"
    }
  ]
}
```

## 8. 음악팀 모집 API

### 8.1 음악팀 모집 목록
```
GET /api/community/music-recruits
Authorization: Bearer <token>
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "title": "찬양팀 드러머 모집",
      "team_name": "은혜 찬양팀",
      "church": "은혜교회",
      "instruments_needed": ["드럼"],
      "team_type": "찬양팀",
      "experience_required": "중급",
      "practice_location": "교회 지하 1층",
      "practice_schedule": "주일 오후 2시",
      "commitment": "최소 6개월",
      "requirements": "기본적인 드럼 연주 가능",
      "benefits": "찬양 사역의 기쁨",
      "contact_method": "phone"
    }
  ]
}
```

## 9. 음악팀 참여 API

### 9.1 참여 신청 목록
(음악팀 모집과 유사한 구조)

## 10. 교회 행사 API

### 10.1 행사 목록 조회
```
GET /api/community/church-events
Authorization: Bearer <token>
```

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "title": "청년 수련회",
      "church": "은혜교회",
      "event_type": "수련회",
      "description": "2박 3일 청년 수련회",
      "start_date": "2024-03-15T00:00:00Z",
      "end_date": "2024-03-17T23:59:59Z",
      "location": "수양관",
      "address": "강원도 춘천시",
      "capacity": 50,
      "current_participants": 35,
      "fee": 100000,
      "registration_deadline": "2024-03-10T23:59:59Z",
      "contact_method": "phone",
      "contact_info": "010-1234-5678",
      "requirements": "청년부 소속",
      "includes": "숙박, 식사, 프로그램",
      "images": ["https://storage.../event1.jpg"]
    }
  ]
}
```

## 11. 내가 올린 글 API

### 11.1 내 게시글 목록 조회
```
GET /api/community/my-posts
Authorization: Bearer <token>
```

**쿼리 파라미터:**
- `type`: 게시글 타입 필터
- `status`: 상태 필터
- `search`: 제목 검색

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "type": "free-sharing",
      "title": "냉장고 무료 나눔",
      "status": "available",
      "created_at": "2024-01-15T14:30:00Z",
      "views": 45,
      "likes": 8,
      "comments": 3,
      "church": "은혜교회",
      "location": "서울시 강남구"
    }
  ]
}
```

## 12. 커뮤니티 관리 API (수퍼어드민 전용)

### 12.1 전체 게시글 조회
```
GET /api/admin/community/posts
Authorization: Bearer <token>
```

**권한:** church_id = 0 (수퍼어드민)만 접근 가능

**쿼리 파라미터:**
- `type`: 게시글 타입
- `status`: 상태
- `author`: 작성자 검색
- `church`: 교회명 검색
- `blocked`: true/false (차단된 글 포함)
- `page`, `limit`

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "type": "free-sharing",
      "title": "냉장고 무료 나눔",
      "author": "홍길동",
      "church": "은혜교회",
      "status": "available",
      "is_blocked": false,
      "created_at": "2024-01-15T14:30:00Z",
      "views": 45,
      "likes": 8,
      "reports_count": 0
    }
  ],
  "pagination": {...}
}
```

### 12.2 게시글 차단
```
POST /api/admin/community/{post_type}/{post_id}/block
Authorization: Bearer <token>
```

**요청:**
```json
{
  "reason": "부적절한 내용"
}
```

### 12.3 게시글 강제 삭제
```
DELETE /api/admin/community/{post_type}/{post_id}/force-delete
Authorization: Bearer <token>
```

**요청:**
```json
{
  "reason": "스팸 게시글"
}
```

## 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": {...},
  "message": "optional success message"
}
```

### 오류 응답
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력 데이터가 올바르지 않습니다",
    "details": {
      "email": ["이미 사용 중인 이메일입니다"],
      "password": ["비밀번호는 8자 이상이어야 합니다"]
    }
  }
}
```

### HTTP 상태 코드
- 200: 성공
- 201: 생성 성공
- 400: 잘못된 요청
- 401: 인증 실패
- 403: 권한 없음
- 404: 리소스 없음
- 413: 파일 크기 초과 (최대 5MB)
- 422: 유효성 검사 실패
- 500: 서버 오류

## 파일 업로드 요구사항

### 이미지 업로드
- 최대 파일 크기: 5MB
- 허용 형식: jpg, jpeg, png, gif, webp
- 최대 파일 수: 5개 (게시글당)
- 저장 경로: `/community/{post_type}/{post_id}/images/`

### 첨부파일
- 교회 증명서: 2MB 이하의 이미지 파일

## 데이터베이스 고려사항

1. **사용자 테이블**: church_id 필드로 사용자 타입 구분
2. **게시글 테이블**: 각 타입별 별도 테이블 또는 통합 테이블 + type 필드
3. **파일 테이블**: 게시글별 첨부 파일 관리
4. **신청 테이블**: 커뮤니티 가입 신청 관리
5. **차단 로그**: 관리자 액션 기록

## 보안 요구사항

1. **JWT 토큰**: 모든 API 요청에 Bearer 토큰 필요
2. **파일 업로드**: 파일 타입 검증, 바이러스 스캔
3. **데이터 검증**: 모든 입력 데이터 sanitization
4. **권한 체크**: church_id 기반 접근 권한 검증
5. **Rate Limiting**: API 호출 빈도 제한

## CORS 설정

개발 환경:
- `http://localhost:3000` 허용

프로덕션 환경:
- 실제 도메인만 허용