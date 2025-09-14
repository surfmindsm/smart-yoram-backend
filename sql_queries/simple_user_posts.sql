-- 간단한 버전: 조회수 컬럼 없이 기본 정보만 조회

-- 1단계: "어떤이" 사용자 찾기
SELECT 
  '=== 사용자 검색 ===' as info,
  id, full_name, email
FROM users 
WHERE full_name LIKE '%어떤이%' 
   OR email LIKE '%어떤이%'
   OR full_name LIKE '%test%'
   OR email LIKE '%test%'
ORDER BY created_at DESC
LIMIT 3;

-- 2단계: 사용자 ID를 직접 입력해서 조회 (위에서 확인한 ID로 변경)
-- 예시: 사용자 ID가 5라고 가정

-- 모든 커뮤니티 테이블의 글 조회 (기본 정보만, status를 텍스트로 캐스팅)
SELECT '무료 나눔' as category, id, title, status::text as status, created_at::date as date_created, author_id
FROM community_sharing WHERE author_id = 5
UNION ALL
SELECT '물품 요청', id, title, status::text, created_at::date, author_id  
FROM community_requests WHERE author_id = 5
UNION ALL
SELECT '구인 공고', id, title, status::text, created_at::date, author_id
FROM job_posts WHERE author_id = 5
UNION ALL
SELECT '구직 신청', id, title, status::text, created_at::date, author_id
FROM job_seekers WHERE author_id = 5
UNION ALL
SELECT '음악팀 모집', id, title, status::text, created_at::date, author_id
FROM community_music_teams WHERE author_id = 5
UNION ALL
SELECT '음악팀 참여', id, title, status::text, created_at::date, author_id
FROM music_team_seekers WHERE author_id = 5
UNION ALL
SELECT '교회 소식', id, title, status::text, created_at::date, author_id
FROM church_news WHERE author_id = 5
UNION ALL
SELECT '교회 행사', id, title, status::text, created_at::date, author_id
FROM church_events WHERE author_id = 5
ORDER BY date_created DESC;

-- 3단계: 테이블별 글 개수 통계
SELECT '=== 통계 ===' as info, '' as table_name, 0 as count
UNION ALL
SELECT '', 'community_sharing', COUNT(*) FROM community_sharing WHERE author_id = 5
UNION ALL
SELECT '', 'community_requests', COUNT(*) FROM community_requests WHERE author_id = 5
UNION ALL  
SELECT '', 'job_posts', COUNT(*) FROM job_posts WHERE author_id = 5
UNION ALL
SELECT '', 'job_seekers', COUNT(*) FROM job_seekers WHERE author_id = 5
UNION ALL
SELECT '', 'community_music_teams', COUNT(*) FROM community_music_teams WHERE author_id = 5
UNION ALL
SELECT '', 'music_team_seekers', COUNT(*) FROM music_team_seekers WHERE author_id = 5
UNION ALL
SELECT '', 'church_news', COUNT(*) FROM church_news WHERE author_id = 5
UNION ALL
SELECT '', 'church_events', COUNT(*) FROM church_events WHERE author_id = 5
ORDER BY count DESC;

-- 4단계: 전체 총합
SELECT 
  '=== 전체 요약 ===' as info,
  (
    (SELECT COUNT(*) FROM community_sharing WHERE author_id = 5) +
    (SELECT COUNT(*) FROM community_requests WHERE author_id = 5) +
    (SELECT COUNT(*) FROM job_posts WHERE author_id = 5) +
    (SELECT COUNT(*) FROM job_seekers WHERE author_id = 5) +
    (SELECT COUNT(*) FROM community_music_teams WHERE author_id = 5) +
    (SELECT COUNT(*) FROM music_team_seekers WHERE author_id = 5) +
    (SELECT COUNT(*) FROM church_news WHERE author_id = 5) +
    (SELECT COUNT(*) FROM church_events WHERE author_id = 5)
  ) as total_posts_for_user_5;

-- ===== 사용 방법 =====
-- 1. 첫 번째 쿼리를 실행해서 "어떤이" 사용자의 ID를 확인
-- 2. 위의 모든 '5'를 실제 사용자 ID로 변경
-- 3. 쿼리 실행하여 결과 확인