# my-posts API 완전 구현 - 프론트엔드 연동 가이드

## 개요

기존에 빈 배열만 반환하던 `GET /api/v1/community/my-posts` API가 모든 커뮤니티 테이블에서 사용자의 글을 조회하도록 완전히 구현되었습니다.

## API 엔드포인트

```
GET /api/v1/community/my-posts
```

**중요**: 이 API는 인증이 필요합니다. Authorization 헤더에 유효한 JWT 토큰을 포함해야 합니다.

```javascript
// 올바른 API 호출 예시
const response = await fetch('/api/v1/community/my-posts', {
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  }
});
```

## 쿼리 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `post_type` | string | null | 게시글 타입 필터 (아래 타입 참고) |
| `status` | string | null | 상태 필터 |
| `search` | string | null | 제목 검색 |
| `page` | integer | 1 | 페이지 번호 |
| `limit` | integer | 20 | 페이지당 항목 수 (최대 100) |

## 조회되는 커뮤니티 테이블

| 순번 | 테이블명 | type | type_label | 설명 |
|------|----------|------|------------|------|
| 1 | community_sharing | `community-sharing` | 무료 나눔 | 무료 나눔 글 |
| 2 | community_request | `community-request` | 물품 요청 | 물품 요청 글 |
| 3 | job_posts | `job-posts` | 구인 공고 | 구인 공고 글 |
| 4 | job_seekers | `job-seekers` | 구직 신청 | 구직 신청 글 |
| 5 | music_team_recruitment | `music-team-recruitment` | 음악팀 모집 | 음악팀 모집 글 |
| 6 | music_team_seekers | `music-team-seekers` | 음악팀 참여 | 음악팀 참여 글 |
| 7 | church_news | `church-news` | 교회 소식 | 교회 소식 글 |
| 8 | church_events | `church-events` | 교회 행사 | 교회 행사 글 |

## 응답 형식

### 성공 응답

```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "type": "community-sharing",
      "type_label": "무료 나눔",
      "title": "아이 옷 나눔합니다",
      "status": "available",
      "created_at": "2025-09-13T15:30:00.000Z",
      "views": 45,
      "likes": 3
    },
    {
      "id": 456,
      "type": "church-news",
      "type_label": "교회 소식",
      "title": "추수감사절 행사 안내",
      "status": "active",
      "created_at": "2025-09-12T10:15:00.000Z",
      "views": 120,
      "likes": 8
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_count": 55,
    "per_page": 20,
    "has_next": true,
    "has_prev": false
  }
}
```

### 데이터 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | integer | 글 ID |
| `type` | string | 글 타입 (필터링용) |
| `type_label` | string | 한글 타입명 (UI 표시용) |
| `title` | string | 글 제목 |
| `status` | string | 글 상태 |
| `created_at` | string | 작성일시 (ISO 8601) |
| `views` | integer | 조회수 |
| `likes` | integer | 좋아요 수 |

## 필터링 예시

### 타입별 필터링
```javascript
// 무료 나눔 글만 조회
GET /api/v1/community/my-posts?post_type=community-sharing

// 교회 소식만 조회
GET /api/v1/community/my-posts?post_type=church-news
```

### 상태별 필터링
```javascript
// 활성 상태 글만 조회
GET /api/v1/community/my-posts?status=active

// 완료된 글만 조회
GET /api/v1/community/my-posts?status=completed
```

### 검색
```javascript
// 제목에 "나눔"이 포함된 글 검색
GET /api/v1/community/my-posts?search=나눔
```

### 복합 필터링
```javascript
// 무료 나눔 중 활성 상태인 글만 조회
GET /api/v1/community/my-posts?post_type=community-sharing&status=available

// 2페이지, 10개씩 조회
GET /api/v1/community/my-posts?page=2&limit=10
```

## 프론트엔드 구현 가이드

### 1. 타입별 아이콘/색상 매핑

```javascript
const typeConfig = {
  'community-sharing': {
    icon: '🎁',
    color: '#4CAF50',
    label: '무료 나눔'
  },
  'community-request': {
    icon: '🙏',
    color: '#FF9800',
    label: '물품 요청'
  },
  'job-posts': {
    icon: '💼',
    color: '#2196F3',
    label: '구인 공고'
  },
  'job-seekers': {
    icon: '🔍',
    color: '#9C27B0',
    label: '구직 신청'
  },
  'music-team-recruitment': {
    icon: '🎵',
    color: '#E91E63',
    label: '음악팀 모집'
  },
  'music-team-seekers': {
    icon: '🎤',
    color: '#673AB7',
    label: '음악팀 참여'
  },
  'church-news': {
    icon: '📢',
    color: '#795548',
    label: '교회 소식'
  },
  'church-events': {
    icon: '🎉',
    color: '#607D8B',
    label: '교회 행사'
  }
};
```

