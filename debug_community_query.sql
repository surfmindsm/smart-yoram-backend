-- 커뮤니티 나눔 데이터 조회 및 분석
-- 1. 전체 community_sharing 데이터 확인
SELECT 
    cs.id, cs.title, cs.user_id, cs.church_id, cs.status, cs.created_at,
    u.full_name, u.name, u.church_id as user_church_id
FROM community_sharing cs
LEFT JOIN users u ON cs.user_id = u.id
ORDER BY cs.created_at DESC;

-- 2. church_id별 데이터 분포 확인
SELECT church_id, COUNT(*) as count
FROM community_sharing 
GROUP BY church_id;

-- 3. user_id가 users 테이블에 존재하는지 확인
SELECT 
    cs.user_id,
    CASE 
        WHEN u.id IS NOT NULL THEN 'EXISTS' 
        ELSE 'NOT_FOUND' 
    END as user_exists
FROM community_sharing cs
LEFT JOIN users u ON cs.user_id = u.id;

-- 4. users 테이블에서 church_id=6인 사용자들 확인
SELECT id, name, full_name, church_id
FROM users 
WHERE church_id = 6;