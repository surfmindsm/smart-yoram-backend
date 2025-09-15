# 프론트엔드 API 마이그레이션 가이드

> **작성일**: 2025-09-15  
> **목적**: 커뮤니티 API 스키마 통일화에 따른 프론트엔드 수정 사항 안내  
> **백엔드 변경사항**: [COMMUNITY_API_SCHEMA_UNIFICATION.md](./COMMUNITY_API_SCHEMA_UNIFICATION.md) 참조

---

## 🚨 **긴급 수정 필요 (1단계 - 1-2일)**

### 1. **필드명 변경 사항**

#### 1.1 조회수 필드 통일
```typescript
// ❌ 기존 사용
interface CommunityPost {
  views: number;  // 이전 필드명
}

// ✅ 변경 후
interface CommunityPost {
  view_count: number;  // 통일된 필드명
}

// 📍 영향받는 API들
- /community/sharing/* → "view_count" 사용
- /community/music-team-recruitments/* → "view_count" 사용  
- /community/church-events/* → "view_count" 사용
- /community/job-posts/* → "view_count" 사용
```

#### 1.2 작성자 필드 중복 제거
```typescript
// ❌ 기존 응답 (중복 필드)
interface ApiResponse {
  user_id: number;
  author_id: number;  // 중복!
  user_name: string;
  author_name: string;  // 중복!
}

// ✅ 변경 후 (중복 제거)
interface ApiResponse {
  author_id: number;     // 통일
  author_name: string;   // 통일
}

// 📍 수정 필요한 컴포넌트들
- 게시글 목록에서 작성자 표시
- 게시글 상세에서 작성자 정보  
- 내 게시글 목록
```

### 2. **페이지네이션 구조 통일**

```typescript
// ❌ 기존 (일부 API)
interface PaginationOld {
  current_page: number;
  total_pages: number;
  total_count: number;
  per_page: number;
  // has_next, has_prev 없음
}

// ✅ 변경 후 (모든 API 통일)
interface PaginationNew {
  current_page: number;
  total_pages: number;
  total_count: number;
  per_page: number;
  has_next: boolean;    // ← 새로 추가
  has_prev: boolean;    // ← 새로 추가
}

// 📍 영향받는 컴포넌트들
- 페이지네이션 컴포넌트
- 무한 스크롤 구현부
- 다음/이전 버튼 표시 로직
```

### 3. **응답 구조 표준화**

```typescript
// ❌ 기존 (API마다 다름)
interface ListResponseOld {
  data: any[];
  pagination: any;
}

// ✅ 변경 후 (모든 API 통일)
interface ListResponseNew {
  success: boolean;      // ← 새로 추가
  data: any[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_count: number;
    per_page: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

// 📍 수정 필요
- API 호출 결과 파싱 로직
- 에러 처리 로직 
- 로딩 상태 관리
```

---

## 🔶 **중요 수정 사항 (2단계 - 3-5일)**

### 4. **상태값 변경 사항**

#### 4.1 커뮤니티 공유/판매
```typescript
// ❌ 기존 상태값
type SharingStatusOld = "available" | "reserved" | "completed";

// ✅ 변경 후 (통일)
type CommunityStatusNew = "active" | "completed" | "cancelled" | "paused";

// 매핑 관계
const statusMapping = {
  "available": "active",
  "reserved": "active", 
  "completed": "completed"
};
```

#### 4.2 구인/구직 게시판
```typescript
// ❌ 기존 상태값 (불규칙)
type JobStatusOld = "open" | "active" | "closed" | "filled";

// ✅ 변경 후 (통일)
type CommunityStatusNew = "active" | "completed" | "cancelled" | "paused";

// 매핑 관계
const jobStatusMapping = {
  "open": "active",
  "active": "active",
  "closed": "completed",
  "filled": "completed"
};
```

#### 4.3 교회 행사
```typescript
// ❌ 기존 상태값
type EventStatusOld = "upcoming" | "ongoing" | "completed" | "cancelled";

// ✅ 변경 후 (통일)  
type CommunityStatusNew = "active" | "completed" | "cancelled" | "paused";
```

### 5. **연락처 정보 구조 변경**

```typescript
// ❌ 기존 (통합형)
interface ContactOld {
  contact_info: string;  // "전화: 010-1234-5678 | 이메일: test@test.com"
}

// ✅ 변경 후 (분리형 권장)
interface ContactNew {
  contact_phone: string;           // 필수
  contact_email?: string;          // 선택
  contact_method?: "phone" | "email" | "both";  // 선호 방법
  contact_info?: string;           // 하위호환용 (읽기전용)
}

// 📍 수정 필요한 폼들
- 게시글 등록/수정 폼
- 연락처 표시 컴포넌트
- 연락처 유효성 검사
```

### 6. **JSON 배열 처리 변경**

