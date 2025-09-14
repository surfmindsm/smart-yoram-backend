# 커뮤니티 테이블 표준화 - 수동 마이그레이션 가이드

## 📋 개요

커뮤니티 테이블의 컬럼 중복 문제를 해결하기 위한 단계별 수동 마이그레이션 가이드입니다.

## 🚨 사전 준비사항

### 1. 백업 생성 (필수)

```sql
-- Supabase에서 실행
CREATE TABLE community_sharing_backup AS SELECT * FROM community_sharing;
CREATE TABLE community_requests_backup AS SELECT * FROM community_requests;
CREATE TABLE job_posts_backup AS SELECT * FROM job_posts;
CREATE TABLE job_seekers_backup AS SELECT * FROM job_seekers;

-- 백업 확인
SELECT 'community_sharing' as table_name, COUNT(*) as count FROM community_sharing_backup
UNION ALL
SELECT 'community_requests', COUNT(*) FROM community_requests_backup
UNION ALL
SELECT 'job_posts', COUNT(*) FROM job_posts_backup
UNION ALL
SELECT 'job_seekers', COUNT(*) FROM job_seekers_backup;
```

### 2. 현재 데이터 확인

```sql
-- 중복 컬럼 현황 확인
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('community_sharing', 'community_requests', 'job_posts', 'job_seekers')
  AND column_name IN ('user_id', 'author_id', 'views', 'view_count')
ORDER BY table_name, column_name;
```

## 🔄 Phase 1: 중복 컬럼 제거

### 1.1 user_id → author_id 통일

```sql
-- 1. job_posts 테이블 (user_id → author_id)
-- 현재: user_id(사용중), author_id(NULL)
UPDATE job_posts SET author_id = user_id WHERE author_id IS NULL;
ALTER TABLE job_posts ALTER COLUMN author_id SET NOT NULL;
ALTER TABLE job_posts ADD CONSTRAINT fk_job_posts_author FOREIGN KEY (author_id) REFERENCES users(id);
ALTER TABLE job_posts DROP COLUMN user_id;

-- 2. job_seekers 테이블 (user_id → author_id)
-- 현재: user_id(사용중), author_id(NULL)
UPDATE job_seekers SET author_id = user_id WHERE author_id IS NULL;
ALTER TABLE job_seekers ALTER COLUMN author_id SET NOT NULL;
ALTER TABLE job_seekers ADD CONSTRAINT fk_job_seekers_author FOREIGN KEY (author_id) REFERENCES users(id);
ALTER TABLE job_seekers DROP COLUMN user_id;

-- 3. community_sharing 테이블 (user_id만 유지, author_id 제거)
-- 현재: user_id(사용중), author_id(NULL)
ALTER TABLE community_sharing DROP COLUMN author_id;

-- 4. community_requests 테이블 (user_id만 유지, author_id 제거)
-- 현재: user_id(사용중), author_id(NULL)
ALTER TABLE community_requests DROP COLUMN author_id;
```

**중간 검증:**
```sql
-- author_id가 모든 테이블에 존재하는지 확인
SELECT 
    table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'author_id'
    ) THEN '✅' ELSE '❌' END as has_author_id,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'user_id'
    ) THEN '❌ (should be removed)' ELSE '✅' END as user_id_removed
FROM (VALUES 
    ('job_posts'),
    ('job_seekers')
) as t(table_name);

-- community_sharing, community_requests는 user_id만 있어야 함
SELECT 
    table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'user_id'
    ) THEN '✅' ELSE '❌' END as has_user_id
FROM (VALUES 
    ('community_sharing'),
    ('community_requests')
) as t(table_name);
```

### 1.2 views → view_count 통일

```sql
-- 1. community_sharing 테이블 (view_count만 유지, views 제거)
-- 현재: view_count(사용중), views(중복)
ALTER TABLE community_sharing DROP COLUMN views;

-- 2. community_requests 테이블 (view_count만 유지, views 제거)
-- 현재: view_count(사용중), views(중복)
ALTER TABLE community_requests DROP COLUMN views;

-- 3. job_posts 테이블 (view_count만 유지, views 제거)
-- 현재: view_count(사용중), views(중복)
ALTER TABLE job_posts DROP COLUMN views;

-- 4. job_seekers 테이블 (view_count만 유지, views 제거)
-- 현재: view_count(사용중), views(중복)
ALTER TABLE job_seekers DROP COLUMN views;
```

**중간 검증:**
```sql
-- view_count만 있고 views가 제거되었는지 확인
SELECT 
    table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'view_count'
    ) THEN '✅' ELSE '❌' END as has_view_count,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'views'
    ) THEN '❌ (should be removed)' ELSE '✅' END as views_removed
FROM (VALUES 
    ('community_sharing'),
    ('community_requests'),
    ('job_posts'),
    ('job_seekers')
) as t(table_name);
```

## 🔄 Phase 2: 나머지 테이블 표준화 (views → view_count)

