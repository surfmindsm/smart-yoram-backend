-- PostgreSQL용 members 테이블 필드 수정/추가 스크립트
-- 기존 SQLite용 스크립트에서 PostgreSQL 호환성 문제 수정

-- 1. 누락된 필드들 추가 (존재하지 않는 경우에만)
DO $$ 
BEGIN
    -- member_type 필드 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'member_type') THEN
        ALTER TABLE members ADD COLUMN member_type VARCHAR(50);
    END IF;
    
    -- confirmation_date 필드 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'confirmation_date') THEN
        ALTER TABLE members ADD COLUMN confirmation_date DATE;
    END IF;
    
    -- sub_district 필드 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'sub_district') THEN
        ALTER TABLE members ADD COLUMN sub_district VARCHAR(50);
    END IF;
    
    -- age_group 필드 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'age_group') THEN
        ALTER TABLE members ADD COLUMN age_group VARCHAR(20);
    END IF;
    
    -- 지역구분 필드들 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'region_1') THEN
        ALTER TABLE members ADD COLUMN region_1 VARCHAR(50);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'region_2') THEN
        ALTER TABLE members ADD COLUMN region_2 VARCHAR(50);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'region_3') THEN
        ALTER TABLE members ADD COLUMN region_3 VARCHAR(50);
    END IF;
    
    -- 세 번째 인도자 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'inviter3_member_id') THEN
        ALTER TABLE members ADD COLUMN inviter3_member_id INTEGER REFERENCES members(id);
    END IF;
    
    -- 우편번호 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'postal_code') THEN
        ALTER TABLE members ADD COLUMN postal_code VARCHAR(10);
    END IF;
    
    -- 마지막 연락일 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'last_contact_date') THEN
        ALTER TABLE members ADD COLUMN last_contact_date DATE;
    END IF;
    
    -- 신급 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'spiritual_grade') THEN
        ALTER TABLE members ADD COLUMN spiritual_grade VARCHAR(20);
    END IF;
    
    -- 직업 상세 정보 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'job_category') THEN
        ALTER TABLE members ADD COLUMN job_category VARCHAR(50);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'job_detail') THEN
        ALTER TABLE members ADD COLUMN job_detail VARCHAR(100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'job_position') THEN
        ALTER TABLE members ADD COLUMN job_position VARCHAR(50);
    END IF;
    
    -- 사역 관련 정보 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'ministry_start_date') THEN
        ALTER TABLE members ADD COLUMN ministry_start_date DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'neighboring_church') THEN
        ALTER TABLE members ADD COLUMN neighboring_church VARCHAR(100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'position_decision') THEN
        ALTER TABLE members ADD COLUMN position_decision VARCHAR(100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'daily_activity') THEN
        ALTER TABLE members ADD COLUMN daily_activity TEXT;
    END IF;
    
    -- 커스텀 필드들 추가 (자유1~자유12)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_1') THEN
        ALTER TABLE members ADD COLUMN custom_field_1 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_2') THEN
        ALTER TABLE members ADD COLUMN custom_field_2 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_3') THEN
        ALTER TABLE members ADD COLUMN custom_field_3 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_4') THEN
        ALTER TABLE members ADD COLUMN custom_field_4 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_5') THEN
        ALTER TABLE members ADD COLUMN custom_field_5 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_6') THEN
        ALTER TABLE members ADD COLUMN custom_field_6 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_7') THEN
        ALTER TABLE members ADD COLUMN custom_field_7 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_8') THEN
        ALTER TABLE members ADD COLUMN custom_field_8 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_9') THEN
        ALTER TABLE members ADD COLUMN custom_field_9 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_10') THEN
        ALTER TABLE members ADD COLUMN custom_field_10 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_11') THEN
        ALTER TABLE members ADD COLUMN custom_field_11 VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'custom_field_12') THEN
        ALTER TABLE members ADD COLUMN custom_field_12 VARCHAR(200);
    END IF;
    
    -- 특별사항 추가
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'members' AND column_name = 'special_notes') THEN
        ALTER TABLE members ADD COLUMN special_notes TEXT;
    END IF;
    
END $$;

-- 2. 인덱스 추가 (존재하지 않는 경우에만)
CREATE INDEX IF NOT EXISTS ix_members_member_type ON members(member_type);
CREATE INDEX IF NOT EXISTS ix_members_confirmation_date ON members(confirmation_date);
CREATE INDEX IF NOT EXISTS ix_members_sub_district ON members(sub_district);
CREATE INDEX IF NOT EXISTS ix_members_age_group ON members(age_group);
CREATE INDEX IF NOT EXISTS ix_members_spiritual_grade ON members(spiritual_grade);
CREATE INDEX IF NOT EXISTS ix_members_job_category ON members(job_category);
CREATE INDEX IF NOT EXISTS ix_members_inviter3 ON members(inviter3_member_id);

-- 3. 교번 업데이트 (PostgreSQL 호환 방식)
-- 기존 교번과 충돌하지 않도록 안전하게 처리
DO $$
DECLARE
    max_code_num INTEGER;
    church_record RECORD;
BEGIN
    -- 각 교회별로 처리
    FOR church_record IN 
        SELECT DISTINCT church_id 
        FROM members 
        WHERE code IS NULL OR code = '' OR code = '0'
    LOOP
        -- 해당 교회의 기존 최대 교번 찾기
        SELECT COALESCE(MAX(CAST(code AS INTEGER)), 0) INTO max_code_num
        FROM members 
        WHERE church_id = church_record.church_id 
        AND code IS NOT NULL 
        AND code != '' 
        AND code ~ '^[0-9]+$';  -- 숫자로만 구성된 교번만
        
        RAISE NOTICE '교회 ID %: 기존 최대 교번 %', church_record.church_id, max_code_num;
        
        -- 해당 교회의 교번이 없는 교인들에게 순차적으로 할당
        UPDATE members 
        SET code = lpad((max_code_num + row_number() OVER (ORDER BY id))::text, 7, '0')
        WHERE church_id = church_record.church_id 
        AND (code IS NULL OR code = '' OR code = '0');
        
    END LOOP;
    
    RAISE NOTICE '교번 업데이트 완료';
END $$;

-- 4. 완료 메시지
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL용 members 테이블 필드 추가 및 교번 업데이트 완료';
END $$;