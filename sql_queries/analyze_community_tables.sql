-- 커뮤니티 API 테이블 구조 분석 - 일관성 확인

-- ===== 1. 테이블명 분석 =====
SELECT 
  '=== 커뮤니티 테이블 목록 ===' as section,
  table_name,
  table_comment
FROM information_schema.tables 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
)
ORDER BY table_name;

-- ===== 2. 공통 컬럼 비교 분석 =====

-- 2-1. ID 컬럼
SELECT 
  '=== ID 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name = 'id'
ORDER BY table_name;

-- 2-2. 제목 컬럼
SELECT 
  '=== 제목 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  character_maximum_length
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name = 'title'
ORDER BY table_name;

-- 2-3. 상태 컬럼
SELECT 
  '=== 상태 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  udt_name
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name = 'status'
ORDER BY table_name;

-- 2-4. 작성자 컬럼
SELECT 
  '=== 작성자 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name = 'author_id'
ORDER BY table_name;

-- 2-5. 조회수 컬럼 (views vs view_count)
SELECT 
  '=== 조회수 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  column_default
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name IN ('views', 'view_count')
ORDER BY table_name, column_name;

-- 2-6. 좋아요 컬럼
SELECT 
  '=== 좋아요 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  column_default
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name = 'likes'
ORDER BY table_name;

-- 2-7. 생성일 컬럼
SELECT 
  '=== 생성일 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name = 'created_at'
ORDER BY table_name;

-- 2-8. 수정일 컬럼
SELECT 
  '=== 수정일 컬럼 ===' as section,
  table_name,
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
AND column_name = 'updated_at'
ORDER BY table_name;

-- ===== 3. ENUM 타입 분석 =====
SELECT 
  '=== ENUM 타입 목록 ===' as section,
  t.typname as enum_name,
  string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as enum_values
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid 
WHERE t.typname LIKE '%status' OR t.typname LIKE '%priority'
GROUP BY t.typname
ORDER BY t.typname;

-- ===== 4. 각 테이블의 전체 컬럼 구조 =====
SELECT 
  '=== 전체 컬럼 구조 ===' as section,
  table_name,
  column_name,
  data_type,
  character_maximum_length,
  is_nullable,
  column_default
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 
  'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers',
  'church_news', 'church_events'
) 
ORDER BY table_name, ordinal_position;

-- ===== 5. 실제 데이터 샘플 확인 =====

-- 5-1. 각 테이블의 레코드 수
SELECT 'community_sharing' as table_name, COUNT(*) as record_count FROM community_sharing
UNION ALL
SELECT 'community_requests', COUNT(*) FROM community_requests
UNION ALL
SELECT 'job_posts', COUNT(*) FROM job_posts
UNION ALL
SELECT 'job_seekers', COUNT(*) FROM job_seekers
UNION ALL
SELECT 'community_music_teams', COUNT(*) FROM community_music_teams
UNION ALL
SELECT 'music_team_seekers', COUNT(*) FROM music_team_seekers
UNION ALL
SELECT 'church_news', COUNT(*) FROM church_news
UNION ALL
SELECT 'church_events', COUNT(*) FROM church_events
ORDER BY record_count DESC;