-- 사용자 '어떤이'가 각 테이블에 올린 글 수 조회
-- 마이그레이션 후 표준화된 스키마 기준

WITH user_info AS (
    SELECT id as user_id FROM users 
    WHERE full_name = '어떤이' AND email = 'test1@test.com'
)
SELECT 
    'community_sharing' as table_name,
    '무료 나눔' as table_label,
    COUNT(*) as user_posts
FROM community_sharing cs
INNER JOIN user_info ui ON cs.author_id = ui.user_id

UNION ALL

SELECT 'community_requests', '물품 요청', COUNT(*)
FROM community_requests cr
INNER JOIN user_info ui ON cr.author_id = ui.user_id

UNION ALL

SELECT 'job_posts', '구인 공고', COUNT(*)
FROM job_posts jp
INNER JOIN user_info ui ON jp.author_id = ui.user_id

UNION ALL

SELECT 'job_seekers', '구직 신청', COUNT(*)
FROM job_seekers js
INNER JOIN user_info ui ON js.author_id = ui.user_id

UNION ALL

SELECT 'community_music_teams', '음악팀 모집', COUNT(*)
FROM community_music_teams cmt
INNER JOIN user_info ui ON cmt.author_id = ui.user_id

UNION ALL

SELECT 'music_team_seekers', '음악팀 참여', COUNT(*)
FROM music_team_seekers mts
INNER JOIN user_info ui ON mts.author_id = ui.user_id

UNION ALL

SELECT 'church_news', '교회 소식', COUNT(*)
FROM church_news cn
INNER JOIN user_info ui ON cn.author_id = ui.user_id

UNION ALL

SELECT 'church_events', '교회 행사', COUNT(*)
FROM church_events ce
INNER JOIN user_info ui ON ce.author_id = ui.user_id

ORDER BY user_posts DESC;