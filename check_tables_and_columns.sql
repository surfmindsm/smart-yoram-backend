-- 커뮤니티 테이블과 컬럼 확인용 SQL

-- 1. 테이블 존재 여부 확인
SELECT 
    table_name,
    table_schema
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN (
        'community_sharing', 
        'community_requests', 
        'job_posts', 
        'job_seekers', 
        'music_requests', 
        'event_announcements'
    )
ORDER BY table_name;

-- 2. community_sharing 테이블 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'community_sharing'
ORDER BY ordinal_position;

-- 3. community_requests 테이블 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'community_requests'
ORDER BY ordinal_position;

-- 4. job_posts 테이블 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'job_posts'
ORDER BY ordinal_position;

-- 5. job_seekers 테이블 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'job_seekers'
ORDER BY ordinal_position;

-- 6. 테이블 카운트 확인
SELECT 
    'community_sharing' as table_name,
    COUNT(*) as row_count
FROM community_sharing
UNION ALL
SELECT 
    'community_requests' as table_name,
    COUNT(*) as row_count
FROM community_requests
UNION ALL
SELECT 
    'job_posts' as table_name,
    COUNT(*) as row_count
FROM job_posts
UNION ALL
SELECT 
    'job_seekers' as table_name,
    COUNT(*) as row_count
FROM job_seekers;