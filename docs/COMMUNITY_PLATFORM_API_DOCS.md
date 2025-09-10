# 커뮤니티 플랫폼 API 문서 (프론트엔드 개발자용)

## 📋 개요

스마트요람 커뮤니티 플랫폼의 새로운 API 엔드포인트들이 구현되었습니다. 이 문서는 프론트엔드 개발자가 커뮤니티 기능을 구현할 때 필요한 모든 API 정보를 제공합니다.

### 🔗 Base URL
```
https://your-domain.com/api/v1/community
```

### 🔐 인증
모든 API는 JWT Bearer 토큰이 필요합니다:
```javascript
headers: {
  'Authorization': 'Bearer <your-jwt-token>',
  'Content-Type': 'application/json'
}
```

---

## 1. 🏠 커뮤니티 홈 API

### 1.1 커뮤니티 통계 조회
```http
GET /api/v1/community/stats
```

**응답 예시:**
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

### 1.2 최근 게시글 조회
```http
GET /api/v1/community/recent-posts?limit=10
```

**쿼리 파라미터:**
- `limit`: 조회할 게시글 수 (기본: 10)

**응답 예시:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "type": "free-sharing",
      "title": "냉장고 무료 나눔",
      "author_id": 456,
      "church_id": 9998,
      "created_at": "2024-01-15T14:30:00Z",
      "status": "available",
      "views": 45,
      "likes": 8
    }
  ]
}
```

### 1.3 내가 올린 글 목록
```http
GET /api/v1/community/my-posts
```

**쿼리 파라미터:**
- `post_type`: 게시글 타입 (free-sharing, item-request, job-post, job-seeker)
- `status`: 상태 필터
- `search`: 제목 검색
- `page`: 페이지 번호 (기본: 1)
- `limit`: 페이지당 항목 수 (기본: 20)

**응답 예시:**
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
      "church_id": 9998,
      "location": "서울시 강남구"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 87,
    "per_page": 20
  }
}
```

---

## 2. 🎁 무료 나눔 API

### 2.1 나눔 목록 조회
```http
GET /api/v1/community/sharing
```

**쿼리 파라미터:**
- `status`: available, reserved, completed
- `category`: 가전제품, 가구, 의류, 도서, 기타
- `location`: 지역 필터
- `search`: 제목/내용 검색
- `church_filter`: 특정 교회 필터 (선택사항)
- `page`: 페이지 번호
- `limit`: 페이지당 항목 수

**응답 예시:**
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
      "status": "available",
      "recipient_info": null,
      "expires_at": "2024-02-15T14:30:00Z",
      "author_id": 456,
      "church_id": 9998,
      "views": 45,
      "likes": 8,
      "created_at": "2024-01-15T14:30:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 87,
    "per_page": 20
  }
}
```

### 2.2 나눔 등록
```http
POST /api/v1/community/sharing
Content-Type: multipart/form-data
```

**요청 데이터 (FormData):**
```javascript
const formData = new FormData();
formData.append('title', '냉장고 무료 나눔');
formData.append('description', '이사가면서 냉장고를 나눔합니다');
formData.append('category', '가전제품');
formData.append('condition', '양호');
formData.append('location', '서울시 강남구');
formData.append('contact_method', 'phone');
formData.append('contact_info', '010-1234-5678');
formData.append('pickup_location', '강남역 근처');
formData.append('available_times', '평일 저녁, 주말 언제나');
formData.append('expires_at', '2024-02-15T14:30:00Z');

