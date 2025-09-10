-- 커뮤니티 플랫폼 테이블 존재 여부 확인 SQL
-- 이 쿼리들을 실행해서 테이블이 실제로 생성되었는지 확인하세요

-- 1. 모든 커뮤니티 관련 테이블 존재 여부 확인
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'community_sharing',
    'community_requests', 
    'job_posts',
    'job_seekers',
    'music_team_recruits',
    'music_team_applications',
    'church_events'
)
ORDER BY table_name;

-- 2. 각 테이블의 컬럼 구조 확인 (테이블이 존재할 경우)
-- community_sharing 테이블 구조
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'community_sharing'
ORDER BY ordinal_position;

-- community_requests 테이블 구조
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'community_requests'
ORDER BY ordinal_position;

-- job_posts 테이블 구조
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'job_posts'
ORDER BY ordinal_position;

-- job_seekers 테이블 구조
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'job_seekers'
ORDER BY ordinal_position;

-- 3. 실제 마이그레이션 실행 여부 확인
-- alembic_version 테이블에서 최신 마이그레이션 확인
SELECT version_num 
FROM alembic_version;

-- 4. 테이블이 없다면 실행해야 할 마이그레이션 명령어
-- alembic upgrade head

-- 5. 간단한 데이터 확인 (테이블이 존재할 경우)
-- SELECT COUNT(*) FROM community_sharing;
-- SELECT COUNT(*) FROM community_requests;
-- SELECT COUNT(*) FROM job_posts;
-- SELECT COUNT(*) FROM job_seekers;