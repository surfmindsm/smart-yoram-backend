-- PostgreSQL 데이터베이스 테이블 구조 확인 SQL

-- 1. 모든 테이블 목록 조회
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. community 관련 테이블들만 조회
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE '%community%'
ORDER BY table_name;

-- 3. community_sharing 테이블 구조 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'community_sharing'
ORDER BY ordinal_position;

-- 4. community_images 테이블 구조 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'community_images'
ORDER BY ordinal_position;

-- 5. 특정 이미지 URL이 저장된 레코드 찾기 (community_images에서)
SELECT 
    ci.id,
    ci.filename,
    ci.file_path,
    ci.sharing_id,
    ci.created_at,
    cs.title,
    cs.church_id
FROM community_images ci
LEFT JOIN community_sharing cs ON ci.sharing_id = cs.id
WHERE ci.filename LIKE '%community_9998_20250910_143039_%'
   OR ci.file_path LIKE '%community_9998_20250910_143039_%'
ORDER BY ci.created_at DESC;

-- 6. church_id = 9998인 커뮤니티 공유글과 연결된 이미지들
SELECT 
    cs.id as sharing_id,
    cs.title,
    cs.church_id,
    cs.created_at,
    ci.id as image_id,
    ci.filename,
    ci.file_path
FROM community_sharing cs
LEFT JOIN community_images ci ON cs.id = ci.sharing_id
WHERE cs.church_id = 9998
ORDER BY cs.created_at DESC
LIMIT 10;

-- 7. 최근 업로드된 community_images 확인
SELECT 
    id,
    filename,
    file_path,
    sharing_id,
    created_at
FROM community_images
ORDER BY created_at DESC
LIMIT 10;