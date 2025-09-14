-- 커뮤니티 테이블 표준화 마이그레이션 스크립트
-- 실행 전 반드시 백업 생성 필요!

-- =====================================================
-- 1단계: 백업 테이블 생성 (안전장치)
-- =====================================================

CREATE TABLE IF NOT EXISTS community_sharing_backup AS SELECT * FROM community_sharing;
CREATE TABLE IF NOT EXISTS community_requests_backup AS SELECT * FROM community_requests;
CREATE TABLE IF NOT EXISTS job_posts_backup AS SELECT * FROM job_posts;
CREATE TABLE IF NOT EXISTS job_seekers_backup AS SELECT * FROM job_seekers;
CREATE TABLE IF NOT EXISTS community_music_teams_backup AS SELECT * FROM community_music_teams;
CREATE TABLE IF NOT EXISTS music_team_seekers_backup AS SELECT * FROM music_team_seekers;
CREATE TABLE IF NOT EXISTS church_news_backup AS SELECT * FROM church_news;
CREATE TABLE IF NOT EXISTS church_events_backup AS SELECT * FROM church_events;

SELECT '백업 테이블 생성 완료' as status;

-- =====================================================
-- 2단계: 작성자 필드 표준화 (author_id 통일)
-- =====================================================

BEGIN;

-- job_posts, job_seekers 테이블에 author_id 추가
ALTER TABLE job_posts ADD COLUMN IF NOT EXISTS author_id INTEGER;
ALTER TABLE job_seekers ADD COLUMN IF NOT EXISTS author_id INTEGER;

-- 기존 user_id 데이터를 author_id로 복사
UPDATE job_posts SET author_id = user_id WHERE author_id IS NULL AND user_id IS NOT NULL;
UPDATE job_seekers SET author_id = user_id WHERE author_id IS NULL AND user_id IS NOT NULL;

-- author_id에 NOT NULL 제약 조건 추가
ALTER TABLE job_posts ALTER COLUMN author_id SET NOT NULL;
ALTER TABLE job_seekers ALTER COLUMN author_id SET NOT NULL;

-- 외래키 제약 조건 추가
ALTER TABLE job_posts ADD CONSTRAINT fk_job_posts_author FOREIGN KEY (author_id) REFERENCES users(id);
ALTER TABLE job_seekers ADD CONSTRAINT fk_job_seekers_author FOREIGN KEY (author_id) REFERENCES users(id);

-- 기존 user_id 컬럼 제거
ALTER TABLE job_posts DROP COLUMN IF EXISTS user_id;
ALTER TABLE job_seekers DROP COLUMN IF EXISTS user_id;

-- community_sharing, community_requests에서 중복 user_id 제거 (author_id만 유지)
ALTER TABLE community_sharing DROP COLUMN IF EXISTS user_id;
ALTER TABLE community_requests DROP COLUMN IF EXISTS user_id;

COMMIT;

SELECT '작성자 필드 표준화 완료' as status;

-- =====================================================
-- 3단계: 조회수 필드 표준화 (view_count 통일)
-- =====================================================

BEGIN;

-- views만 있는 테이블에 view_count 추가
ALTER TABLE community_music_teams ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;
ALTER TABLE music_team_seekers ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;
ALTER TABLE church_events ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0;

-- 기존 views 데이터를 view_count로 복사
UPDATE community_music_teams SET view_count = COALESCE(views, 0) WHERE view_count = 0;
UPDATE music_team_seekers SET view_count = COALESCE(views, 0) WHERE view_count = 0;
UPDATE church_events SET view_count = COALESCE(views, 0) WHERE view_count = 0;

-- 기존 views 컬럼 제거
ALTER TABLE community_music_teams DROP COLUMN IF EXISTS views;
ALTER TABLE music_team_seekers DROP COLUMN IF EXISTS views;
ALTER TABLE church_events DROP COLUMN IF EXISTS views;

