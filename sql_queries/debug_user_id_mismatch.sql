-- 🚨 사용자 ID 불일치 문제 긴급 디버깅
-- JWT user_id 54 vs 실제 게시글 작성자 확인

-- 1. test1@test.com 사용자의 실제 user_id 확인
SELECT 
    '=== 사용자 정보 확인 ===' as section,
    id as actual_user_id,
    full_name,
    email,
    created_at
FROM users 
WHERE email = 'test1@test.com' OR full_name = '어떤이'
ORDER BY id;

-- 2. JWT user_id 54로 조회 (현재 API에서 사용)
WITH jwt_user AS (
    SELECT 54 as jwt_user_id
)
SELECT 
    '=== JWT user_id 54 게시글 수 ===' as section,
    'community_sharing' as table_name,
    COUNT(*) as posts_count
FROM community_sharing cs, jwt_user ju
WHERE cs.author_id = ju.jwt_user_id

UNION ALL
SELECT '', 'community_requests', COUNT(*)
FROM community_requests cr, jwt_user ju
WHERE cr.author_id = ju.jwt_user_id

UNION ALL
SELECT '', 'job_posts', COUNT(*)
FROM job_posts jp, jwt_user ju
WHERE jp.author_id = ju.jwt_user_id

UNION ALL
SELECT '', 'job_seekers', COUNT(*)
FROM job_seekers js, jwt_user ju
WHERE js.author_id = ju.jwt_user_id

UNION ALL
SELECT '', 'community_music_teams', COUNT(*)
FROM community_music_teams cmt, jwt_user ju
WHERE cmt.author_id = ju.jwt_user_id

UNION ALL
SELECT '', 'music_team_seekers', COUNT(*)
FROM music_team_seekers mts, jwt_user ju
WHERE mts.author_id = ju.jwt_user_id

UNION ALL
SELECT '', 'church_news', COUNT(*)
FROM church_news cn, jwt_user ju
WHERE cn.author_id = ju.jwt_user_id

UNION ALL
SELECT '', 'church_events', COUNT(*)
FROM church_events ce, jwt_user ju
WHERE ce.author_id = ju.jwt_user_id;

-- 3. '어떤이' 사용자가 실제로 작성한 게시글의 author_id들 확인
SELECT 
    '=== 실제 게시글의 author_id 확인 ===' as section,
    'community_music_teams' as table_name,
    author_id,
    COUNT(*) as posts_count,
    MIN(title) as sample_title
FROM community_music_teams cmt
INNER JOIN users u ON cmt.author_id = u.id
WHERE u.full_name = '어떤이' AND u.email = 'test1@test.com'
GROUP BY author_id

UNION ALL

SELECT '', 'church_events', author_id, COUNT(*), MIN(title)
FROM church_events ce
INNER JOIN users u ON ce.author_id = u.id
WHERE u.full_name = '어떤이' AND u.email = 'test1@test.com'
GROUP BY author_id

UNION ALL

SELECT '', 'job_posts', author_id, COUNT(*), MIN(title)
FROM job_posts jp
INNER JOIN users u ON jp.author_id = u.id
WHERE u.full_name = '어떤이' AND u.email = 'test1@test.com'
GROUP BY author_id

UNION ALL

SELECT '', 'music_team_seekers', author_id, COUNT(*), MIN(title)
FROM music_team_seekers mts
INNER JOIN users u ON mts.author_id = u.id
WHERE u.full_name = '어떤이' AND u.email = 'test1@test.com'
GROUP BY author_id

UNION ALL

SELECT '', 'church_news', author_id, COUNT(*), MIN(title)
FROM church_news cn
INNER JOIN users u ON cn.author_id = u.id
WHERE u.full_name = '어떤이' AND u.email = 'test1@test.com'
GROUP BY author_id;

-- 4. 중복 사용자 계정 확인
SELECT 
    '=== 중복 계정 확인 ===' as section,
    full_name,
    email,
    id as user_id,
    created_at
FROM users 
WHERE full_name LIKE '%어떤이%' OR email LIKE '%test1%'
ORDER BY created_at;

-- 5. JWT와 실제 author_id 불일치 요약
SELECT 
    '=== 불일치 요약 ===' as summary,
    (SELECT id FROM users WHERE email = 'test1@test.com' LIMIT 1) as actual_user_id,
    54 as jwt_user_id,
    CASE 
        WHEN (SELECT id FROM users WHERE email = 'test1@test.com' LIMIT 1) = 54 
        THEN '✅ 일치' 
        ELSE '🚨 불일치' 
    END as id_match_status;