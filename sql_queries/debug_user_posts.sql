-- 디버깅용 단계별 SQL - ENUM 타입 오류 없는 안전한 버전

-- ===== 1단계: 사용자 찾기 =====
SELECT 
  'Step 1: Find Users' as step,
  id, 
  full_name, 
  email,
  created_at::date as join_date
FROM users 
WHERE full_name LIKE '%어떤이%' 
   OR full_name LIKE '%test%'
   OR email LIKE '%test%'
   OR email LIKE '%어떤이%'
ORDER BY created_at DESC
LIMIT 5;

-- ===== 2단계: 각 테이블별로 개별 조회 (오류 방지) =====

-- 2-1. 무료 나눔
SELECT 
  'Step 2-1: 무료 나눔' as step,
  'community_sharing' as table_name,
  COUNT(*) as total_count
FROM community_sharing 
WHERE author_id = 1;  -- 사용자 ID를 실제 값으로 변경

-- 2-2. 물품 요청
SELECT 
  'Step 2-2: 물품 요청' as step,
  'community_requests' as table_name,
  COUNT(*) as total_count
FROM community_requests 
WHERE author_id = 1;

-- 2-3. 구인 공고
SELECT 
  'Step 2-3: 구인 공고' as step,
  'job_posts' as table_name,
  COUNT(*) as total_count
FROM job_posts 
WHERE author_id = 1;

-- 2-4. 구직 신청
SELECT 
  'Step 2-4: 구직 신청' as step,
  'job_seekers' as table_name,
  COUNT(*) as total_count
FROM job_seekers 
WHERE author_id = 1;

-- 2-5. 음악팀 모집
SELECT 
  'Step 2-5: 음악팀 모집' as step,
  'community_music_teams' as table_name,
  COUNT(*) as total_count
FROM community_music_teams 
WHERE author_id = 1;

-- 2-6. 음악팀 참여
SELECT 
  'Step 2-6: 음악팀 참여' as step,
  'music_team_seekers' as table_name,
  COUNT(*) as total_count
FROM music_team_seekers 
WHERE author_id = 1;

-- 2-7. 교회 소식
SELECT 
  'Step 2-7: 교회 소식' as step,
  'church_news' as table_name,
  COUNT(*) as total_count
FROM church_news 
WHERE author_id = 1;

-- 2-8. 교회 행사
SELECT 
  'Step 2-8: 교회 행사' as step,
  'church_events' as table_name,
  COUNT(*) as total_count
FROM church_events 
WHERE author_id = 1;

-- ===== 3단계: 실제 글 데이터 조회 (개별 테이블) =====

-- 3-1. 무료 나눔 글 목록
SELECT 
  'community_sharing' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM community_sharing 
WHERE author_id = 1
ORDER BY created_at DESC;

-- 3-2. 물품 요청 글 목록  
SELECT 
  'community_requests' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM community_requests 
WHERE author_id = 1
ORDER BY created_at DESC;

-- 3-3. 구인 공고 글 목록
SELECT 
  'job_posts' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM job_posts 
WHERE author_id = 1
ORDER BY created_at DESC;

-- 3-4. 구직 신청 글 목록
SELECT 
  'job_seekers' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM job_seekers 
WHERE author_id = 1
ORDER BY created_at DESC;

-- 3-5. 음악팀 모집 글 목록
SELECT 
  'community_music_teams' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM community_music_teams 
WHERE author_id = 1
ORDER BY created_at DESC;

-- 3-6. 음악팀 참여 글 목록
SELECT 
  'music_team_seekers' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM music_team_seekers 
WHERE author_id = 1
ORDER BY created_at DESC;

-- 3-7. 교회 소식 글 목록
SELECT 
  'church_news' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM church_news 
WHERE author_id = 1
ORDER BY created_at DESC;

-- 3-8. 교회 행사 글 목록
SELECT 
  'church_events' as source_table,
  id,
  title,
  CAST(status AS TEXT) as status_text,
  created_at::date as date_created,
  author_id
FROM church_events 
WHERE author_id = 1
ORDER BY created_at DESC;

-- ===== 4단계: 전체 요약 통계 =====
SELECT 
  'SUMMARY' as step,
  (SELECT COUNT(*) FROM community_sharing WHERE author_id = 1) as sharing_count,
  (SELECT COUNT(*) FROM community_requests WHERE author_id = 1) as requests_count,
  (SELECT COUNT(*) FROM job_posts WHERE author_id = 1) as job_posts_count,
  (SELECT COUNT(*) FROM job_seekers WHERE author_id = 1) as job_seekers_count,
  (SELECT COUNT(*) FROM community_music_teams WHERE author_id = 1) as music_teams_count,
  (SELECT COUNT(*) FROM music_team_seekers WHERE author_id = 1) as music_seekers_count,
  (SELECT COUNT(*) FROM church_news WHERE author_id = 1) as church_news_count,
  (SELECT COUNT(*) FROM church_events WHERE author_id = 1) as church_events_count,
  (
    (SELECT COUNT(*) FROM community_sharing WHERE author_id = 1) +
    (SELECT COUNT(*) FROM community_requests WHERE author_id = 1) +
    (SELECT COUNT(*) FROM job_posts WHERE author_id = 1) +
    (SELECT COUNT(*) FROM job_seekers WHERE author_id = 1) +
    (SELECT COUNT(*) FROM community_music_teams WHERE author_id = 1) +
    (SELECT COUNT(*) FROM music_team_seekers WHERE author_id = 1) +
    (SELECT COUNT(*) FROM church_news WHERE author_id = 1) +
    (SELECT COUNT(*) FROM church_events WHERE author_id = 1)
  ) as total_posts;

-- ===== 사용법 =====
-- 1. 위의 모든 '1'을 실제 사용자 ID로 변경 (1단계에서 확인한 ID)
-- 2. 각 쿼리를 단계별로 실행
-- 3. UNION 오류 없이 안전하게 각 테이블의 데이터 확인 가능