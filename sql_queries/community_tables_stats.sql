-- 커뮤니티 테이블별 게시글 통계 조회
-- 마이그레이션 후 표준화된 스키마 기준

-- 1. 각 테이블별 총 게시글 수
SELECT 
    '=== 테이블별 게시글 수 ===' as section,
    'community_sharing' as table_name,
    '무료 나눔' as table_label,
    COUNT(*) as total_posts,
    COUNT(CASE WHEN status = 'available' THEN 1 END) as active_posts,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as posts_this_week,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as posts_this_month
FROM community_sharing

UNION ALL

SELECT '', 'community_requests', '물품 요청', 
    COUNT(*),
    COUNT(CASE WHEN status = 'open' OR status = 'active' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
FROM community_requests

UNION ALL

SELECT '', 'job_posts', '구인 공고',
    COUNT(*),
    COUNT(CASE WHEN status = 'active' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
FROM job_posts

UNION ALL

SELECT '', 'job_seekers', '구직 신청',
    COUNT(*),
    COUNT(CASE WHEN status = 'active' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
FROM job_seekers

UNION ALL

SELECT '', 'community_music_teams', '음악팀 모집',
    COUNT(*),
    COUNT(CASE WHEN status = 'open' OR status = 'active' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
FROM community_music_teams

UNION ALL

SELECT '', 'music_team_seekers', '음악팀 참여',
    COUNT(*),
    COUNT(CASE WHEN status = 'available' OR status = 'active' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
FROM music_team_seekers

UNION ALL

SELECT '', 'church_news', '교회 소식',
    COUNT(*),
    COUNT(CASE WHEN status::text = 'active' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
FROM church_news

UNION ALL

SELECT '', 'church_events', '교회 행사',
    COUNT(*),
    COUNT(CASE WHEN status = 'upcoming' OR status = 'active' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END),
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END)
FROM church_events

ORDER BY total_posts DESC;

-- 2. 전체 요약 통계
WITH all_stats AS (
    SELECT COUNT(*) as count FROM community_sharing
    UNION ALL SELECT COUNT(*) FROM community_requests
    UNION ALL SELECT COUNT(*) FROM job_posts
    UNION ALL SELECT COUNT(*) FROM job_seekers
    UNION ALL SELECT COUNT(*) FROM community_music_teams
    UNION ALL SELECT COUNT(*) FROM music_team_seekers
    UNION ALL SELECT COUNT(*) FROM church_news
    UNION ALL SELECT COUNT(*) FROM church_events
)
SELECT 
    '=== 전체 요약 ===' as summary,
    SUM(count) as total_community_posts,
    AVG(count) as avg_posts_per_table,
    MAX(count) as max_posts_in_table,
    MIN(count) as min_posts_in_table
FROM all_stats;

-- 3. 가장 활발한 테이블 TOP 3 (최근 7일 기준)
WITH recent_activity AS (
    SELECT 'community_sharing' as table_name, '무료 나눔' as label, 
           COUNT(*) as recent_posts
    FROM community_sharing 
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    
    UNION ALL
    
    SELECT 'community_requests', '물품 요청',
           COUNT(*)
    FROM community_requests
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    
    UNION ALL
    
    SELECT 'job_posts', '구인 공고',
           COUNT(*)
    FROM job_posts
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    
    UNION ALL
    
    SELECT 'job_seekers', '구직 신청',
           COUNT(*)
    FROM job_seekers
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    
    UNION ALL
    
    SELECT 'community_music_teams', '음악팀 모집',
           COUNT(*)
    FROM community_music_teams
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    
    UNION ALL
    
    SELECT 'music_team_seekers', '음악팀 참여',
           COUNT(*)
    FROM music_team_seekers
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    
    UNION ALL
    
    SELECT 'church_news', '교회 소식',
           COUNT(*)
    FROM church_news
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    
    UNION ALL
    
    SELECT 'church_events', '교회 행사',
           COUNT(*)
    FROM church_events
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
)
SELECT 
    '=== 최근 7일 활발한 테이블 TOP 3 ===' as section,
    table_name,
    label,
    recent_posts
FROM recent_activity
WHERE recent_posts > 0
ORDER BY recent_posts DESC
LIMIT 3;

-- 4. 상태별 분포 (각 테이블의 상태 분포)
SELECT 
    '=== 상태별 분포 ===' as section,
    'community_sharing' as table_name,
    status,
    COUNT(*) as count
FROM community_sharing
GROUP BY status

UNION ALL

SELECT '', 'community_requests', status, COUNT(*)
FROM community_requests
GROUP BY status

UNION ALL

SELECT '', 'job_posts', status, COUNT(*)
FROM job_posts
GROUP BY status

UNION ALL

SELECT '', 'job_seekers', status, COUNT(*)
FROM job_seekers
GROUP BY status

UNION ALL

SELECT '', 'community_music_teams', status, COUNT(*)
FROM community_music_teams
GROUP BY status

UNION ALL

SELECT '', 'music_team_seekers', status, COUNT(*)
FROM music_team_seekers
GROUP BY status

UNION ALL

SELECT '', 'church_news', status::text, COUNT(*)
FROM church_news
GROUP BY status

UNION ALL

SELECT '', 'church_events', status, COUNT(*)
FROM church_events
GROUP BY status

ORDER BY table_name, count DESC;

-- 5. 조회수/좋아요 통계
SELECT 
    '=== 인기도 통계 ===' as section,
    'community_sharing' as table_name,
    AVG(view_count) as avg_views,
    MAX(view_count) as max_views,
    AVG(likes) as avg_likes,
    MAX(likes) as max_likes
FROM community_sharing

UNION ALL

SELECT '', 'community_requests',
    AVG(view_count), MAX(view_count), AVG(likes), MAX(likes)
FROM community_requests

UNION ALL

SELECT '', 'job_posts',
    AVG(view_count), MAX(view_count), AVG(likes), MAX(likes)
FROM job_posts

UNION ALL

SELECT '', 'job_seekers',
    AVG(view_count), MAX(view_count), AVG(likes), MAX(likes)
FROM job_seekers

UNION ALL

SELECT '', 'community_music_teams',
    AVG(view_count), MAX(view_count), AVG(likes), MAX(likes)
FROM community_music_teams

UNION ALL

SELECT '', 'music_team_seekers',
    AVG(view_count), MAX(view_count), AVG(likes), MAX(likes)
FROM music_team_seekers

UNION ALL

SELECT '', 'church_news',
    AVG(view_count), MAX(view_count), AVG(likes), MAX(likes)
FROM church_news

UNION ALL

SELECT '', 'church_events',
    AVG(view_count), MAX(view_count), AVG(likes), MAX(likes)
FROM church_events

ORDER BY avg_views DESC;