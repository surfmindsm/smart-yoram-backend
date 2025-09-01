-- members 테이블에 레퍼런스 요구사항 누락 필드들 추가

-- 교인구분 추가
ALTER TABLE members ADD COLUMN member_type VARCHAR(50);

-- 입교일 추가  
ALTER TABLE members ADD COLUMN confirmation_date DATE;

-- 부구역 추가
ALTER TABLE members ADD COLUMN sub_district VARCHAR(50);

-- 나이그룹 추가
ALTER TABLE members ADD COLUMN age_group VARCHAR(20);

-- 지역구분 필드들 추가
ALTER TABLE members ADD COLUMN region_1 VARCHAR(50);
ALTER TABLE members ADD COLUMN region_2 VARCHAR(50); 
ALTER TABLE members ADD COLUMN region_3 VARCHAR(50);

-- 세 번째 인도자 추가
ALTER TABLE members ADD COLUMN inviter3_member_id INTEGER REFERENCES members(id);

-- 우편번호 추가
ALTER TABLE members ADD COLUMN postal_code VARCHAR(10);

-- 마지막 연락일 추가
ALTER TABLE members ADD COLUMN last_contact_date DATE;

-- 신급 추가
ALTER TABLE members ADD COLUMN spiritual_grade VARCHAR(20);

-- 직업 상세 정보 추가
ALTER TABLE members ADD COLUMN job_category VARCHAR(50);
ALTER TABLE members ADD COLUMN job_detail VARCHAR(100);
ALTER TABLE members ADD COLUMN job_position VARCHAR(50);

-- 사역 관련 정보 추가
ALTER TABLE members ADD COLUMN ministry_start_date DATE;
ALTER TABLE members ADD COLUMN neighboring_church VARCHAR(100);
ALTER TABLE members ADD COLUMN position_decision VARCHAR(100);
ALTER TABLE members ADD COLUMN daily_activity TEXT;

-- 커스텀 필드들 추가 (자유1~자유12)
ALTER TABLE members ADD COLUMN custom_field_1 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_2 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_3 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_4 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_5 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_6 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_7 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_8 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_9 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_10 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_11 VARCHAR(200);
ALTER TABLE members ADD COLUMN custom_field_12 VARCHAR(200);

-- 특별사항 추가 (개인 특별 사항)
ALTER TABLE members ADD COLUMN special_notes TEXT;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS ix_members_member_type ON members(member_type);
CREATE INDEX IF NOT EXISTS ix_members_confirmation_date ON members(confirmation_date);
CREATE INDEX IF NOT EXISTS ix_members_sub_district ON members(sub_district);
CREATE INDEX IF NOT EXISTS ix_members_age_group ON members(age_group);
CREATE INDEX IF NOT EXISTS ix_members_spiritual_grade ON members(spiritual_grade);
CREATE INDEX IF NOT EXISTS ix_members_job_category ON members(job_category);
CREATE INDEX IF NOT EXISTS ix_members_inviter3 ON members(inviter3_member_id);

-- 기존 교번 NULL인 교인들에게 교번 할당
UPDATE members 
SET code = printf('%07d', ROW_NUMBER() OVER (PARTITION BY church_id ORDER BY id))
WHERE code IS NULL;