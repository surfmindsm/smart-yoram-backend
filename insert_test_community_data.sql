-- community_sharing 테스트 데이터 삽입
INSERT INTO community_sharing (
    church_id, user_id, title, description, category, 
    condition, price, is_free, location, contact_info, 
    images, status, view_count, created_at
) VALUES 
(6, 54, '테스트 책상 나눔', '사용하지 않는 책상을 나눔합니다', '가구', 
 'good', 0, true, '서울', 'test@example.com', 
 '[]'::json, 'available', 0, NOW()),

(6, 54, '의자 무료 나눔', '의자 2개 나눔합니다', '가구',
 'good', 0, true, '부산', 'contact@test.com',
 '[]'::json, 'available', 5, NOW() - INTERVAL '1 day');

-- 데이터 확인
SELECT id, title, user_id, church_id, status, created_at 
FROM community_sharing 
ORDER BY created_at DESC;