// 이미지 파일들 (최대 5개, 각각 10MB 이하)
for (let i = 0; i < imageFiles.length; i++) {
  formData.append('images', imageFiles[i]);
}
```

**응답:**
```json
{
  "success": true,
  "message": "나눔 게시글이 등록되었습니다.",
  "data": { /* 생성된 나눔 객체 */ }
}
```

### 2.3 나눔 상세 조회
```http
GET /api/v1/community/sharing/{sharing_id}
```

### 2.4 나눔 수정
```http
PUT /api/v1/community/sharing/{sharing_id}
Content-Type: application/json
```

**요청 데이터:**
```json
{
  "title": "수정된 제목",
  "description": "수정된 설명",
  "condition": "보통"
}
```

### 2.5 나눔 상태 변경
```http
PATCH /api/v1/community/sharing/{sharing_id}/status
```

**요청 데이터:**
```json
{
  "status": "reserved",
  "recipient_info": "김철수 (010-9876-5432)"
}
```

### 2.6 나눔 삭제
```http
DELETE /api/v1/community/sharing/{sharing_id}
```

---

## 3. 🛒 물품 요청 API

### 3.1 요청 목록 조회
```http
GET /api/v1/community/requests
```

**쿼리 파라미터:**
- `status`: active, fulfilled, cancelled
- `category`: 가전제품, 가구, 의류, 도서, 기타
- `urgency_level`: 낮음, 보통, 높음
- `location`: 지역 필터
- `search`: 제목/내용 검색
- `church_filter`: 특정 교회 필터
- `page`, `limit`: 페이징

**응답 구조는 나눔과 유사하되 추가 필드:**
```json
{
  "urgency_level": "높음",
  "needed_by": "2024-02-01T00:00:00Z",
  "request_reason": "신혼집 꾸미기",
  "provider_info": null
}
```

### 3.2 요청 등록
```http
POST /api/v1/community/requests
Content-Type: multipart/form-data
```

**요청 데이터 (FormData):**
```javascript
const formData = new FormData();
formData.append('title', '냉장고 구합니다');
formData.append('description', '신혼집에서 사용할 냉장고를 찾고 있습니다');
formData.append('category', '가전제품');
formData.append('urgency_level', '높음');
formData.append('needed_by', '2024-02-01T00:00:00Z');
formData.append('request_reason', '신혼집 꾸미기');
formData.append('location', '서울시 강남구');
formData.append('contact_method', 'phone');
formData.append('contact_info', '010-1234-5678');
```

### 3.3 기타 요청 API
- `GET /requests/{id}` - 상세 조회
- `PUT /requests/{id}` - 수정
- `PATCH /requests/{id}/status` - 상태 변경
- `DELETE /requests/{id}` - 삭제

---

## 4. 💼 구인/구직 API

### 4.1 구인 공고 목록
```http
GET /api/v1/community/job-posts
```

**쿼리 파라미터:**
- `status`: open, closed, filled
- `employment_type`: full_time, part_time, contract, freelance, internship
- `location`: 지역 필터
- `search`: 제목/회사명/직책 검색

**응답 예시:**
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
      "description": "커피에 관심 있는 분을 모집합니다",
      "requirements": "커피에 대한 관심",
      "benefits": "식사 제공, 커피 교육",
      "contact_method": "email",
      "contact_info": "hr@coffee.com",
      "deadline": "2024-02-15T23:59:59Z",
      "status": "open",
      "author_id": 456,
      "church_id": 9998,
      "views": 25,
      "likes": 5,
      "created_at": "2024-01-15T14:30:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

### 4.2 구인 공고 등록
```http
POST /api/v1/community/job-posts
Content-Type: multipart/form-data
```

**요청 데이터 (FormData):**
```javascript
const formData = new FormData();
formData.append('title', '카페 아르바이트 모집');
formData.append('company', '커피숍 은혜');
formData.append('position', '바리스타');
formData.append('employment_type', 'part_time');
formData.append('location', '서울시 강남구');
formData.append('salary', '시급 10,000원');
formData.append('work_hours', '주 20시간');
formData.append('description', '커피에 관심 있는 분을 모집합니다');
formData.append('requirements', '커피에 대한 관심');
formData.append('benefits', '식사 제공, 커피 교육');
formData.append('contact_method', 'email');
formData.append('contact_info', 'hr@coffee.com');
formData.append('deadline', '2024-02-15T23:59:59Z');
```

### 4.3 구직 신청 목록
```http
GET /api/v1/community/job-seekers
```

**응답 예시:**
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
      "available_from": "2024-02-01T00:00:00Z",
      "status": "active"
    }
  ]
}
```

### 4.4 기타 구인/구직 API
- `GET /job-posts/{id}` - 구인 공고 상세
- `PUT /job-posts/{id}` - 구인 공고 수정
- `DELETE /job-posts/{id}` - 구인 공고 삭제
- `POST /job-seekers` - 구직 신청 등록
- `GET /job-seekers/{id}` - 구직 신청 상세
- `DELETE /job-seekers/{id}` - 구직 신청 삭제

---