#### 6.1 음악팀 모집 - 악기 정보
```typescript
// ❌ 기존 (문자열로 받아서 파싱)
const handleInstruments = (response: any) => {
  const instruments = JSON.parse(response.instruments_needed);
  return instruments;
};

// ✅ 변경 후 (직접 배열로 받음)
interface MusicTeamResponse {
  instruments_needed: string[];  // 직접 배열
}

const handleInstruments = (response: MusicTeamResponse) => {
  return response.instruments_needed;  // 파싱 불필요
};
```

#### 6.2 이미지 배열
```typescript
// ❌ 기존 (일부 API에서 문자열 파싱 필요)
const images = typeof response.images === 'string' 
  ? JSON.parse(response.images) 
  : response.images;

// ✅ 변경 후 (모든 API 통일)
interface PostResponse {
  images: string[];  // 항상 배열
}
```

### 7. **필드 길이 제한 업데이트**

```typescript
// 폼 유효성 검사 업데이트
const validationRules = {
  title: {
    required: true,
    maxLength: 255,        // 통일됨
  },
  contact_info: {
    maxLength: 200,        // 통일됨
  },
  email: {
    maxLength: 255,        // 통일됨
  },
  phone: {
    maxLength: 20,         // 통일됨
  },
  location: {
    maxLength: 200,        // 통일됨
  }
};
```

---

## 🔸 **장기 개선 사항 (3단계 - 1-2주)**

### 8. **타입 정의 통합**

#### 8.1 공통 타입 생성
```typescript
// types/community-common.ts (새로 생성)
export interface CommunityBasePost {
  id: number;
  title: string;
  description?: string;
  status: CommunityStatus;
  author_id: number;
  author_name: string;
  church_id: number;
  view_count: number;
  likes: number;
  created_at: string;
  updated_at: string;
}

export type CommunityStatus = "active" | "completed" | "cancelled" | "paused";

export interface StandardPagination {
  current_page: number;
  total_pages: number;
  total_count: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface StandardListResponse<T> {
  success: boolean;
  data: T[];
  pagination: StandardPagination;
}
```

#### 8.2 개별 API 타입들
```typescript
// types/community-sharing.ts
export interface CommunitySharing extends CommunityBasePost {
  category: string;
  condition: string;
  price: number;
  is_free: boolean;
  location: string;
  contact_phone: string;
  contact_email?: string;
  images: string[];
}

// types/job-posts.ts  
export interface JobPost extends CommunityBasePost {
  company_name: string;
  job_type: string;
  employment_type: string;
  location: string;
  salary_range?: string;
  requirements?: string;
  contact_phone: string;
  contact_email?: string;
  application_deadline?: string;
}
```

### 9. **API 호출 함수 리팩터링**

```typescript
// api/community-common.ts (새로 생성)
export class CommunityAPI {
  static async getList<T>(
    endpoint: string, 
    params: { page?: number; limit?: number; search?: string } = {}
  ): Promise<StandardListResponse<T>> {
    const response = await fetch(`${endpoint}?${new URLSearchParams(params)}`);
    return response.json();
  }

  static async getDetail<T>(endpoint: string, id: number): Promise<T> {
    const response = await fetch(`${endpoint}/${id}`);
    const result = await response.json();
    return result.data;
  }

  static async create<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    return result.data;
  }
}
```

### 10. **컴포넌트 리팩터링**

```typescript
// components/CommunityPostCard.tsx (공통 컴포넌트)
interface CommunityPostCardProps {
  post: CommunityBasePost;
  type: 'sharing' | 'job' | 'music' | 'event';
  onView?: () => void;
  onLike?: () => void;
}

export const CommunityPostCard: React.FC<CommunityPostCardProps> = ({
  post,
  type,
  onView,
  onLike
}) => {
  return (
    <div className="post-card">
      <h3>{post.title}</h3>
      <p>작성자: {post.author_name}</p>
      <p>조회수: {post.view_count}</p>  {/* view_count 사용 */}
      <p>좋아요: {post.likes}</p>
      <span className={`status-${post.status}`}>
        {getStatusLabel(post.status)}
      </span>
    </div>
  );
};

// utils/status-helpers.ts (유틸리티)
export const getStatusLabel = (status: CommunityStatus): string => {
  const labels = {
    active: '활성',
    completed: '완료',
    cancelled: '취소',
    paused: '일시중지'
  };
  return labels[status] || '알수없음';
};
```

---

## 📋 **단계별 수정 체크리스트**

### 🔥 **1단계 (긴급 - 1-2일)**

#### 필드명 변경
- [ ] `views` → `view_count` 모든 컴포넌트에서 변경
- [ ] `user_id`, `user_name` → `author_id`, `author_name` 변경
- [ ] 게시글 목록 컴포넌트 수정
- [ ] 게시글 상세 컴포넌트 수정
- [ ] 내 게시글 목록 수정

#### 페이지네이션 구조 변경
- [ ] 페이지네이션 컴포넌트에 `has_next`, `has_prev` 지원 추가
- [ ] 무한스크롤에서 `has_next` 사용
- [ ] 다음/이전 버튼 로직 업데이트

