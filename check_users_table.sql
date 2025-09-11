-- users 테이블의 실제 구조 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- users 테이블 샘플 데이터 확인
SELECT * FROM users WHERE church_id = 6 LIMIT 3;