```sql
-- 1. community_music_teams (views → view_count)
ALTER TABLE community_music_teams ADD COLUMN view_count INTEGER DEFAULT 0;
UPDATE community_music_teams SET view_count = COALESCE(views, 0);
ALTER TABLE community_music_teams DROP COLUMN views;

-- 2. music_team_seekers (views → view_count)
ALTER TABLE music_team_seekers ADD COLUMN view_count INTEGER DEFAULT 0;
UPDATE music_team_seekers SET view_count = COALESCE(views, 0);
ALTER TABLE music_team_seekers DROP COLUMN views;

-- 3. church_events (views → view_count)
ALTER TABLE church_events ADD COLUMN view_count INTEGER DEFAULT 0;
UPDATE church_events SET view_count = COALESCE(views, 0);
ALTER TABLE church_events DROP COLUMN views;
```

**검증:**
```sql
-- 모든 테이블이 view_count를 가지는지 확인
SELECT 
    table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'view_count'
    ) THEN '✅' ELSE '❌' END as has_view_count
FROM (VALUES 
    ('community_sharing'),
    ('community_requests'),
    ('job_posts'),
    ('job_seekers'),
    ('community_music_teams'),
    ('music_team_seekers'),
    ('church_news'),
    ('church_events')
) as t(table_name);
```

## 🔄 Phase 3: 최종 검증

```sql
-- 최종 표준화 결과 확인
SELECT 
    '=== 최종 표준화 검증 ===' as status,
    table_name,
    -- author_id 또는 user_id 확인
    CASE 
        WHEN table_name IN ('community_sharing', 'community_requests') 
            AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'user_id')
        THEN '✅ user_id'
        WHEN table_name NOT IN ('community_sharing', 'community_requests') 
            AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'author_id')
        THEN '✅ author_id'
        ELSE '❌' 
    END as author_field,
    -- view_count 확인
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'view_count'
    ) THEN '✅' ELSE '❌' END as has_view_count
FROM (VALUES 
    ('community_sharing'),
    ('community_requests'), 
    ('job_posts'),
    ('job_seekers'),
    ('community_music_teams'),
    ('music_team_seekers'),
    ('church_news'),
    ('church_events')
) as t(table_name);

-- 레코드 수 확인 (데이터 손실 없음 확인)
SELECT 
    '=== 데이터 무결성 확인 ===' as status,
    'community_sharing' as table_name, COUNT(*) as current_count, 
    (SELECT COUNT(*) FROM community_sharing_backup) as backup_count
FROM community_sharing
UNION ALL
SELECT '', 'community_requests', COUNT(*), (SELECT COUNT(*) FROM community_requests_backup)
FROM community_requests
UNION ALL
SELECT '', 'job_posts', COUNT(*), (SELECT COUNT(*) FROM job_posts_backup)
FROM job_posts
UNION ALL
SELECT '', 'job_seekers', COUNT(*), (SELECT COUNT(*) FROM job_seekers_backup)
FROM job_seekers;
```

## 🔧 SQLAlchemy 모델 업데이트

마이그레이션 완료 후 다음 모델 파일들을 업데이트해야 합니다:

### 1. job_posts.py
```python
# 제거할 컬럼들
- user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
- views = Column(Integer, default=0, comment="조회수 (중복)")

# 수정할 relationship
- author = relationship("User", foreign_keys=[author_id])  # user_id → author_id
```

### 2. community_sharing.py
```python
# 제거할 컬럼들
- views = Column(Integer, nullable=True, default=0, comment="조회수2")
- author_id = Column(Integer, nullable=True, comment="작성자 ID2")

# user_id와 view_count만 유지
```

### 3. community_request.py
```python
# 동일하게 중복 컬럼들 제거
```

## 🚨 롤백 절차 (문제 발생시)

```sql
-- 롤백 스크립트
BEGIN;

-- 현재 테이블 삭제
DROP TABLE community_sharing;
DROP TABLE community_requests;
DROP TABLE job_posts;
DROP TABLE job_seekers;

-- 백업에서 복구
ALTER TABLE community_sharing_backup RENAME TO community_sharing;
ALTER TABLE community_requests_backup RENAME TO community_requests;
ALTER TABLE job_posts_backup RENAME TO job_posts;
ALTER TABLE job_seekers_backup RENAME TO job_seekers;

COMMIT;
```

## 📊 예상 효과

### 1. API 코드 단순화
**Before:**
```python
"views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
```

**After:**
```python
"views": post.view_count,  # 모든 테이블에 view_count 표준화
```

### 2. 작성자 필드 일관성
- `job_posts`, `job_seekers`: `author_id` 사용
- `community_sharing`, `community_requests`: `user_id` 사용
- 모든 relationship이 올바른 필드 참조

### 3. 데이터 무결성
- 중복 컬럼 제거로 데이터 불일치 방지
- 외래키 제약조건으로 데이터 무결성 확보

---

**⚠️ 주의사항:**
1. **반드시 백업 후 실행**
2. **단계별로 실행하며 검증**
3. **프로덕션 환경에서는 점검 시간에 수행**
4. **마이그레이션 후 애플리케이션 재시작**

**실행자**: Backend Team  
**검증자**: DevOps Team  
**완료 예정**: TBD