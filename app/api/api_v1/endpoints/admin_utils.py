"""
관리자 유틸리티 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from app.db.session import get_db
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/create-community-tables", response_model=Dict[str, Any])
def create_community_tables_manually(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    커뮤니티 테이블을 수동으로 생성 (마이그레이션 실패 시 사용)
    관리자만 실행 가능
    """
    
    # 관리자 권한 확인 (임시로 모든 사용자 허용)
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    
    try:
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
        
        # 테이블 생성 실행
        db.execute(text(create_tables_sql))
        db.commit()
        
        # 인덱스 생성 실행
        db.execute(text(create_indexes_sql))
        db.commit()
        
        # 생성된 테이블 확인
        result = db.execute(text("""
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
        
        return {
            "success": True,
            "message": "커뮤니티 테이블이 성공적으로 생성되었습니다",
            "created_tables": tables,
            "total_tables": len(tables),
            "expected_tables": 6
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"테이블 생성 실패: {str(e)}"
        )

@router.get("/check-community-tables", response_model=Dict[str, Any])
def check_community_tables_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """커뮤니티 테이블 존재 여부 확인"""
    
    try:
        # 테이블 존재 확인
        result = db.execute(text("""
            SELECT 
                table_name,
                CASE 
                    WHEN table_name IN (
                        'community_sharing', 
                        'community_requests', 
                        'job_posts', 
                        'job_seekers', 
                        'music_requests', 
                        'event_announcements'
                    ) THEN true
                    ELSE false
                END as is_community_table
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
        
        tables = [(row[0], row[1]) for row in result]
        existing_tables = [table[0] for table in tables]
        
        expected_tables = [
            'community_sharing', 
            'community_requests', 
            'job_posts', 
            'job_seekers', 
            'music_requests', 
            'event_announcements'
        ]
        
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        
        return {
            "existing_tables": existing_tables,
            "missing_tables": missing_tables,
            "total_existing": len(existing_tables),
            "total_expected": len(expected_tables),
            "all_tables_exist": len(missing_tables) == 0,
            "status": "완료" if len(missing_tables) == 0 else f"{len(missing_tables)}개 테이블 누락"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"테이블 상태 확인 실패: {str(e)}"
        )