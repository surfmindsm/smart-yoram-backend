#!/usr/bin/env python3
"""
로컬 테스트 환경 데이터베이스 설정
production 환경의 user_id 54 '어떤이' 사용자와 동일한 데이터 구조를 로컬에 생성
"""
import sqlite3
import os
from datetime import datetime, timedelta

def create_local_test_db():
    """로컬 SQLite 테스트 DB 생성"""
    db_path = "local_test.db"
    
    # 기존 DB 파일이 있으면 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  기존 {db_path} 파일 삭제")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 테이블 생성 중...")
        
        # 1. users 테이블 (User 모델의 모든 필드 포함)
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                encrypted_password TEXT,
                full_name TEXT,
                phone TEXT,
                church_id INTEGER,
                role TEXT DEFAULT 'member',
                is_active BOOLEAN DEFAULT 1,
                is_superuser BOOLEAN DEFAULT 0,
                is_first BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. community_music_teams 테이블 (5개 게시글)
        cursor.execute("""
            CREATE TABLE community_music_teams (
                id INTEGER PRIMARY KEY,
                author_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                view_count INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
        """)
        
        # 3. church_events 테이블 (2개 게시글)
        cursor.execute("""
            CREATE TABLE church_events (
                id INTEGER PRIMARY KEY,
                author_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                view_count INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
        """)
        
        # 4. job_posts 테이블 (1개 게시글)
        cursor.execute("""
            CREATE TABLE job_posts (
                id INTEGER PRIMARY KEY,
                author_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                view_count INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
        """)
        
        # 5. music_team_seekers 테이블 (1개 게시글)
        cursor.execute("""
            CREATE TABLE music_team_seekers (
                id INTEGER PRIMARY KEY,
                author_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                view_count INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
        """)
        
        # 6. church_news 테이블 (1개 게시글)
        cursor.execute("""
            CREATE TABLE church_news (
                id INTEGER PRIMARY KEY,
                author_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                view_count INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
        """)
        
        # 7. 빈 테이블들 (0개 게시글)
        for table in ['community_sharing', 'community_requests', 'job_seekers']:
            cursor.execute(f"""
                CREATE TABLE {table} (
                    id INTEGER PRIMARY KEY,
                    author_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    view_count INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (author_id) REFERENCES users(id)
                )
            """)
        
        print("✅ 모든 테이블 생성 완료")
        
        # 데이터 삽입
        print("📝 테스트 데이터 삽입 중...")
        
        # user_id 54 '어떤이' 사용자 생성 (모든 필수 필드 포함)
        cursor.execute("""
            INSERT INTO users (id, email, username, hashed_password, full_name, church_id, is_active)
            VALUES (54, 'test1@test.com', 'test_user_54', 'dummy_hash', '어떤이', 9998, 1)
        """)
        
        # community_music_teams에 5개 게시글
        for i in range(1, 6):
            cursor.execute("""
                INSERT INTO community_music_teams (author_id, title, created_at)
                VALUES (54, ?, ?)
            """, (f"음악팀 모집 게시글 {i}", datetime.now() - timedelta(days=i)))
        
        # church_events에 2개 게시글
        for i in range(1, 3):
            cursor.execute("""
                INSERT INTO church_events (author_id, title, created_at)
                VALUES (54, ?, ?)
            """, (f"교회 행사 게시글 {i}", datetime.now() - timedelta(days=i+5)))
        
        # job_posts에 1개 게시글
        cursor.execute("""
            INSERT INTO job_posts (author_id, title, created_at)
            VALUES (54, '구인 공고 게시글', ?)
        """, (datetime.now() - timedelta(days=8),))
        
        # music_team_seekers에 1개 게시글
        cursor.execute("""
            INSERT INTO music_team_seekers (author_id, title, created_at)
            VALUES (54, '음악팀 참여 게시글', ?)
        """, (datetime.now() - timedelta(days=9),))
        
        # church_news에 1개 게시글
        cursor.execute("""
            INSERT INTO church_news (author_id, title, created_at)
            VALUES (54, '교회 소식 게시글', ?)
        """, (datetime.now() - timedelta(days=10),))
        
        conn.commit()
        print("✅ 테스트 데이터 삽입 완료")
        
        # 데이터 확인
        print("\n📊 생성된 데이터 확인:")
        
        # 사용자 확인
        cursor.execute("SELECT id, full_name, email FROM users WHERE id = 54")
        user = cursor.fetchone()
        print(f"  사용자: ID={user[0]}, 이름={user[1]}, 이메일={user[2]}")
        
        # 각 테이블별 게시글 수 확인
        tables = [
            'community_sharing', 'community_requests', 'job_posts', 'job_seekers',
            'community_music_teams', 'music_team_seekers', 'church_news', 'church_events'
        ]
        
        total_posts = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE author_id = 54")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count}개")
            total_posts += count
        
        print(f"\n🎯 총 게시글: {total_posts}개")
        print(f"📍 데이터베이스 파일: {os.path.abspath(db_path)}")
        
        return db_path
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None
        
    finally:
        conn.close()


if __name__ == "__main__":
    create_local_test_db()