### 2. 필터 컴포넌트 구현

```javascript
const typeFilters = [
  { value: 'all', label: '전체' },
  { value: 'community-sharing', label: '무료 나눔' },
  { value: 'community-request', label: '물품 요청' },
  { value: 'job-posts', label: '구인 공고' },
  { value: 'job-seekers', label: '구직 신청' },
  { value: 'music-team-recruitment', label: '음악팀 모집' },
  { value: 'music-team-seekers', label: '음악팀 참여' },
  { value: 'church-news', label: '교회 소식' },
  { value: 'church-events', label: '교회 행사' }
];

const statusFilters = [
  { value: 'all', label: '전체' },
  { value: 'active', label: '활성' },
  { value: 'available', label: '나눔 가능' },
  { value: 'completed', label: '완료' },
  { value: 'cancelled', label: '취소' }
];
```

### 3. API 호출 함수

```javascript
const fetchMyPosts = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.post_type && filters.post_type !== 'all') {
    params.append('post_type', filters.post_type);
  }
  if (filters.status && filters.status !== 'all') {
    params.append('status', filters.status);
  }
  if (filters.search) {
    params.append('search', filters.search);
  }
  if (filters.page) {
    params.append('page', filters.page);
  }
  if (filters.limit) {
    params.append('limit', filters.limit);
  }

  const response = await fetch(`/api/v1/community/my-posts?${params}`);
  const data = await response.json();
  
  return data;
};
```

### 4. 게시글 클릭 처리

```javascript
const handlePostClick = (post) => {
  // 타입에 따라 다른 상세 페이지로 이동
  const routes = {
    'community-sharing': `/community/sharing/${post.id}`,
    'community-request': `/community/request/${post.id}`,
    'job-posts': `/community/job-posts/${post.id}`,
    'job-seekers': `/community/job-seekers/${post.id}`,
    'music-team-recruitment': `/community/music-team-recruitment/${post.id}`,
    'music-team-seekers': `/community/music-team-seekers/${post.id}`,
    'church-news': `/community/church-news/${post.id}`,
    'church-events': `/community/church-events/${post.id}`
  };
  
  router.push(routes[post.type] || '/community');
};
```

## 정렬 및 표시

- **정렬**: 최신순 (created_at 내림차순)
- **페이지네이션**: 기본 20개씩, 최대 100개까지 설정 가능
- **빈 데이터**: 글이 없을 경우 빈 배열 반환

## 오류 처리

API는 개별 테이블 조회 오류시에도 전체 API가 중단되지 않도록 구현되었습니다. 각 테이블별로 try-catch 처리되어 있어 일부 테이블에 문제가 있어도 나머지 데이터는 정상 조회됩니다.

## 테스트 방법

1. **유효한 JWT 토큰으로 로그인** (가장 중요!)
2. 각 커뮤니티 메뉴에서 글 1개씩 등록
3. "내가 쓴 글" 페이지에서 모든 글이 표시되는지 확인
4. 필터링 기능 테스트
5. 페이지네이션 테스트

## 현재 상태 및 문제 해결

✅ **백엔드 구현 완료**: 모든 8개 테이블을 조회하는 로직이 정상 구현됨  
❌ **프론트엔드 인증 문제**: JWT 토큰 오류로 인해 403 Forbidden 발생

### 인증 오류 해결 방법

만약 API 호출시 403 Forbidden 에러가 발생한다면:

1. **JWT 토큰 확인**: Authorization 헤더에 올바른 토큰이 포함되어 있는지 확인
2. **토큰 형식 확인**: `Bearer ${token}` 형식이 맞는지 확인
3. **토큰 만료 확인**: 토큰이 만료되었다면 재로그인 필요
4. **서버 로그 확인**: 백엔드 서버 로그에서 JWT 디코딩 오류 메시지 확인

### 디버깅용 로깅

API가 정상 호출되면 서버 로그에 다음과 같은 메시지가 출력됩니다:

```
🔍 [MY_POSTS] 사용자 {user_id}의 게시글 조회 시작
🔍 [MY_POSTS] 무료 나눔: 2개
🔍 [MY_POSTS] 물품 요청: 1개
🔍 [MY_POSTS] 구인 공고: 3개
...
🔍 [MY_POSTS] 최종 결과: 15개 중 15개 반환 (페이지 1/1)
```

## 로깅

백엔드에서 상세한 로깅을 제공하므로 문제 발생시 서버 로그를 확인하여 디버깅할 수 있습니다.

---
ㄹ
**구현 완료일**: 2025-09-
3  
**커밋**: `392ce7f - my-posts API 완전 구현 - 모든 커뮤니티 테이블 통합 조회`