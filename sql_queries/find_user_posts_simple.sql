-- "어떤이" 사용자의 모든 커뮤니티 글 조회 (간단 버전)

-- 1단계: "어떤이" 사용자 찾기
SELECT id, full_name, email, created_at 
FROM users 
WHERE full_name LIKE '%어떤이%' 
   OR email LIKE '%어떤이%'
ORDER BY created_at DESC;

-- 2단계: 특정 사용자 ID의 모든 글 조회 (사용자 ID를 위에서 확인한 값으로 변경)
-- 예시: 사용자 ID가 5라고 가정

-- 무료 나눔
SELECT 'community_sharing' as table_name, id, title, status, created_at, 
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes
FROM community_sharing WHERE author_id = 5
UNION ALL

-- 물품 요청  
SELECT 'community_requests' as table_name, id, title, status, created_at,
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes  
FROM community_requests WHERE author_id = 5
UNION ALL

-- 구직 신청
SELECT 'job_seekers' as table_name, id, title, status, created_at,
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes
FROM job_seekers WHERE author_id = 5
UNION ALL

-- 구인 공고
SELECT 'job_posts' as table_name, id, title, status, created_at,
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes
FROM job_posts WHERE author_id = 5
UNION ALL

-- 음악팀 모집
SELECT 'community_music_teams' as table_name, id, title, status, created_at,
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes
FROM community_music_teams WHERE author_id = 5
UNION ALL

-- 음악팀 참여
SELECT 'music_team_seekers' as table_name, id, title, status, created_at,
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes
FROM music_team_seekers WHERE author_id = 5
UNION ALL

-- 교회 소식
SELECT 'church_news' as table_name, id, title, status, created_at,
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes
FROM church_news WHERE author_id = 5
UNION ALL

-- 교회 행사
SELECT 'church_events' as table_name, id, title, status, created_at,
       COALESCE(view_count, views, 0) as views, COALESCE(likes, 0) as likes
FROM church_events WHERE author_id = 5

ORDER BY created_at DESC;

-- 3단계: 테이블별 통계
SELECT 
  'community_sharing' as table_name, COUNT(*) as count 
FROM community_sharing WHERE author_id = 5
UNION ALL
SELECT 'community_requests', COUNT(*) FROM community_requests WHERE author_id = 5
UNION ALL  
SELECT 'job_posts', COUNT(*) FROM job_posts WHERE author_id = 5
UNION ALL
SELECT 'job_seekers', COUNT(*) FROM job_seekers WHERE author_id = 5
UNION ALL
SELECT 'community_music_teams', COUNT(*) FROM community_music_teams WHERE author_id = 5
UNION ALL
SELECT 'music_team_seekers', COUNT(*) FROM music_team_seekers WHERE author_id = 5
UNION ALL
SELECT 'church_news', COUNT(*) FROM church_news WHERE author_id = 5
UNION ALL
SELECT 'church_events', COUNT(*) FROM church_events WHERE author_id = 5
ORDER BY count DESC;