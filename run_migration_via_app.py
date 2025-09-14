#!/usr/bin/env python3
"""
애플리케이션 DB 세션을 통한 커뮤니티 테이블 표준화 마이그레이션
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import text
from app.db.session import SessionLocal

def run_migration_commands():
    """개별 마이그레이션 명령어들을 단계별로 실행"""
    
    db = SessionLocal()
    
    try:
        print("🔄 1단계: 백업 테이블 생성")
        
        backup_commands = [
            "CREATE TABLE IF NOT EXISTS community_sharing_backup AS SELECT * FROM community_sharing",
            "CREATE TABLE IF NOT EXISTS community_requests_backup AS SELECT * FROM community_requests", 
            "CREATE TABLE IF NOT EXISTS job_posts_backup AS SELECT * FROM job_posts",
            "CREATE TABLE IF NOT EXISTS job_seekers_backup AS SELECT * FROM job_seekers",
            "CREATE TABLE IF NOT EXISTS community_music_teams_backup AS SELECT * FROM community_music_teams",
            "CREATE TABLE IF NOT EXISTS music_team_seekers_backup AS SELECT * FROM music_team_seekers",
            "CREATE TABLE IF NOT EXISTS church_news_backup AS SELECT * FROM church_news",
            "CREATE TABLE IF NOT EXISTS church_events_backup AS SELECT * FROM church_events"
        ]
        
        for cmd in backup_commands:
            try:
                db.execute(text(cmd))
                db.commit()
                print(f"✅ {cmd.split()[5]} 백업 완료")
            except Exception as e:
                print(f"⚠️  {cmd.split()[5]} 백업 건너뜀: {e}")
        
        print("\n🔄 2단계: 작성자 필드 표준화")
        
        # job_posts와 job_seekers에 author_id 추가
        author_commands = [
            "ALTER TABLE job_posts ADD COLUMN IF NOT EXISTS author_id INTEGER",
            "ALTER TABLE job_seekers ADD COLUMN IF NOT EXISTS author_id INTEGER", 
            "UPDATE job_posts SET author_id = user_id WHERE author_id IS NULL AND user_id IS NOT NULL",
            "UPDATE job_seekers SET author_id = user_id WHERE author_id IS NULL AND user_id IS NOT NULL",
            "ALTER TABLE job_posts DROP COLUMN IF EXISTS user_id",
            "ALTER TABLE job_seekers DROP COLUMN IF EXISTS user_id",
            "ALTER TABLE community_sharing DROP COLUMN IF EXISTS user_id", 
            "ALTER TABLE community_requests DROP COLUMN IF EXISTS user_id"
        ]
        
        for cmd in author_commands:
            try:
                db.execute(text(cmd))
                db.commit()
                print(f"✅ 작성자 필드 명령 완료: {cmd[:50]}...")
            except Exception as e:
                print(f"⚠️  작성자 필드 명령 건너뜀: {e}")
        
        print("\n🔄 3단계: 조회수 필드 표준화")
        
        view_commands = [
            "ALTER TABLE community_music_teams ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0",
            "ALTER TABLE music_team_seekers ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0", 
            "ALTER TABLE church_events ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0",
            "UPDATE community_music_teams SET view_count = COALESCE(views, 0) WHERE view_count = 0",
            "UPDATE music_team_seekers SET view_count = COALESCE(views, 0) WHERE view_count = 0",
            "UPDATE church_events SET view_count = COALESCE(views, 0) WHERE view_count = 0",
            "ALTER TABLE community_music_teams DROP COLUMN IF EXISTS views",
            "ALTER TABLE music_team_seekers DROP COLUMN IF EXISTS views", 
            "ALTER TABLE church_events DROP COLUMN IF EXISTS views",
            "ALTER TABLE community_sharing DROP COLUMN IF EXISTS views",
            "ALTER TABLE community_requests DROP COLUMN IF EXISTS views",
            "ALTER TABLE job_posts DROP COLUMN IF EXISTS views",
            "ALTER TABLE job_seekers DROP COLUMN IF EXISTS views"
        ]
        
        for cmd in view_commands:
            try:
                db.execute(text(cmd))
                db.commit()
                print(f"✅ 조회수 필드 명령 완료: {cmd[:50]}...")
            except Exception as e:
                print(f"⚠️  조회수 필드 명령 건너뜀: {e}")
        
        print("\n🔄 4단계: 검증")
        
        # 표준화 결과 확인
        verification_query = """
        SELECT 
            table_name,
            CASE WHEN EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = t.table_name AND column_name = 'author_id'
            ) THEN '✅' ELSE '❌' END as has_author_id,
            CASE WHEN EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = t.table_name AND column_name = 'view_count'
            ) THEN '✅' ELSE '❌' END as has_view_count
        FROM (
            VALUES 
            ('community_sharing'),
            ('community_requests'), 
            ('job_posts'),
            ('job_seekers'),
            ('community_music_teams'),
            ('music_team_seekers'),
            ('church_news'),
            ('church_events')
        ) as t(table_name)
        """
        
        result = db.execute(text(verification_query))
        rows = result.fetchall()
        
        print("\n📊 표준화 검증 결과:")
        print("테이블명 | author_id | view_count")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]:<20} | {row[1]:<9} | {row[2]}")
        
        print("\n✅ 마이그레이션 완료!")
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_migration_commands()