#!/usr/bin/env python3
"""
커뮤니티 테이블 스키마 일관성 검증 스크립트
"""
import sys
import os

# Add the app directory to Python path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import text, inspect
from app.db.session import SessionLocal

def verify_schema_consistency():
    """스키마 일관성 검증"""
    print("🔍 커뮤니티 테이블 스키마 일관성 검증")
    
    db = SessionLocal()
    
    try:
        # 1. 표준화 결과 확인
        print("\n📊 1. 표준화 결과 확인")
        verification_query = """
        SELECT 
            table_name,
            -- author_id 또는 user_id 확인
            CASE 
                WHEN table_name IN ('community_sharing', 'community_requests') 
                    AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'user_id')
                THEN '✅ user_id'
                WHEN table_name NOT IN ('community_sharing', 'community_requests') 
                    AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'author_id')
                THEN '✅ author_id'
                ELSE '❌' 
            END as author_field,
            -- view_count 확인
            CASE WHEN EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = t.table_name AND column_name = 'view_count'
            ) THEN '✅' ELSE '❌' END as has_view_count,
            -- 중복 컬럼 제거 확인
            CASE WHEN EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = t.table_name AND column_name = 'views'
            ) THEN '❌ (should be removed)' ELSE '✅' END as views_removed
        FROM (VALUES 
            ('community_sharing'),
            ('community_requests'), 
            ('job_posts'),
            ('job_seekers'),
            ('community_music_teams'),
            ('music_team_seekers'),
            ('church_news'),
            ('church_events')
        ) as t(table_name)
        ORDER BY table_name
        """
        
        result = db.execute(text(verification_query))
        rows = result.fetchall()
        
        print("테이블명 | 작성자 필드 | view_count | views 제거")
        print("-" * 55)
        
        all_consistent = True
        for row in rows:
            table_name = row[0]
            author_field = row[1] 
            has_view_count = row[2]
            views_removed = row[3]
            
            print(f"{table_name:<20} | {author_field:<11} | {has_view_count:<10} | {views_removed}")
            
            if "❌" in [author_field, has_view_count, views_removed]:
                all_consistent = False
        
        # 2. my-posts API에서 사용하는 모든 테이블의 필수 컬럼 확인
        print("\n📊 2. my-posts API 필수 컬럼 확인")
        essential_columns_query = """
        SELECT 
            table_name,
            CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'id') THEN '✅' ELSE '❌' END as has_id,
            CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'title') THEN '✅' ELSE '❌' END as has_title,
            CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'status') THEN '✅' ELSE '❌' END as has_status,
            CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'created_at') THEN '✅' ELSE '❌' END as has_created_at,
            CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = t.table_name AND column_name = 'likes') THEN '✅' ELSE '❌' END as has_likes
        FROM (VALUES 
            ('community_sharing'),
            ('community_requests'), 
            ('job_posts'),
            ('job_seekers'),
            ('community_music_teams'),
            ('music_team_seekers'),
            ('church_news'),
            ('church_events')
        ) as t(table_name)
        ORDER BY table_name
        """
        
        result2 = db.execute(text(essential_columns_query))
        rows2 = result2.fetchall()
        
        print("테이블명 | id | title | status | created_at | likes")
        print("-" * 60)
        
        for row in rows2:
            table_name = row[0]
            has_id = row[1]
            has_title = row[2] 
            has_status = row[3]
            has_created_at = row[4]
            has_likes = row[5]
            
            print(f"{table_name:<20} | {has_id:<2} | {has_title:<5} | {has_status:<6} | {has_created_at:<10} | {has_likes}")
            
            if "❌" in [has_id, has_title, has_status, has_created_at, has_likes]:
                all_consistent = False
        
        # 3. 레코드 수 확인 (데이터 손실 검증)
        print("\n📊 3. 데이터 무결성 확인")
        data_integrity_query = """
        SELECT 
            'community_sharing' as table_name, 
            COUNT(*) as current_count,
            (SELECT COUNT(*) FROM community_sharing_backup) as backup_count
        FROM community_sharing
        UNION ALL
        SELECT 'community_requests', COUNT(*), (SELECT COUNT(*) FROM community_requests_backup)
        FROM community_requests  
        UNION ALL
        SELECT 'job_posts', COUNT(*), (SELECT COUNT(*) FROM job_posts_backup)
        FROM job_posts
        UNION ALL
        SELECT 'job_seekers', COUNT(*), (SELECT COUNT(*) FROM job_seekers_backup)
        FROM job_seekers
        """
        
        result3 = db.execute(text(data_integrity_query))
        rows3 = result3.fetchall()
        
        print("테이블명 | 현재 레코드 수 | 백업 레코드 수 | 상태")
        print("-" * 50)
        
        for row in rows3:
            table_name = row[0]
            current_count = row[1]
            backup_count = row[2]
            status = "✅ 일치" if current_count == backup_count else "❌ 불일치"
            
            print(f"{table_name:<18} | {current_count:>8} | {backup_count:>9} | {status}")
            
            if current_count != backup_count:
                all_consistent = False
        
        # 결론
        print("\n" + "="*60)
        if all_consistent:
            print("🎉 스키마 일관성 검증 완료!")
            print("✅ 모든 테이블이 표준화되었습니다.")
            print("✅ my-posts API가 안정적으로 작동할 준비가 되었습니다.")
        else:
            print("⚠️  일부 스키마 불일치가 발견되었습니다.")
            print("❌ 추가 조치가 필요할 수 있습니다.")
        
        return all_consistent
        
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    verify_schema_consistency()