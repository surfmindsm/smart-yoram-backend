-- 커뮤니티 회원 신청 시스템 테이블 생성
-- PostgreSQL용 (프로덕션) & SQLite용 (로컬) 호환

-- 1. 신청자 유형 ENUM (PostgreSQL용)
-- SQLite에서는 CHECK 제약조건으로 대체됨

-- 2. 메인 테이블 생성
CREATE TABLE IF NOT EXISTS community_applications (
    id SERIAL PRIMARY KEY,  -- PostgreSQL: SERIAL, SQLite: INTEGER PRIMARY KEY AUTOINCREMENT
    
    -- 신청자 정보
    applicant_type VARCHAR(20) NOT NULL CHECK (applicant_type IN ('company', 'individual', 'musician', 'minister', 'organization', 'other')),
    organization_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    business_number VARCHAR(50),
    address TEXT,
    description TEXT NOT NULL,
    service_area VARCHAR(200),
    website VARCHAR(500),
    
    -- 첨부파일 정보 (JSON)
    attachments JSON,  -- PostgreSQL: JSON, SQLite: TEXT
    
    -- 신청 상태
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by INTEGER,
    rejection_reason TEXT,
    notes TEXT,
    
    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 외래키 (users 테이블의 reviewer)
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);

-- 3. 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_community_applications_status ON community_applications(status);
CREATE INDEX IF NOT EXISTS idx_community_applications_submitted_at ON community_applications(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_community_applications_applicant_type ON community_applications(applicant_type);
CREATE INDEX IF NOT EXISTS idx_community_applications_email ON community_applications(email);
CREATE INDEX IF NOT EXISTS idx_community_applications_organization ON community_applications(organization_name);

-- 4. 이메일 중복 방지를 위한 부분 유니크 인덱스
-- (승인된 신청서들 간에만 이메일 중복 방지)
CREATE UNIQUE INDEX IF NOT EXISTS idx_community_applications_email_approved 
ON community_applications(email) 
WHERE status = 'approved';

-- 5. 테이블 생성 확인
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'community_applications'
ORDER BY ordinal_position;

-- SQLite용 확인 쿼리 (위가 실패할 경우)
-- PRAGMA table_info(community_applications);

-- 완료 메시지
SELECT '✅ community_applications 테이블 생성 완료!' as result;