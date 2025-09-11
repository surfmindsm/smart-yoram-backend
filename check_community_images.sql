-- 커뮤니티 이미지 URL 확인 SQL
-- 특정 이미지 URL들이 데이터베이스에 저장되어 있는지 확인

-- 1. 정확한 URL로 검색
SELECT 
    id,
    church_id,
    title,
    content,
    images,
    created_at,
    updated_at
FROM community_sharing 
WHERE images::text LIKE '%community_9998_20250910_143039_23c50355.png%'
   OR images::text LIKE '%community_9998_20250910_143039_41925038.png%';

-- 2. JSON 배열에서 해당 URL들이 포함된 레코드 찾기
SELECT 
    id,
    church_id,
    title,
    content,
    images,
    created_at
FROM community_sharing 
WHERE images @> '["https://api.surfmind-team.com/static/community/images/community_9998_20250910_143039_23c50355.png"]'
   OR images @> '["https://api.surfmind-team.com/static/community/images/community_9998_20250910_143039_41925038.png"]';

-- 3. 해당 이미지들을 포함한 모든 커뮤니티 글 상세 조회
WITH image_posts AS (
    SELECT 
        cs.id,
        cs.church_id,
        cs.title,
        cs.content,
        cs.images,
        cs.created_at,
        cs.updated_at,
        u.email as author_email,
        c.church_name
    FROM community_sharing cs
    LEFT JOIN users u ON cs.user_id = u.id
    LEFT JOIN churches c ON cs.church_id = c.id
    WHERE cs.images::text LIKE '%community_9998_20250910_143039_%'
)
SELECT * FROM image_posts
ORDER BY created_at DESC;

-- 4. church_id = 9998인 모든 커뮤니티 이미지 확인
SELECT 
    id,
    title,
    images,
    created_at
FROM community_sharing 
WHERE church_id = 9998
  AND images IS NOT NULL 
  AND json_array_length(images) > 0
ORDER BY created_at DESC;

-- 5. 해당 날짜(2025-09-10)에 업로드된 이미지들 확인
SELECT 
    id,
    church_id,
    title,
    images,
    created_at
FROM community_sharing 
WHERE images::text LIKE '%20250910%'
ORDER BY created_at DESC;