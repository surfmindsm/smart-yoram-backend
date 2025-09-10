-- 커뮤니티 플랫폼 테이블 수동 생성 SQL
-- 마이그레이션이 실행되지 않을 경우 직접 실행용

-- 1. 커뮤니티 나눔 테이블
CREATE TABLE IF NOT EXISTS community_sharing (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL DEFAULT 9998,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    condition VARCHAR(20) DEFAULT 'good',
    price DECIMAL(10,2) DEFAULT 0,
    is_free BOOLEAN DEFAULT true,
    location VARCHAR(200),
    contact_info VARCHAR(500),
    images JSON,
    status VARCHAR(20) DEFAULT 'available',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 2. 커뮤니티 도움 요청 테이블
CREATE TABLE IF NOT EXISTS community_requests (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL DEFAULT 9998,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    urgency VARCHAR(20) DEFAULT 'normal',
    location VARCHAR(200),
    contact_info VARCHAR(500),
    reward_type VARCHAR(20) DEFAULT 'none',
    reward_amount DECIMAL(10,2),
    images JSON,
    status VARCHAR(20) DEFAULT 'open',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 3. 구인 공고 테이블
CREATE TABLE IF NOT EXISTS job_posts (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL DEFAULT 9998,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    company_name VARCHAR(200),
    job_type VARCHAR(50),
    employment_type VARCHAR(50),
    location VARCHAR(200),
    salary_range VARCHAR(100),
    requirements TEXT,
    contact_info VARCHAR(500),
    application_deadline DATE,
    status VARCHAR(20) DEFAULT 'active',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. 구직 정보 테이블
CREATE TABLE IF NOT EXISTS job_seekers (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL DEFAULT 9998,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    desired_position VARCHAR(200),
    experience_years INTEGER,
    desired_location VARCHAR(200),
    desired_salary_range VARCHAR(100),
    skills TEXT,
    education VARCHAR(200),
    contact_info VARCHAR(500),
    resume_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 5. 음악 요청 테이블
CREATE TABLE IF NOT EXISTS music_requests (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL DEFAULT 9998,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    music_type VARCHAR(50),
    occasion VARCHAR(100),
    preferred_date DATE,
    location VARCHAR(200),
    contact_info VARCHAR(500),
    status VARCHAR(20) DEFAULT 'open',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 6. 이벤트 공지 테이블
CREATE TABLE IF NOT EXISTS event_announcements (
    id SERIAL PRIMARY KEY,
    church_id INTEGER NOT NULL DEFAULT 9998,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50),
    event_date TIMESTAMP WITH TIME ZONE,
    location VARCHAR(200),
    max_participants INTEGER,
    registration_required BOOLEAN DEFAULT false,
    contact_info VARCHAR(500),
    images JSON,
    status VARCHAR(20) DEFAULT 'active',
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_community_sharing_church_id ON community_sharing(church_id);
CREATE INDEX IF NOT EXISTS idx_community_sharing_status ON community_sharing(status);
CREATE INDEX IF NOT EXISTS idx_community_sharing_category ON community_sharing(category);

CREATE INDEX IF NOT EXISTS idx_community_requests_church_id ON community_requests(church_id);
CREATE INDEX IF NOT EXISTS idx_community_requests_status ON community_requests(status);
CREATE INDEX IF NOT EXISTS idx_community_requests_category ON community_requests(category);

CREATE INDEX IF NOT EXISTS idx_job_posts_church_id ON job_posts(church_id);
CREATE INDEX IF NOT EXISTS idx_job_posts_status ON job_posts(status);
CREATE INDEX IF NOT EXISTS idx_job_posts_job_type ON job_posts(job_type);

CREATE INDEX IF NOT EXISTS idx_job_seekers_church_id ON job_seekers(church_id);
CREATE INDEX IF NOT EXISTS idx_job_seekers_status ON job_seekers(status);

CREATE INDEX IF NOT EXISTS idx_music_requests_church_id ON music_requests(church_id);
CREATE INDEX IF NOT EXISTS idx_music_requests_status ON music_requests(status);

CREATE INDEX IF NOT EXISTS idx_event_announcements_church_id ON event_announcements(church_id);
CREATE INDEX IF NOT EXISTS idx_event_announcements_status ON event_announcements(status);
CREATE INDEX IF NOT EXISTS idx_event_announcements_event_date ON event_announcements(event_date);

-- 마이그레이션 버전 업데이트 (community_platform_001이 적용되었다고 기록)
-- 주의: 이미 다른 버전이 적용되어 있다면 실행하지 마세요
-- UPDATE alembic_version SET version_num = 'community_platform_001';

SELECT 'Community tables created successfully! 🎉' as result;