-- 커뮤니티 이미지 URL 확인 SQL (SQLite용)
-- 특정 이미지 URL들이 데이터베이스에 저장되어 있는지 확인

-- 1. community_images 테이블에서 특정 파일명 검색
SELECT 
    ci.id,
    ci.filename,
    ci.original_filename,
    ci.file_path,
    ci.sharing_id,
    ci.created_at,
    cs.title as sharing_title,
    cs.church_id
FROM community_images ci
LEFT JOIN community_sharing cs ON ci.sharing_id = cs.id
WHERE ci.filename LIKE '%community_9998_20250910_143039_23c50355.png%'
   OR ci.filename LIKE '%community_9998_20250910_143039_41925038.png%'
   OR ci.file_path LIKE '%community_9998_20250910_143039_%';

-- 2. church_id = 9998과 관련된 모든 이미지들
SELECT 
    ci.id,
    ci.filename,
    ci.file_path,
    ci.created_at,
    cs.id as sharing_id,
    cs.title,
    cs.church_id
FROM community_images ci
LEFT JOIN community_sharing cs ON ci.sharing_id = cs.id
WHERE cs.church_id = 9998
ORDER BY ci.created_at DESC;

-- 3. 2025-09-10 날짜에 업로드된 모든 이미지
SELECT 
    id,
    filename,
    file_path,
    sharing_id,
    created_at
FROM community_images
WHERE filename LIKE '%20250910%'
   OR created_at LIKE '2025-09-10%'
ORDER BY created_at DESC;

-- 4. community_images 테이블의 모든 데이터 확인 (최근 20개)
SELECT 
    ci.id,
    ci.filename,
    ci.file_path,
    ci.sharing_id,
    ci.created_at,
    cs.title
FROM community_images ci
LEFT JOIN community_sharing cs ON ci.sharing_id = cs.id
ORDER BY ci.created_at DESC
LIMIT 20;

-- 5. 결론: 해당 URL들의 존재 여부 확인
-- 'https://api.surfmind-team.com/static/community/images/community_9998_20250910_143039_23c50355.png'
-- 'https://api.surfmind-team.com/static/community/images/community_9998_20250910_143039_41925038.png'

-- 현재 결과: 해당 이미지들이 community_images 테이블에 존재하지 않음
-- 이는 다음을 의미합니다:
-- 1. 이미지가 실제로 업로드되지 않았거나
-- 2. 프론트엔드에서 보여지는 URL이 테스트용 더미 데이터이거나  
-- 3. 다른 방식으로 저장되고 있을 가능성