## 5. 📝 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": { /* 응답 데이터 */ },
  "message": "성공 메시지 (선택사항)"
}
```

### 에러 응답
```json
{
  "success": false,
  "detail": "에러 메시지"
}
```

### 페이지네이션
모든 목록 API는 다음과 같은 페이지네이션을 포함합니다:
```json
{
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_count": 87,
    "per_page": 20
  }
}
```

---

## 6. 🔧 프론트엔드 구현 가이드

### 6.1 파일 업로드 처리
```javascript
// 이미지 업로드가 있는 API 호출 예시
const uploadSharing = async (formData) => {
  try {
    const response = await fetch('/api/v1/community/sharing', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Content-Type을 설정하지 마세요 (FormData가 자동으로 설정)
      },
      body: formData
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

### 6.2 필터링 및 검색
```javascript
// 쿼리 파라미터가 있는 API 호출
const fetchSharingList = async (filters) => {
  const params = new URLSearchParams();
  
  if (filters.status) params.append('status', filters.status);
  if (filters.category) params.append('category', filters.category);
  if (filters.location) params.append('location', filters.location);
  if (filters.search) params.append('search', filters.search);
  if (filters.page) params.append('page', filters.page);
  if (filters.limit) params.append('limit', filters.limit);
  
  const response = await fetch(`/api/v1/community/sharing?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  return response.json();
};
```

### 6.3 상태 관리 (React 예시)
```javascript
// 커뮤니티 상태 관리 Hook 예시
const useCommunityStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/v1/community/stats', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        const result = await response.json();
        if (result.success) {
          setStats(result.data);
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);
  
  return { stats, loading };
};
```

---

## 7. 📊 데이터 타입 정의 (TypeScript)

```typescript
// 기본 타입들
interface CommunitySharing {
  id: number;
  title: string;
  description: string;
  category: string;
  condition?: string;
  images?: string[];
  location: string;
  contact_method: string;
  contact_info: string;
  pickup_location?: string;
  available_times?: string;
  status: 'available' | 'reserved' | 'completed';
  recipient_info?: string;
  expires_at?: string;
  author_id: number;
  church_id?: number;
  views: number;
  likes: number;
  created_at: string;
  updated_at: string;
}

interface CommunityRequest {
  id: number;
  title: string;
  description: string;
  category: string;
  urgency_level: '낮음' | '보통' | '높음';
  needed_by?: string;
  request_reason?: string;
  images?: string[];
  location: string;
  contact_method: string;
  contact_info: string;
  status: 'active' | 'fulfilled' | 'cancelled';
  provider_info?: string;
  author_id: number;
  church_id?: number;
  views: number;
  likes: number;
  created_at: string;
  updated_at: string;
}

interface JobPost {
  id: number;
  title: string;
  company: string;
  position: string;
  employment_type: 'full_time' | 'part_time' | 'contract' | 'freelance' | 'internship';
  location: string;
  salary?: string;
  work_hours?: string;
  description: string;
  requirements?: string;
  benefits?: string;
  contact_method: string;
  contact_info: string;
  deadline?: string;
  status: 'open' | 'closed' | 'filled';
  author_id: number;
  church_id?: number;
  views: number;
  likes: number;
  created_at: string;
  updated_at: string;
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  detail?: string;
}

interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_count: number;
    per_page: number;
  };
}
```

---

## 8. 🚨 주의사항

### 8.1 파일 업로드 제한
- **최대 파일 크기**: 10MB per file
- **최대 파일 개수**: 5개
- **허용 확장자**: jpg, jpeg, png, pdf, doc, docx

### 8.2 권한 체계
- **작성자**: 본인이 작성한 게시글만 수정/삭제 가능
- **슈퍼어드민**: 모든 게시글 강제 삭제 가능
- **교차 교회 접근**: 모든 교회 사용자가 커뮤니티 기능 이용 가능

### 8.3 데이터 검증
- 필수 필드는 반드시 포함해야 함
- 이메일, 전화번호 형식 검증 필요
- XSS 방지를 위한 입력값 sanitization 권장

---

## 9. 📞 문의 및 지원

개발 중 문제가 발생하거나 추가 기능이 필요한 경우 백엔드 개발팀에 문의해주세요.

**API 테스트 도구**: Postman, Insomnia 등을 활용하여 API를 테스트해보세요.

---

*이 문서는 커뮤니티 플랫폼 API v1.0 기준으로 작성되었습니다.*