-- community_sharing, community_requests에서 중복 views 제거 (view_count만 유지)
ALTER TABLE community_sharing DROP COLUMN IF EXISTS views;
ALTER TABLE community_requests DROP COLUMN IF EXISTS views;

-- job_posts, job_seekers에서 중복 views 제거 (view_count만 유지)
ALTER TABLE job_posts DROP COLUMN IF EXISTS views;
ALTER TABLE job_seekers DROP COLUMN IF EXISTS views;

COMMIT;

SELECT '조회수 필드 표준화 완료' as status;

-- =====================================================
-- 4단계: 상태 필드 ENUM을 String으로 변경
-- =====================================================

BEGIN;

-- 임시 컬럼 추가하여 ENUM → String 변환
ALTER TABLE community_sharing ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);
ALTER TABLE community_requests ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);
ALTER TABLE job_posts ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);
ALTER TABLE job_seekers ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);
ALTER TABLE community_music_teams ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);
ALTER TABLE music_team_seekers ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);
ALTER TABLE church_news ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);
ALTER TABLE church_events ADD COLUMN IF NOT EXISTS status_new VARCHAR(20);

-- 기존 ENUM 값을 소문자 문자열로 변환하여 복사
UPDATE community_sharing SET status_new = LOWER(status::text);
UPDATE community_requests SET status_new = LOWER(status::text);
UPDATE job_posts SET status_new = LOWER(status::text);
UPDATE job_seekers SET status_new = LOWER(status::text);
UPDATE community_music_teams SET status_new = LOWER(status::text);
UPDATE music_team_seekers SET status_new = LOWER(status::text);
UPDATE church_news SET status_new = LOWER(status::text);
UPDATE church_events SET status_new = LOWER(status::text);

-- 기존 status 컬럼 제거
ALTER TABLE community_sharing DROP COLUMN status;
ALTER TABLE community_requests DROP COLUMN status;
ALTER TABLE job_posts DROP COLUMN status;
ALTER TABLE job_seekers DROP COLUMN status;
ALTER TABLE community_music_teams DROP COLUMN status;
ALTER TABLE music_team_seekers DROP COLUMN status;
ALTER TABLE church_news DROP COLUMN status;
ALTER TABLE church_events DROP COLUMN status;

-- 새 컬럼을 status로 이름 변경
ALTER TABLE community_sharing RENAME COLUMN status_new TO status;
ALTER TABLE community_requests RENAME COLUMN status_new TO status;
ALTER TABLE job_posts RENAME COLUMN status_new TO status;
ALTER TABLE job_seekers RENAME COLUMN status_new TO status;
ALTER TABLE community_music_teams RENAME COLUMN status_new TO status;
ALTER TABLE music_team_seekers RENAME COLUMN status_new TO status;
ALTER TABLE church_news RENAME COLUMN status_new TO status;
ALTER TABLE church_events RENAME COLUMN status_new TO status;

-- 기본값 및 인덱스 설정
ALTER TABLE community_sharing ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE community_requests ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE job_posts ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE job_seekers ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE community_music_teams ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE music_team_seekers ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE church_news ALTER COLUMN status SET DEFAULT 'active';
ALTER TABLE church_events ALTER COLUMN status SET DEFAULT 'active';

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_community_sharing_status ON community_sharing(status);
CREATE INDEX IF NOT EXISTS idx_community_requests_status ON community_requests(status);
CREATE INDEX IF NOT EXISTS idx_job_posts_status ON job_posts(status);
CREATE INDEX IF NOT EXISTS idx_job_seekers_status ON job_seekers(status);
CREATE INDEX IF NOT EXISTS idx_community_music_teams_status ON community_music_teams(status);
CREATE INDEX IF NOT EXISTS idx_music_team_seekers_status ON music_team_seekers(status);
CREATE INDEX IF NOT EXISTS idx_church_news_status ON church_news(status);
CREATE INDEX IF NOT EXISTS idx_church_events_status ON church_events(status);

COMMIT;

