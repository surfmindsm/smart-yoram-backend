# 데이터베이스 실제 구조 분석 결과

## 📊 SQL 분석 쿼리 실행 완료

**실행일**: 2025-09-13  
**대상 테이블**: 8개 커뮤니티 테이블

## 🔍 주요 발견사항

### 1. **작성자 필드 불일치 확인**

| 테이블명 | author_id | user_id | nullable |
|----------|-----------|---------|----------|
| `church_events` | ✅ | ❌ | NO |
| `church_news` | ✅ | ❌ | NO |
| `community_music_teams` | ✅ | ❌ | NO |
| `music_team_seekers` | ✅ | ❌ | NO |
| `community_requests` | ✅ | ✅ | YES |
| `community_sharing` | ✅ | ✅ | YES |
| `job_posts` | ✅ | ✅ | YES |
| `job_seekers` | ✅ | ✅ | YES |

**문제점**: 
- `community_requests`, `community_sharing`, `job_posts`, `job_seekers`에서 **author_id와 user_id 중복 존재**
- 이 4개 테이블에서 author_id가 nullable=YES로 설정됨

### 2. **조회수 필드 중복 확인**

| 테이블명 | view_count | views | 비고 |
|----------|------------|-------|------|
| `church_news` | ✅ | ❌ | view_count만 |
| `church_events` | ❌ | ✅ | views만 |
| `community_music_teams` | ❌ | ✅ | views만 |
| `music_team_seekers` | ❌ | ✅ | views만 |
| `community_requests` | ✅ | ✅ | **중복!** |
| `community_sharing` | ✅ | ✅ | **중복!** |
| `job_posts` | ✅ | ✅ | **중복!** |
| `job_seekers` | ✅ | ✅ | **중복!** |

**현재 my-posts API 문제**: 이 중복으로 인해 `getattr(post, 'view_count', 0) or getattr(post, 'views', 0)` 처리 필요

### 3. **상태 필드 타입 분석**

| 테이블명 | 데이터 타입 | ENUM 타입 | 기본값 |
|----------|-------------|-----------|--------|
| `church_news` | USER-DEFINED | newsstatus | 'active' |
| `church_events` | character varying | - | 'upcoming' |
| `community_music_teams` | character varying | - | - |
| `community_requests` | character varying | - | 'open' |
| `community_sharing` | character varying | - | 'available' |
| `job_posts` | character varying | - | 'active' |
| `job_seekers` | character varying | - | 'active' |
| `music_team_seekers` | character varying | - | 'available' |

**문제점**: 
- `church_news`만 ENUM 타입 사용 (newsstatus)
- 나머지는 모두 character varying 사용
- **이것이 my-posts API에서 UNION 오류 발생 원인!**

### 4. **ENUM 타입 현황**
```sql
newspriority: urgent, important, normal
newsstatus: active, completed, cancelled  -- church_news만 사용
```

### 5. **제목 컬럼 길이 불일치**

| 테이블명 | 제목 컬럼 길이 |
|----------|----------------|
| `church_news` | 255 |
| **나머지 7개 테이블** | **200** |

### 6. **타임존 불일치**

| 테이블명 | created_at 타입 |
|----------|-----------------|
| `community_music_teams` | timestamp **without** time zone |
| **나머지 7개 테이블** | timestamp **with** time zone |

## 🚨 즉시 해결해야 할 문제들

### Priority 1: my-posts API UNION 오류
- **원인**: `church_news.status`가 ENUM, 나머지가 VARCHAR
- **해결**: `status::text` 캐스팅 (이미 적용됨)

### Priority 2: 중복 컬럼 정리
```sql
-- 4개 테이블에서 중복 컬럼 존재
community_sharing: user_id + author_id (중복)
community_requests: user_id + author_id (중복)  
job_posts: user_id + author_id (중복)
job_seekers: user_id + author_id (중복)

-- 조회수 중복도 동일한 4개 테이블
community_sharing: view_count + views (중복)
community_requests: view_count + views (중복)
job_posts: view_count + views (중복)  
job_seekers: view_count + views (중복)
```

## 💡 마이그레이션 우선순위

### Phase 1: 즉시 실행 가능 (중복 제거)
```sql
-- 1. user_id 제거 (author_id 사용)
ALTER TABLE community_sharing DROP COLUMN user_id;
ALTER TABLE community_requests DROP COLUMN user_id; 
ALTER TABLE job_posts DROP COLUMN user_id;
ALTER TABLE job_seekers DROP COLUMN user_id;

-- 2. views 제거 (view_count 사용)  
ALTER TABLE community_sharing DROP COLUMN views;
ALTER TABLE community_requests DROP COLUMN views;
ALTER TABLE job_posts DROP COLUMN views;
ALTER TABLE job_seekers DROP COLUMN views;
```

### Phase 2: 추가 표준화 (선택사항)
```sql
-- 1. views만 있는 테이블에 view_count 추가
ALTER TABLE church_events ADD COLUMN view_count INTEGER DEFAULT 0;
ALTER TABLE community_music_teams ADD COLUMN view_count INTEGER DEFAULT 0;
ALTER TABLE music_team_seekers ADD COLUMN view_count INTEGER DEFAULT 0;

-- 2. 데이터 복사 후 views 제거
UPDATE church_events SET view_count = views;
UPDATE community_music_teams SET view_count = views;  
UPDATE music_team_seekers SET view_count = views;

ALTER TABLE church_events DROP COLUMN views;
ALTER TABLE community_music_teams DROP COLUMN views;
ALTER TABLE music_team_seekers DROP COLUMN views;
```

### Phase 3: ENUM 표준화 (복잡함)
```sql
-- church_news.status ENUM → VARCHAR 변경
-- 신중한 접근 필요 (프로덕션 데이터 영향)
```

## 📈 예상 효과

### my-posts API 개선
**Before (복잡함):**
```python
"views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
"author_name": recruitment.author.full_name if recruitment.author else "익명"
```

**After (단순함):**  
```python
"views": post.view_count,
"author_name": post.author.full_name if post.author else "익명"
```

### 데이터 무결성
- 중복 컬럼 제거로 일관성 확보
- 외래키 관계 명확화
- 스토리지 사용량 감소

## ⚠️ 주의사항

1. **백업 필수**: 마이그레이션 전 모든 테이블 백업
2. **단계적 실행**: Phase 1부터 차례대로
3. **테스트 환경 선행**: 프로덕션 적용 전 검증
4. **API 호환성**: 기존 API 응답 형식 유지

## 🎯 결론

**핵심 문제**: 4개 테이블(`community_sharing`, `community_requests`, `job_posts`, `job_seekers`)에서 컬럼 중복으로 인한 복잡성

**해결 방안**: 중복 컬럼 제거 후 표준화된 스키마 적용

**우선순위**: Phase 1 (중복 제거) → Phase 2 (표준화) → Phase 3 (ENUM 통일)

---

**분석 완료일**: 2025-09-13  
**다음 단계**: Phase 1 마이그레이션 스크립트 실행