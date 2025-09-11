-- 데이터베이스 테이블 구조 확인 SQL

-- 1. 모든 테이블 목록 조회 (SQLite용)
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- 2. community 관련 테이블들만 조회
SELECT name FROM sqlite_master 
WHERE type='table' AND name LIKE '%community%' 
ORDER BY name;

-- 3. community_sharing 테이블 구조 확인
PRAGMA table_info(community_sharing);

-- 4. community_images 테이블 구조 확인 (존재하는 경우)
PRAGMA table_info(community_images);

-- 5. images 관련 컬럼이 있는 테이블 찾기
-- (SQLite에서는 직접적인 방법이 없으므로 수동으로 확인)
-- community_sharing 테이블의 모든 컬럼 확인
SELECT sql FROM sqlite_master WHERE type='table' AND name='community_sharing';

-- community_images 테이블의 모든 컬럼 확인
SELECT sql FROM sqlite_master WHERE type='table' AND name='community_images';

-- 6. 실제 데이터 확인 - community_sharing
SELECT 
    id,
    title,
    description,
    church_id,
    author_id,
    created_at
FROM community_sharing 
LIMIT 5;

-- 7. 실제 데이터 확인 - community_images
SELECT 
    id,
    filename,
    file_path,
    sharing_id,
    created_at
FROM community_images 
LIMIT 5;