#### 응답 구조 변경
- [ ] 모든 API 호출에서 `success` 필드 확인 로직 추가
- [ ] 에러 처리 로직 업데이트
- [ ] 로딩 상태 관리 개선

### 🔶 **2단계 (중요 - 3-5일)**

#### 상태값 변경
- [ ] 상태값 매핑 함수 생성 (`utils/status-mapping.ts`)
- [ ] 커뮤니티 공유/판매 상태 표시 업데이트
- [ ] 구인/구직 게시판 상태 표시 업데이트  
- [ ] 교회 행사 상태 표시 업데이트
- [ ] 필터/검색에서 상태값 업데이트

#### 연락처 정보 구조 변경
- [ ] 게시글 등록 폼에서 연락처 분리 입력
- [ ] 게시글 수정 폼 업데이트
- [ ] 연락처 표시 컴포넌트 업데이트
- [ ] 연락처 유효성 검사 로직 업데이트

#### JSON 배열 처리 개선
- [ ] 음악팀 모집에서 악기 정보 파싱 로직 제거
- [ ] 이미지 배열 파싱 로직 제거
- [ ] 태그 배열 파싱 로직 제거

#### 필드 길이 제한 업데이트
- [ ] 폼 유효성 검사 규칙 업데이트
- [ ] 입력 필드 maxLength 속성 업데이트
- [ ] 에러 메시지 업데이트

### 🔸 **3단계 (장기 - 1-2주)**

#### 타입 정의 통합
- [ ] `types/community-common.ts` 생성
- [ ] 개별 API 타입 파일들 생성
- [ ] 기존 타입 정의들을 새로운 구조로 마이그레이션

#### API 호출 함수 리팩터링
- [ ] `api/community-common.ts` 생성
- [ ] 공통 API 함수들 구현
- [ ] 개별 API 파일들을 공통 함수 사용하도록 수정

#### 컴포넌트 리팩터링
- [ ] 공통 게시글 카드 컴포넌트 생성
- [ ] 공통 페이지네이션 컴포넌트 생성
- [ ] 공통 상태 표시 컴포넌트 생성
- [ ] 유틸리티 함수들 생성

---

## 🔧 **개발 팁 및 주의사항**

### 1. **점진적 마이그레이션**
```typescript
// 하위호환을 위한 임시 어댑터 함수
const adaptOldResponse = (oldResponse: any): NewResponse => {
  return {
    ...oldResponse,
    view_count: oldResponse.views || oldResponse.view_count || 0,
    author_id: oldResponse.user_id || oldResponse.author_id,
    author_name: oldResponse.user_name || oldResponse.author_name,
  };
};
```

### 2. **환경별 API 엔드포인트 관리**
```typescript
// config/api.ts
const API_BASE = {
  development: 'http://localhost:8000',
  production: 'https://api.smartyoram.com'
};

export const COMMUNITY_ENDPOINTS = {
  sharing: '/community/sharing',
  requests: '/community/requests', 
  jobs: '/community/job-posts',
  music: '/community/music-team-recruitments',
  events: '/community/church-events'
};
```

### 3. **타입 안전성 확보**
```typescript
// API 응답 타입 가드
const isCommunityResponse = (data: any): data is CommunityBasePost => {
  return data && 
    typeof data.id === 'number' &&
    typeof data.title === 'string' &&
    typeof data.author_id === 'number';
};
```

### 4. **에러 처리 개선**
```typescript
// api/error-handler.ts
export const handleApiError = (error: any) => {
  if (error.response?.data?.success === false) {
    throw new Error(error.response.data.message || '알 수 없는 오류');
  }
  throw error;
};
```

---

## 📞 **백엔드 협업 체크포인트**

### 마이그레이션 전 확인사항
1. [ ] 백엔드 1단계 수정 완료 확인
2. [ ] 개발 서버에서 API 응답 구조 확인
3. [ ] 기존 데이터 호환성 확인

### 단계별 배포 계획
1. **1단계**: 백엔드 먼저 배포 → 프론트엔드 핫픽스
2. **2단계**: 백엔드 + 프론트엔드 동시 배포
3. **3단계**: 프론트엔드 먼저 배포 (하위호환 유지)

### 테스트 시나리오
- [ ] 각 커뮤니티 메뉴별 CRUD 동작 확인
- [ ] 페이지네이션 정상 동작 확인  
- [ ] 검색/필터 기능 정상 동작 확인
- [ ] 파일 업로드 기능 정상 동작 확인

---

> **🎯 권장 진행 순서**: 백엔드 1단계 완료 → 프론트엔드 1단계 → 백엔드 2단계 → 프론트엔드 2단계  
> **⏰ 총 예상 작업 시간**: 1-2주 (백엔드 작업과 병행)  
> **🔄 배포 방식**: 단계별 점진적 배포로 서비스 중단 최소화