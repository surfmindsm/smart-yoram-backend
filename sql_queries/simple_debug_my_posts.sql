-- 간단한 my-posts API 디버깅
-- user_id 54가 실제로 게시글을 가지고 있는지 확인

-- 1. user_id 54 정보 확인
SELECT id, full_name, email FROM users WHERE id = 54;

-- 2. user_id 54의 각 테이블별 게시글 수 (my-posts API 시뮬레이션)
SELECT 'community_sharing' as table_name, COUNT(*) as posts FROM community_sharing WHERE author_id = 54
UNION ALL
SELECT 'community_requests', COUNT(*) FROM community_requests WHERE author_id = 54
UNION ALL  
SELECT 'job_posts', COUNT(*) FROM job_posts WHERE author_id = 54
UNION ALL
SELECT 'job_seekers', COUNT(*) FROM job_seekers WHERE author_id = 54
UNION ALL
SELECT 'community_music_teams', COUNT(*) FROM community_music_teams WHERE author_id = 54
UNION ALL
SELECT 'music_team_seekers', COUNT(*) FROM music_team_seekers WHERE author_id = 54
UNION ALL
SELECT 'church_news', COUNT(*) FROM church_news WHERE author_id = 54
UNION ALL
SELECT 'church_events', COUNT(*) FROM church_events WHERE author_id = 54;

-- 3. '어떤이' 사용자의 실제 user_id 확인
SELECT id, full_name, email FROM users WHERE full_name = '어떤이';

-- 4. '어떤이' 사용자의 게시글 수
SELECT 'community_music_teams' as table_name, COUNT(*) as posts 
FROM community_music_teams cmt 
INNER JOIN users u ON cmt.author_id = u.id 
WHERE u.full_name = '어떤이'
UNION ALL
SELECT 'church_events', COUNT(*) 
FROM church_events ce 
INNER JOIN users u ON ce.author_id = u.id 
WHERE u.full_name = '어떤이';

-- 5. 모든 author_id 값들 확인 (상위 5개)
SELECT author_id, COUNT(*) as total_posts
FROM (
    SELECT author_id FROM community_music_teams
    UNION ALL SELECT author_id FROM church_events
    UNION ALL SELECT author_id FROM job_posts
    UNION ALL SELECT author_id FROM music_team_seekers
    UNION ALL SELECT author_id FROM church_news
) all_posts
GROUP BY author_id
ORDER BY total_posts DESC
LIMIT 5;