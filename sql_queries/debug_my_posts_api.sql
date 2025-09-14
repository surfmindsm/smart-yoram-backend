-- my-posts API 디버깅: user_id 54로 실제 조회되는 데이터 확인
-- API와 동일한 로직으로 검증

-- 1. user_id 54 사용자 정보 재확인
SELECT 
    '=== user_id 54 사용자 정보 ===' as section,
    id,
    full_name,
    email,
    created_at
FROM users WHERE id = 54;

-- 2. my-posts API와 동일한 쿼리로 각 테이블 확인
SELECT 
    '=== my-posts API 시뮬레이션 ===' as section,
    'community_sharing' as table_type,
    '무료 나눔' as type_label,
    COUNT(*) as found_posts
FROM community_sharing 
WHERE author_id = 54

UNION ALL

SELECT '', 'community_requests', '물품 요청', COUNT(*)
FROM community_requests 
WHERE author_id = 54

UNION ALL

SELECT '', 'job_posts', '구인 공고', COUNT(*)
FROM job_posts 
WHERE author_id = 54

UNION ALL

SELECT '', 'job_seekers', '구직 신청', COUNT(*)
FROM job_seekers 
WHERE author_id = 54

UNION ALL

SELECT '', 'community_music_teams', '음악팀 모집', COUNT(*)
FROM community_music_teams 
WHERE author_id = 54

UNION ALL

SELECT '', 'music_team_seekers', '음악팀 참여', COUNT(*)
FROM music_team_seekers 
WHERE author_id = 54

UNION ALL

SELECT '', 'church_news', '교회 소식', COUNT(*)
FROM church_news 
WHERE author_id = 54

UNION ALL

SELECT '', 'church_events', '교회 행사', COUNT(*)
FROM church_events 
WHERE author_id = 54

ORDER BY found_posts DESC;

-- 3. 실제 게시글들의 상세 정보 (샘플)
SELECT 
    '=== 실제 게시글 샘플 ===' as section,
    'community_music_teams' as table_name,
    id::text as post_id,
    title,
    author_id::text,
    created_at::text
FROM community_music_teams
WHERE author_id = (
    SELECT id FROM users WHERE full_name = '어떤이' AND email = 'test1@test.com'
)
LIMIT 3

UNION ALL

SELECT '', 'church_events', id::text, title, author_id::text, created_at::text
FROM church_events
WHERE author_id = (
    SELECT id FROM users WHERE full_name = '어떤이' AND email = 'test1@test.com'
)
LIMIT 2;

-- 4. author_id가 다른 값인지 확인
SELECT 
    '=== author_id 분포 확인 ===' as section,
    author_id,
    COUNT(*) as posts_count
FROM (
    SELECT author_id FROM community_music_teams
    UNION ALL SELECT author_id FROM church_events  
    UNION ALL SELECT author_id FROM job_posts
    UNION ALL SELECT author_id FROM music_team_seekers
    UNION ALL SELECT author_id FROM church_news
    UNION ALL SELECT author_id FROM community_sharing
    UNION ALL SELECT author_id FROM community_requests
    UNION ALL SELECT author_id FROM job_seekers
) all_posts
GROUP BY author_id
ORDER BY posts_count DESC
LIMIT 5;