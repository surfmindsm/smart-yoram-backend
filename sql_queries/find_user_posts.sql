-- 사용자 '어떤이' (test1@test.com)가 작성한 모든 커뮤니티 글 조회
-- 마이그레이션 후 표준화된 스키마 기준

-- 1. 사용자 ID 먼저 확인
SELECT id, full_name, email FROM users 
WHERE full_name = '어떤이' AND email = 'test1@test.com';

-- 2. 모든 커뮤니티 테이블에서 해당 사용자의 글 조회 (UNION)
WITH user_info AS (
    SELECT id as user_id FROM users 
    WHERE full_name = '어떤이' AND email = 'test1@test.com'
)
SELECT 
    'community_sharing' as table_type,
    '무료 나눔' as type_label,
    id,
    title,
    status,
    view_count as views,
    likes,
    created_at,
    updated_at
FROM community_sharing cs
INNER JOIN user_info ui ON cs.author_id = ui.user_id

UNION ALL

SELECT 
    'community_requests' as table_type,
    '물품 요청' as type_label,
    id,
    title,
    status,
    view_count as views,
    likes,
    created_at,
    updated_at
FROM community_requests cr
INNER JOIN user_info ui ON cr.author_id = ui.user_id

UNION ALL

SELECT 
    'job_posts' as table_type,
    '구인 공고' as type_label,
    id,
    title,
    status,
    view_count as views,
    likes,
    created_at,
    updated_at
FROM job_posts jp
INNER JOIN user_info ui ON jp.author_id = ui.user_id

UNION ALL

SELECT 
    'job_seekers' as table_type,
    '구직 신청' as type_label,
    id,
    title,
    status,
    view_count as views,
    likes,
    created_at,
    updated_at
FROM job_seekers js
INNER JOIN user_info ui ON js.author_id = ui.user_id

UNION ALL

SELECT 
    'community_music_teams' as table_type,
    '음악팀 모집' as type_label,
    id,
    title,
    status,
    view_count as views,
    likes,
    created_at,
    updated_at
FROM community_music_teams cmt
INNER JOIN user_info ui ON cmt.author_id = ui.user_id

UNION ALL

SELECT 
    'music_team_seekers' as table_type,
    '음악팀 참여' as type_label,
    id,
    title,
    status,
    view_count as views,
    likes,
    created_at,
    updated_at
FROM music_team_seekers mts
INNER JOIN user_info ui ON mts.author_id = ui.user_id

UNION ALL

SELECT 
    'church_news' as table_type,
    '교회 소식' as type_label,
    id,
    title,
    status::text as status,  -- ENUM을 TEXT로 캐스팅
    view_count as views,
    likes,
    created_at,
    updated_at
FROM church_news cn
INNER JOIN user_info ui ON cn.author_id = ui.user_id

UNION ALL

SELECT 
    'church_events' as table_type,
    '교회 행사' as type_label,
    id,
    title,
    status,
    view_count as views,
    likes,
    created_at,
    updated_at
FROM church_events ce
INNER JOIN user_info ui ON ce.author_id = ui.user_id

ORDER BY created_at DESC;

-- 3. 각 테이블별 개수 요약
WITH user_info AS (
    SELECT id as user_id FROM users 
    WHERE full_name = '어떤이' AND email = 'test1@test.com'
)
SELECT 
    '=== 테이블별 게시글 수 요약 ===' as summary,
    'community_sharing' as table_name,
    COUNT(*) as post_count
FROM community_sharing cs
INNER JOIN user_info ui ON cs.author_id = ui.user_id

UNION ALL

SELECT '', 'community_requests', COUNT(*)
FROM community_requests cr
INNER JOIN user_info ui ON cr.author_id = ui.user_id

UNION ALL

SELECT '', 'job_posts', COUNT(*)
FROM job_posts jp
INNER JOIN user_info ui ON jp.author_id = ui.user_id

UNION ALL

SELECT '', 'job_seekers', COUNT(*)
FROM job_seekers js
INNER JOIN user_info ui ON js.author_id = ui.user_id

UNION ALL

SELECT '', 'community_music_teams', COUNT(*)
FROM community_music_teams cmt
INNER JOIN user_info ui ON cmt.author_id = ui.user_id

UNION ALL

SELECT '', 'music_team_seekers', COUNT(*)
FROM music_team_seekers mts
INNER JOIN user_info ui ON mts.author_id = ui.user_id

UNION ALL

SELECT '', 'church_news', COUNT(*)
FROM church_news cn
INNER JOIN user_info ui ON cn.author_id = ui.user_id

UNION ALL

SELECT '', 'church_events', COUNT(*)
FROM church_events ce
INNER JOIN user_info ui ON ce.author_id = ui.user_id;

-- 4. 전체 통계
WITH user_info AS (
    SELECT id as user_id FROM users 
    WHERE full_name = '어떤이' AND email = 'test1@test.com'
),
all_posts AS (
    SELECT 'community_sharing' as source FROM community_sharing cs INNER JOIN user_info ui ON cs.author_id = ui.user_id
    UNION ALL SELECT 'community_requests' FROM community_requests cr INNER JOIN user_info ui ON cr.author_id = ui.user_id
    UNION ALL SELECT 'job_posts' FROM job_posts jp INNER JOIN user_info ui ON jp.author_id = ui.user_id
    UNION ALL SELECT 'job_seekers' FROM job_seekers js INNER JOIN user_info ui ON js.author_id = ui.user_id
    UNION ALL SELECT 'community_music_teams' FROM community_music_teams cmt INNER JOIN user_info ui ON cmt.author_id = ui.user_id
    UNION ALL SELECT 'music_team_seekers' FROM music_team_seekers mts INNER JOIN user_info ui ON mts.author_id = ui.user_id
    UNION ALL SELECT 'church_news' FROM church_news cn INNER JOIN user_info ui ON cn.author_id = ui.user_id
    UNION ALL SELECT 'church_events' FROM church_events ce INNER JOIN user_info ui ON ce.author_id = ui.user_id
)
SELECT 
    '=== 전체 요약 ===' as final_summary,
    COUNT(*) as total_posts,
    (SELECT full_name FROM users WHERE full_name = '어떤이' AND email = 'test1@test.com') as user_name,
    (SELECT email FROM users WHERE full_name = '어떤이' AND email = 'test1@test.com') as user_email
FROM all_posts;