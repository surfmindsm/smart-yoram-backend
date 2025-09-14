-- 커뮤니티 테이블별 게시글 수 조회 (간단 버전)
-- 마이그레이션 후 표준화된 스키마 기준

-- 각 테이블별 총 게시글 수
SELECT 
    'community_sharing' as table_name,
    '무료 나눔' as table_label,
    COUNT(*) as total_posts
FROM community_sharing

UNION ALL

SELECT 'community_requests', '물품 요청', COUNT(*)
FROM community_requests

UNION ALL

SELECT 'job_posts', '구인 공고', COUNT(*)
FROM job_posts

UNION ALL

SELECT 'job_seekers', '구직 신청', COUNT(*)
FROM job_seekers

UNION ALL

SELECT 'community_music_teams', '음악팀 모집', COUNT(*)
FROM community_music_teams

UNION ALL

SELECT 'music_team_seekers', '음악팀 참여', COUNT(*)
FROM music_team_seekers

UNION ALL

SELECT 'church_news', '교회 소식', COUNT(*)
FROM church_news

UNION ALL

SELECT 'church_events', '교회 행사', COUNT(*)
FROM church_events

ORDER BY total_posts DESC;