SELECT '상태 필드 표준화 완료' as status;

-- =====================================================
-- 5단계: 표준화 검증 쿼리
-- =====================================================

-- 모든 테이블의 표준화된 필드 확인
SELECT 
    '=== 표준화 검증 결과 ===' as section,
    table_name,
    
    -- author_id 필드 존재 확인
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'author_id'
    ) THEN '✅' ELSE '❌' END as has_author_id,
    
    -- view_count 필드 존재 확인  
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'view_count'
    ) THEN '✅' ELSE '❌' END as has_view_count,
    
    -- status 필드가 varchar인지 확인
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = t.table_name AND column_name = 'status' AND data_type = 'character varying'
    ) THEN '✅' ELSE '❌' END as status_is_varchar

FROM (
    VALUES 
    ('community_sharing'),
    ('community_requests'), 
    ('job_posts'),
    ('job_seekers'),
    ('community_music_teams'),
    ('music_team_seekers'),
    ('church_news'),
    ('church_events')
) as t(table_name);

-- 각 테이블의 레코드 수 확인 (데이터 손실 없음을 확인)
SELECT 
    '=== 데이터 무결성 확인 ===' as section,
    'community_sharing' as table_name, COUNT(*) as record_count FROM community_sharing
UNION ALL
SELECT '', 'community_requests', COUNT(*) FROM community_requests
UNION ALL
SELECT '', 'job_posts', COUNT(*) FROM job_posts
UNION ALL
SELECT '', 'job_seekers', COUNT(*) FROM job_seekers
UNION ALL
SELECT '', 'community_music_teams', COUNT(*) FROM community_music_teams
UNION ALL
SELECT '', 'music_team_seekers', COUNT(*) FROM music_team_seekers
UNION ALL
SELECT '', 'church_news', COUNT(*) FROM church_news
UNION ALL
SELECT '', 'church_events', COUNT(*) FROM church_events;

-- =====================================================
-- 6단계: 불필요한 ENUM 타입 정리 (선택사항)
-- =====================================================

-- 사용하지 않는 ENUM 타입들을 제거할 수 있음 (주의: 다른 곳에서 사용중일 수 있음)
-- DROP TYPE IF EXISTS sharingstatus CASCADE;
-- DROP TYPE IF EXISTS requeststatus CASCADE;  
-- DROP TYPE IF EXISTS jobstatus CASCADE;
-- DROP TYPE IF EXISTS recruitmentstatus CASCADE;
-- DROP TYPE IF EXISTS seekerstatus CASCADE;
-- DROP TYPE IF EXISTS newsstatus CASCADE;
-- DROP TYPE IF EXISTS eventstatus CASCADE;

SELECT '커뮤니티 테이블 표준화 완료!' as final_status;

-- =====================================================
-- 롤백 스크립트 (문제 발생시 사용)
-- =====================================================

/*
-- 롤백이 필요한 경우 실행할 스크립트
BEGIN;

DROP TABLE IF EXISTS community_sharing;
DROP TABLE IF EXISTS community_requests;
DROP TABLE IF EXISTS job_posts;
DROP TABLE IF EXISTS job_seekers;
DROP TABLE IF EXISTS community_music_teams;
DROP TABLE IF EXISTS music_team_seekers;
DROP TABLE IF EXISTS church_news;
DROP TABLE IF EXISTS church_events;

ALTER TABLE community_sharing_backup RENAME TO community_sharing;
ALTER TABLE community_requests_backup RENAME TO community_requests;
ALTER TABLE job_posts_backup RENAME TO job_posts;
ALTER TABLE job_seekers_backup RENAME TO job_seekers;
ALTER TABLE community_music_teams_backup RENAME TO community_music_teams;
ALTER TABLE music_team_seekers_backup RENAME TO music_team_seekers;
ALTER TABLE church_news_backup RENAME TO church_news;
ALTER TABLE church_events_backup RENAME TO church_events;

COMMIT;

SELECT '롤백 완료' as status;
*/