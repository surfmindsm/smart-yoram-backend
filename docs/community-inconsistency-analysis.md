# 커뮤니티 API 불일치 분석 및 통일화 방안

## 📋 현재 상황 요약

커뮤니티 관련 8개 테이블이 각각 다른 명명 규칙과 컬럼 구조를 사용하고 있어 my-posts API 등에서 복잡한 처리가 필요한 상황입니다.

## 🔍 발견된 주요 불일치 사항

### 1. **테이블명 불일치**

| 현재 테이블명 | 사용 패턴 | 문제점 |
|--------------|-----------|--------|
| `community_sharing` | community_ 접두사 | ✅ 일관성 있음 |
| `community_requests` | community_ 접두사 | ✅ 일관성 있음 |
| `job_posts` | 접두사 없음 | ❌ 패턴 불일치 |
| `job_seekers` | 접두사 없음 | ❌ 패턴 불일치 |
| `community_music_teams` | community_ 접두사 | ✅ 일관성 있음 |
| `music_team_seekers` | 접두사 없음 | ❌ 패턴 불일치 |
| `church_news` | church_ 접두사 | ❌ 패턴 불일치 |
| `church_events` | church_ 접두사 | ❌ 패턴 불일치 |

### 2. **컬럼명 불일치**

#### 작성자 참조 필드
- **author_id**: `music_team_recruitment`, `music_team_seeker`, `church_news`, `church_events` 
- **user_id**: `community_sharing`, `community_request`, `job_posts`
- **중복 존재**: 일부 테이블에서 `author_id`와 `user_id` 둘 다 정의됨

#### 조회수 필드  
- **view_count**: `job_posts`, `job_seekers`, `church_news`
- **views**: `community_music_teams`, `music_team_seekers`, `church_events`
- **중복 존재**: `community_sharing`, `community_requests`에서 둘 다 정의됨

#### 상태(Status) 필드 ENUM 타입
```sql
-- 각각 다른 ENUM 타입 사용
SharingStatus: 'available', 'reserved', 'completed'
RequestStatus: 'active', 'fulfilled', 'cancelled'  
JobStatus: 'active', 'closed', 'filled' (job_posts.py)
JobStatus: 'open', 'closed', 'filled' (job_post.py - 중복 파일)
RecruitmentStatus: 'open', 'closed', 'completed'
NewsStatus: 'active', 'completed', 'cancelled'
EventStatus: 'upcoming', 'ongoing', 'completed', 'cancelled'
```

### 3. **중복 모델 파일**
- `job_posts.py` vs `job_post.py` (같은 테이블을 다르게 정의)
- `church_events.py` vs `church_event.py` (같은 테이블을 다르게 정의)
- `music_team_recruitment.py`와 `music_team.py` (유사한 기능 중복)

## 🛠️ 통일화 방안

### Phase 1: 중복 파일 제거
```bash
# 제거할 중복 파일들
rm app/models/job_post.py          # job_posts.py 사용
rm app/models/church_event.py      # church_events.py 사용
# music_team.py와 music_team_recruitment.py 통합 검토
```

### Phase 2: 컬럼명 표준화

#### 표준 작성자 참조
```python
# 모든 테이블에서 통일
author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
author = relationship("User", foreign_keys=[author_id])
```

#### 표준 조회수 필드
```python
# 모든 테이블에서 통일
view_count = Column(Integer, default=0, comment="조회수")
```

#### 표준 상태 필드
```python
# ENUM 대신 String 사용으로 통일
status = Column(String(20), default="active", index=True, comment="상태")
```

### Phase 3: 테이블명 표준화 (선택사항)

#### 옵션 A: community_ 접두사로 통일
```sql
job_posts → community_job_posts
job_seekers → community_job_seekers  
music_team_seekers → community_music_team_seekers
church_news → community_church_news
church_events → community_church_events
```

#### 옵션 B: 현재 상태 유지 (권장)
- 테이블명 변경시 DB 마이그레이션 복잡도가 높음
- 현재 my-posts API가 모든 테이블을 정상 조회하므로 문제없음

## 🚀 my-posts API 개선 사항

### 현재 코드 (복잡함)
```python
# 각 테이블마다 다른 컬럼명 때문에 복잡한 처리 필요
"views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
```

### 통일화 후 코드 (간단함)
```python
# 모든 테이블이 동일한 컬럼명 사용시
"views": post.view_count,
"author_name": post.author.full_name if post.author else "익명",
```

## 📊 현재 상태별 처리 방법

### 1. **즉시 수정 가능한 항목**

#### A. 중복 컬럼 정리
```sql
-- community_sharing 테이블
-- author_id만 사용하고 user_id 제거
ALTER TABLE community_sharing DROP COLUMN user_id;

-- community_requests 테이블  
-- author_id만 사용하고 user_id 제거
ALTER TABLE community_requests DROP COLUMN user_id;
```

