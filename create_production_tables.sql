-- PostgreSQL용 시스템 공지사항 테이블 생성
-- 프로덕션 데이터베이스에서 실행

-- 1. system_announcements 테이블 생성
CREATE TABLE IF NOT EXISTS system_announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL DEFAULT 'normal',
    start_date DATE NOT NULL,
    end_date DATE,
    target_churches TEXT,
    is_active BOOLEAN DEFAULT true,
    is_pinned BOOLEAN DEFAULT false,
    created_by INTEGER NOT NULL,
    author_name VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_system_announcements_created_by FOREIGN KEY (created_by) REFERENCES users (id),
    CONSTRAINT check_system_priority CHECK (priority IN ('urgent', 'important', 'normal'))
);

-- 2. system_announcement_reads 테이블 생성
CREATE TABLE IF NOT EXISTS system_announcement_reads (
    id SERIAL PRIMARY KEY,
    system_announcement_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    church_id INTEGER NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_system_announcement_reads_announcement FOREIGN KEY (system_announcement_id) REFERENCES system_announcements (id) ON DELETE CASCADE,
    CONSTRAINT fk_system_announcement_reads_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_system_announcement_reads_church FOREIGN KEY (church_id) REFERENCES churches (id) ON DELETE CASCADE,
    CONSTRAINT unique_system_announcement_read UNIQUE (system_announcement_id, user_id, church_id)
);

-- 3. 인덱스 생성
CREATE INDEX IF NOT EXISTS ix_system_announcements_start_date ON system_announcements (start_date);
CREATE INDEX IF NOT EXISTS ix_system_announcements_priority ON system_announcements (priority);
CREATE INDEX IF NOT EXISTS ix_system_announcements_is_active ON system_announcements (is_active);
CREATE INDEX IF NOT EXISTS ix_system_announcements_created_by ON system_announcements (created_by);
CREATE INDEX IF NOT EXISTS ix_system_announcement_reads_user ON system_announcement_reads (user_id);
CREATE INDEX IF NOT EXISTS ix_system_announcement_reads_church ON system_announcement_reads (church_id);
CREATE INDEX IF NOT EXISTS ix_system_announcement_reads_announcement ON system_announcement_reads (system_announcement_id);

-- 4. 테스트용 시스템 공지사항 생성
INSERT INTO system_announcements (
    title, 
    content, 
    priority, 
    start_date, 
    end_date, 
    is_active, 
    is_pinned, 
    created_by, 
    author_name
) VALUES (
    '시스템 공지사항 기능 출시',
    '새로운 시스템 공지사항 기능이 출시되었습니다. 시스템 관리자는 모든 교회에 공지사항을 전달할 수 있습니다.',
    'important',
    '2025-09-01',
    '2025-09-30',
    true,
    true,
    30, -- system_superadmin의 user_id
    '시스템 최고관리자'
) ON CONFLICT DO NOTHING;

-- 5. 테이블 생성 확인
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_name IN ('system_announcements', 'system_announcement_reads')
AND table_schema = 'public';

-- 6. 생성된 테스트 데이터 확인
SELECT 
    id, 
    title, 
    priority, 
    start_date, 
    end_date, 
    is_active,
    created_by,
    author_name
FROM system_announcements 
LIMIT 5;