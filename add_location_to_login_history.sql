-- 프로덕션 PostgreSQL: login_history 테이블에 location 컬럼 추가

-- 1. 현재 테이블 구조 확인
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'login_history'
ORDER BY ordinal_position;
 
-- 2. location 컬럼이 없다면 추가
DO $$
BEGIN
    -- location 컬럼 존재 여부 확인
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'login_history' 
        AND column_name = 'location'
    ) THEN
        -- location 컬럼 추가
        ALTER TABLE login_history 
        ADD COLUMN location VARCHAR(200);
        
        RAISE NOTICE '✅ location 컬럼이 추가되었습니다.';
    ELSE
        RAISE NOTICE '⚠️ location 컬럼이 이미 존재합니다.';
    END IF;
END $$;

-- 3. 업데이트된 테이블 구조 확인
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'login_history'
ORDER BY ordinal_position;

-- 4. 기존 데이터에 기본값 설정 (선택사항)
-- UPDATE login_history 
-- SET location = '위치 정보 없음' 
-- WHERE location IS NULL;

-- 완료 메시지
SELECT '✅ login_history 테이블에 location 필드 추가 완료!' as result;