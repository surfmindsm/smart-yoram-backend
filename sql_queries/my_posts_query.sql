-- 특정 사용자가 등록한 모든 커뮤니티 글 조회 SQL
-- 사용법: @user_id를 실제 사용자 ID로 변경하여 실행

-- 예시: "어떤이" 사용자 ID 조회 (사용자 이름으로 ID 찾기)
-- SELECT id, full_name FROM users WHERE full_name LIKE '%어떤이%';

WITH user_posts AS (
  -- 1. 무료 나눔 (community_sharing)
  SELECT 
    id,
    'community-sharing' as type,
    '무료 나눔' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'community_sharing' as table_name
  FROM community_sharing 
  WHERE author_id = @user_id

  UNION ALL

  -- 2. 물품 요청 (community_requests)
  SELECT 
    id,
    'community-request' as type,
    '물품 요청' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'community_requests' as table_name
  FROM community_requests 
  WHERE author_id = @user_id

  UNION ALL

  -- 3. 구인 공고 (job_posts)
  SELECT 
    id,
    'job-posts' as type,
    '구인 공고' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'job_posts' as table_name
  FROM job_posts 
  WHERE author_id = @user_id

  UNION ALL

  -- 4. 구직 신청 (job_seekers)
  SELECT 
    id,
    'job-seekers' as type,
    '구직 신청' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'job_seekers' as table_name
  FROM job_seekers 
  WHERE author_id = @user_id

  UNION ALL

  -- 5. 음악팀 모집 (community_music_teams)
  SELECT 
    id,
    'music-team-recruitment' as type,
    '음악팀 모집' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'community_music_teams' as table_name
  FROM community_music_teams 
  WHERE author_id = @user_id

  UNION ALL

  -- 6. 음악팀 참여 (music_team_seekers)
  SELECT 
    id,
    'music-team-seekers' as type,
    '음악팀 참여' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'music_team_seekers' as table_name
  FROM music_team_seekers 
  WHERE author_id = @user_id

  UNION ALL

  -- 7. 교회 소식 (church_news)
  SELECT 
    id,
    'church-news' as type,
    '교회 소식' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'church_news' as table_name
  FROM church_news 
  WHERE author_id = @user_id

  UNION ALL

  -- 8. 교회 행사 (church_events)
  SELECT 
    id,
    'church-events' as type,
    '교회 행사' as type_label,
    title,
    status,
    created_at,
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes,
    author_id,
    'church_events' as table_name
  FROM church_events 
  WHERE author_id = @user_id
)

-- 최종 결과 조회 (사용자 이름 포함)
SELECT 
  up.id,
  up.type,
  up.type_label,
  up.title,
  up.status,
  up.created_at,
  up.views,
  up.likes,
  up.author_id,
  u.full_name as author_name,
  up.table_name
FROM user_posts up
LEFT JOIN users u ON up.author_id = u.id
ORDER BY up.created_at DESC;

-- ==============================================
-- 실행 예시 (특정 사용자 ID로 조회)
-- ==============================================

-- 예시 1: 사용자 ID 123의 모든 글 조회
/*
WITH user_posts AS (
  -- 위의 쿼리에서 @user_id를 123으로 변경
  -- WHERE author_id = 123
)
SELECT * FROM user_posts ORDER BY created_at DESC;
*/

-- 예시 2: "어떤이" 사용자의 모든 글 조회 (사용자명으로 검색)
/*
WITH target_user AS (
  SELECT id FROM users WHERE full_name LIKE '%어떤이%' LIMIT 1
),
user_posts AS (
  SELECT 
    id, 'community-sharing' as type, '무료 나눔' as type_label,
    title, status, created_at, 
    COALESCE(view_count, views, 0) as views,
    COALESCE(likes, 0) as likes, author_id
  FROM community_sharing 
  WHERE author_id = (SELECT id FROM target_user)
  
  UNION ALL
  
  -- 나머지 테이블들도 동일하게...
)
SELECT * FROM user_posts ORDER BY created_at DESC;
*/

-- ==============================================
-- 통계 조회 (테이블별 글 개수)
-- ==============================================

WITH user_stats AS (
  SELECT '무료 나눔' as category, COUNT(*) as count FROM community_sharing WHERE author_id = @user_id
  UNION ALL
  SELECT '물품 요청' as category, COUNT(*) as count FROM community_requests WHERE author_id = @user_id
  UNION ALL
  SELECT '구인 공고' as category, COUNT(*) as count FROM job_posts WHERE author_id = @user_id
  UNION ALL
  SELECT '구직 신청' as category, COUNT(*) as count FROM job_seekers WHERE author_id = @user_id
  UNION ALL
  SELECT '음악팀 모집' as category, COUNT(*) as count FROM community_music_teams WHERE author_id = @user_id
  UNION ALL
  SELECT '음악팀 참여' as category, COUNT(*) as count FROM music_team_seekers WHERE author_id = @user_id
  UNION ALL
  SELECT '교회 소식' as category, COUNT(*) as count FROM church_news WHERE author_id = @user_id
  UNION ALL
  SELECT '교회 행사' as category, COUNT(*) as count FROM church_events WHERE author_id = @user_id
)
SELECT 
  category,
  count,
  ROUND(count * 100.0 / (SELECT SUM(count) FROM user_stats), 2) as percentage
FROM user_stats 
WHERE count > 0
ORDER BY count DESC;