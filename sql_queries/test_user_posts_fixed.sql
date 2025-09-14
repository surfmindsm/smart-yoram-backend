-- "어떤이" 사용자의 모든 커뮤니티 글 조회 (컬럼명 수정 버전)

-- 1단계: "어떤이" 사용자 찾기
SELECT 
  '=== 사용자 검색 결과 ===' as section,
  id, 
  full_name, 
  email, 
  created_at::date as join_date
FROM users 
WHERE full_name LIKE '%어떤이%' 
   OR email LIKE '%어떤이%'
   OR full_name LIKE '%test%'
   OR email LIKE '%test%'
ORDER BY created_at DESC
LIMIT 5;

-- 2단계: 첫 번째 사용자의 모든 글 조회 (테이블별로 올바른 컬럼명 사용)
WITH first_user AS (
  SELECT id FROM users 
  WHERE full_name LIKE '%어떤이%' 
     OR email LIKE '%어떤이%'
     OR full_name LIKE '%test%'
     OR email LIKE '%test%'
  ORDER BY created_at DESC 
  LIMIT 1
),
all_user_posts AS (
  -- 무료 나눔 (community_sharing) - view_count, views 둘 다 존재
  SELECT 
    'community_sharing' as table_name,
    'community-sharing' as type,
    '무료 나눔' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(view_count, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM community_sharing 
  WHERE author_id = (SELECT id FROM first_user)
  
  UNION ALL
  
  -- 물품 요청 (community_requests) - view_count, views 둘 다 존재
  SELECT 
    'community_requests' as table_name,
    'community-request' as type,
    '물품 요청' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(view_count, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM community_requests 
  WHERE author_id = (SELECT id FROM first_user)
  
  UNION ALL
  
  -- 구인 공고 (job_posts) - view_count, views 둘 다 존재
  SELECT 
    'job_posts' as table_name,
    'job-posts' as type,
    '구인 공고' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(view_count, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM job_posts 
  WHERE author_id = (SELECT id FROM first_user)
  
  UNION ALL
  
  -- 구직 신청 (job_seekers) - view_count, views 둘 다 존재
  SELECT 
    'job_seekers' as table_name,
    'job-seekers' as type,
    '구직 신청' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(view_count, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM job_seekers 
  WHERE author_id = (SELECT id FROM first_user)
  
  UNION ALL
  
  -- 음악팀 모집 (community_music_teams) - views만 존재
  SELECT 
    'community_music_teams' as table_name,
    'music-team-recruitment' as type,
    '음악팀 모집' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(views, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM community_music_teams 
  WHERE author_id = (SELECT id FROM first_user)
  
  UNION ALL
  
  -- 음악팀 참여 (music_team_seekers) - views만 존재
  SELECT 
    'music_team_seekers' as table_name,
    'music-team-seekers' as type,
    '음악팀 참여' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(views, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM music_team_seekers 
  WHERE author_id = (SELECT id FROM first_user)
  
  UNION ALL
  
  -- 교회 소식 (church_news) - view_count만 존재
  SELECT 
    'church_news' as table_name,
    'church-news' as type,
    '교회 소식' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(view_count, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM church_news 
  WHERE author_id = (SELECT id FROM first_user)
  
  UNION ALL
  
  -- 교회 행사 (church_events) - views만 존재
  SELECT 
    'church_events' as table_name,
    'church-events' as type,
    '교회 행사' as type_label,
    id, title, status::text as status, created_at,
    COALESCE(views, 0) as views, 
    COALESCE(likes, 0) as likes,
    author_id
  FROM church_events 
  WHERE author_id = (SELECT id FROM first_user)
)
SELECT 
  '=== 사용자 작성 글 목록 ===' as section,
  table_name,
  type,
  type_label,
  id,
  title,
  status,
  created_at::date as date_created,
  views,
  likes,
  author_id
FROM all_user_posts
ORDER BY created_at DESC;

-- 3단계: 테이블별 통계
WITH first_user AS (
  SELECT id FROM users 
  WHERE full_name LIKE '%어떤이%' 
     OR email LIKE '%어떤이%'
     OR full_name LIKE '%test%'
     OR email LIKE '%test%'
  ORDER BY created_at DESC 
  LIMIT 1
),
stats AS (
  SELECT 'community_sharing' as table_name, '무료 나눔' as type_label, COUNT(*) as count 
  FROM community_sharing WHERE author_id = (SELECT id FROM first_user)
  UNION ALL
  SELECT 'community_requests', '물품 요청', COUNT(*) 
  FROM community_requests WHERE author_id = (SELECT id FROM first_user)
  UNION ALL  
  SELECT 'job_posts', '구인 공고', COUNT(*) 
  FROM job_posts WHERE author_id = (SELECT id FROM first_user)
  UNION ALL
  SELECT 'job_seekers', '구직 신청', COUNT(*) 
  FROM job_seekers WHERE author_id = (SELECT id FROM first_user)
  UNION ALL
  SELECT 'community_music_teams', '음악팀 모집', COUNT(*) 
  FROM community_music_teams WHERE author_id = (SELECT id FROM first_user)
  UNION ALL
  SELECT 'music_team_seekers', '음악팀 참여', COUNT(*) 
  FROM music_team_seekers WHERE author_id = (SELECT id FROM first_user)
  UNION ALL
  SELECT 'church_news', '교회 소식', COUNT(*) 
  FROM church_news WHERE author_id = (SELECT id FROM first_user)
  UNION ALL
  SELECT 'church_events', '교회 행사', COUNT(*) 
  FROM church_events WHERE author_id = (SELECT id FROM first_user)
)
SELECT 
  '=== 테이블별 통계 ===' as section,
  table_name,
  type_label,
  count,
  CASE 
    WHEN (SELECT SUM(count) FROM stats) > 0 
    THEN ROUND(count * 100.0 / (SELECT SUM(count) FROM stats), 1) 
    ELSE 0 
  END as percentage
FROM stats 
WHERE count > 0
ORDER BY count DESC;

-- 4단계: 전체 요약
WITH first_user AS (
  SELECT id, full_name FROM users 
  WHERE full_name LIKE '%어떤이%' 
     OR email LIKE '%어떤이%'
     OR full_name LIKE '%test%'
     OR email LIKE '%test%'
  ORDER BY created_at DESC 
  LIMIT 1
)
SELECT 
  '=== 전체 요약 ===' as section,
  (SELECT full_name FROM first_user) as user_name,
  (SELECT id FROM first_user) as user_id,
  (
    (SELECT COUNT(*) FROM community_sharing WHERE author_id = (SELECT id FROM first_user)) +
    (SELECT COUNT(*) FROM community_requests WHERE author_id = (SELECT id FROM first_user)) +
    (SELECT COUNT(*) FROM job_posts WHERE author_id = (SELECT id FROM first_user)) +
    (SELECT COUNT(*) FROM job_seekers WHERE author_id = (SELECT id FROM first_user)) +
    (SELECT COUNT(*) FROM community_music_teams WHERE author_id = (SELECT id FROM first_user)) +
    (SELECT COUNT(*) FROM music_team_seekers WHERE author_id = (SELECT id FROM first_user)) +
    (SELECT COUNT(*) FROM church_news WHERE author_id = (SELECT id FROM first_user)) +
    (SELECT COUNT(*) FROM church_events WHERE author_id = (SELECT id FROM first_user))
  ) as total_posts;

-- 5단계: 각 테이블의 컬럼 존재 여부 확인 (디버깅용)
SELECT '=== 테이블별 컬럼 정보 ===' as section;

-- 각 테이블에 어떤 컬럼이 있는지 확인하는 쿼리
SELECT 
  table_name,
  column_name,
  data_type
FROM information_schema.columns 
WHERE table_name IN (
  'community_sharing', 'community_requests', 'job_posts', 'job_seekers',
  'community_music_teams', 'music_team_seekers', 'church_news', 'church_events'
) 
AND column_name IN ('view_count', 'views', 'likes')
ORDER BY table_name, column_name;