#### B. 누락된 컬럼 추가
```sql
-- job_posts, job_seekers 테이블에 author_id 추가 (user_id 대신)
ALTER TABLE job_posts ADD COLUMN author_id INTEGER REFERENCES users(id);
ALTER TABLE job_seekers ADD COLUMN author_id INTEGER REFERENCES users(id);

-- 기존 user_id 데이터를 author_id로 복사 후 user_id 제거
UPDATE job_posts SET author_id = user_id;
UPDATE job_seekers SET author_id = user_id;
ALTER TABLE job_posts DROP COLUMN user_id;
ALTER TABLE job_seekers DROP COLUMN user_id;
```

#### C. 조회수 컬럼 표준화
```sql
-- views만 있는 테이블에 view_count 추가
ALTER TABLE community_music_teams ADD COLUMN view_count INTEGER DEFAULT 0;
ALTER TABLE music_team_seekers ADD COLUMN view_count INTEGER DEFAULT 0; 
ALTER TABLE church_events ADD COLUMN view_count INTEGER DEFAULT 0;

-- 기존 views 데이터를 view_count로 복사
UPDATE community_music_teams SET view_count = views;
UPDATE music_team_seekers SET view_count = views;
UPDATE church_events SET view_count = views;

-- 기존 views 컬럼 제거
ALTER TABLE community_music_teams DROP COLUMN views;
ALTER TABLE music_team_seekers DROP COLUMN views;
ALTER TABLE church_events DROP COLUMN views;
```

### 2. **단계적 수정이 필요한 항목**

#### A. 상태 ENUM 타입 통일
```python
# 모든 모델에서 String 타입 사용
# PostgreSQL ENUM → String 마이그레이션 필요
status = Column(String(20), default="active", index=True, comment="상태")
```

## 🔧 마이그레이션 SQL 스크립트

```sql
-- 1단계: 중복 컬럼 정리 및 표준화
BEGIN;

-- community_sharing, community_requests 테이블 정리
ALTER TABLE community_sharing DROP COLUMN IF EXISTS user_id;
ALTER TABLE community_requests DROP COLUMN IF EXISTS user_id;

-- job_posts, job_seekers 테이블 정리  
ALTER TABLE job_posts ADD COLUMN IF NOT EXISTS author_id INTEGER;
ALTER TABLE job_seekers ADD COLUMN IF NOT EXISTS author_id INTEGER;

UPDATE job_posts SET author_id = user_id WHERE author_id IS NULL;
UPDATE job_seekers SET author_id = user_id WHERE author_id IS NULL;

ALTER TABLE job_posts DROP COLUMN IF EXISTS user_id;
ALTER TABLE job_seekers DROP COLUMN IF EXISTS user_id;

-- 조회수 컬럼 표준화
ALTER TABLE community_music_teams ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;
ALTER TABLE music_team_seekers ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;
ALTER TABLE church_events ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;

UPDATE community_music_teams SET view_count = COALESCE(views, 0) WHERE view_count = 0;
UPDATE music_team_seekers SET view_count = COALESCE(views, 0) WHERE view_count = 0;
UPDATE church_events SET view_count = COALESCE(views, 0) WHERE view_count = 0;

ALTER TABLE community_music_teams DROP COLUMN IF EXISTS views;
ALTER TABLE music_team_seekers DROP COLUMN IF EXISTS views;
ALTER TABLE church_events DROP COLUMN IF EXISTS views;

COMMIT;
```

## 📈 기대 효과

### 1. **my-posts API 단순화**
- `getattr()` 처리 제거로 코드 가독성 향상
- 유지보수성 증대

### 2. **새로운 커뮤니티 기능 추가 용이성**
- 표준화된 스키마로 일관된 API 개발 가능
- 공통 base 모델 사용으로 개발 속도 향상

### 3. **데이터 무결성 향상**
- 중복 컬럼 제거로 데이터 일관성 확보
- 외래키 관계 명확화

## ⚠️ 주의사항

### 1. **마이그레이션 전 백업 필수**
```sql
-- 백업 생성
CREATE TABLE community_sharing_backup AS SELECT * FROM community_sharing;
CREATE TABLE community_requests_backup AS SELECT * FROM community_requests;
-- ... (모든 테이블 백업)
```

### 2. **단계적 적용**
- 테스트 환경에서 먼저 검증
- 프로덕션 환경에서는 점진적 적용

### 3. **API 버전 관리**
- 기존 API 호환성 유지
- 필요시 API 버전 분리 고려

---

**작성일**: 2025-09-13  
**우선순위**: High  
**예상 작업 시간**: 2-3일  
**리스크 레벨**: Medium (백업 및 테스트 환경 검증 필수)