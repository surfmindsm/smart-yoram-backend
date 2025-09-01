-- 현재 데이터베이스 테이블 구조 확인 SQL
-- 프로덕션 또는 로컬 DB에서 실행하여 기존 구조 파악

-- 1. 전체 테이블 목록 조회
SELECT 
    table_name,
    table_type,
    table_comment
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. members 테이블 상세 구조 확인
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'members'
ORDER BY ordinal_position;

-- 3. members 테이블의 제약조건 확인
SELECT 
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage ccu 
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_schema = 'public' 
    AND tc.table_name = 'members';

-- 4. 교인 관련 테이블들 확인
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name IN ('families', 'codes', 'member_contacts', 'member_addresses', 'member_vehicles', 'member_families')
ORDER BY table_name, ordinal_position;

-- 5. 코드성 테이블들 확인 (있다면)
SELECT 
    table_name
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name LIKE '%code%' OR table_name LIKE '%type%' OR table_name LIKE '%category%'
ORDER BY table_name;

-- 6. 인덱스 확인
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
    AND tablename = 'members';

-- 7. members 테이블 샘플 데이터 구조 확인 (상위 3개 레코드)
SELECT *
FROM members 
LIMIT 3;

-- 8. 현재 members 테이블의 컬럼 개수 및 기본 통계
SELECT 
    COUNT(*) as total_columns
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'members';

-- 9. families 테이블 구조 확인 (있다면)
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'families'
ORDER BY ordinal_position;

-- 10. 기존에 있을 수 있는 확장 테이블들 확인
SELECT 
    table_name,
    column_name
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND (table_name LIKE 'member_%' OR table_name LIKE '%member%')
    AND table_name != 'members'
ORDER BY table_name, column_name;