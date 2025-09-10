#!/usr/bin/env python3
"""
커뮤니티 테이블 수동 생성 유틸리티
마이그레이션이 실행되지 않을 때 사용
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

def create_community_tables():
    """커뮤니티 테이블들을 직접 생성"""
    
    engine = create_engine(DATABASE_URL)
    
    # 테이블 생성 SQL
    create_tables_sql = """
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
    """
    
    # 인덱스 생성 SQL
    create_indexes_sql = """
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
    """
    
    try:
        with engine.connect() as conn:
            print("🔄 커뮤니티 테이블 생성 중...")
            
            # SQL 문을 개별적으로 실행
            sql_statements = [
                # 1. 커뮤니티 나눔 테이블
                """CREATE TABLE IF NOT EXISTS community_sharing (
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
                )""",
                
                # 2. 커뮤니티 도움 요청 테이블
                """CREATE TABLE IF NOT EXISTS community_requests (
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
                )""",
                
                # 3. 구인 공고 테이블
                """CREATE TABLE IF NOT EXISTS job_posts (
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
                )""",
                
                # 4. 구직 정보 테이블
                """CREATE TABLE IF NOT EXISTS job_seekers (
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
                )""",
                
                # 5. 음악 요청 테이블
                """CREATE TABLE IF NOT EXISTS music_requests (
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
                )""",
                
                # 6. 이벤트 공지 테이블
                """CREATE TABLE IF NOT EXISTS event_announcements (
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
                )"""
            ]
            
            # 각 테이블을 개별적으로 생성
            for i, sql in enumerate(sql_statements, 1):
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    table_names = ["community_sharing", "community_requests", "job_posts", "job_seekers", "music_requests", "event_announcements"]
                    print(f"✅ {table_names[i-1]} 테이블 생성 완료")
                except Exception as e:
                    print(f"⚠️ 테이블 {i} 생성 중 오류 (이미 존재할 수 있음): {e}")
            
            # 인덱스 생성
            index_statements = [
                "CREATE INDEX IF NOT EXISTS idx_community_sharing_church_id ON community_sharing(church_id)",
                "CREATE INDEX IF NOT EXISTS idx_community_sharing_status ON community_sharing(status)",
                "CREATE INDEX IF NOT EXISTS idx_community_sharing_category ON community_sharing(category)",
                "CREATE INDEX IF NOT EXISTS idx_community_requests_church_id ON community_requests(church_id)",
                "CREATE INDEX IF NOT EXISTS idx_community_requests_status ON community_requests(status)",
                "CREATE INDEX IF NOT EXISTS idx_community_requests_category ON community_requests(category)",
                "CREATE INDEX IF NOT EXISTS idx_job_posts_church_id ON job_posts(church_id)",
                "CREATE INDEX IF NOT EXISTS idx_job_posts_status ON job_posts(status)",
                "CREATE INDEX IF NOT EXISTS idx_job_posts_job_type ON job_posts(job_type)",
                "CREATE INDEX IF NOT EXISTS idx_job_seekers_church_id ON job_seekers(church_id)",
                "CREATE INDEX IF NOT EXISTS idx_job_seekers_status ON job_seekers(status)",
                "CREATE INDEX IF NOT EXISTS idx_music_requests_church_id ON music_requests(church_id)",
                "CREATE INDEX IF NOT EXISTS idx_music_requests_status ON music_requests(status)",
                "CREATE INDEX IF NOT EXISTS idx_event_announcements_church_id ON event_announcements(church_id)",
                "CREATE INDEX IF NOT EXISTS idx_event_announcements_status ON event_announcements(status)",
                "CREATE INDEX IF NOT EXISTS idx_event_announcements_event_date ON event_announcements(event_date)"
            ]
            
            for idx_sql in index_statements:
                try:
                    conn.execute(text(idx_sql))
                    conn.commit()
                except Exception as e:
                    print(f"⚠️ 인덱스 생성 중 오류 (이미 존재할 수 있음): {e}")
            
            print("✅ 인덱스 생성 완료")
            
            # 생성된 테이블 확인
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                    AND table_name IN (
                        'community_sharing', 
                        'community_requests', 
                        'job_posts', 
                        'job_seekers', 
                        'music_requests', 
                        'event_announcements'
                    )
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            print(f"✅ 생성된 테이블: {', '.join(tables)}")
            
            if len(tables) == 6:
                print("🎉 모든 커뮤니티 테이블이 성공적으로 생성되었습니다!")
            else:
                print(f"⚠️ 일부 테이블만 생성됨: {len(tables)}/6")
                
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🚀 커뮤니티 테이블 수동 생성 시작...")
    
    if create_community_tables():
        print("✅ 작업 완료! 이제 프론트엔드에서 커뮤니티 기능을 사용할 수 있습니다.")
    else:
        print("❌ 작업 실패")
        sys.exit(1)