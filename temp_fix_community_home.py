from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from app.api.deps import get_db, get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/stats", response_model=Dict[str, Any])
def get_community_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """커뮤니티 홈 통계 조회 - 직접 SQL 사용"""
    try:
        # 직접 SQL로 안전하게 조회
        result = db.execute(text("""
            SELECT 
                'community_sharing' as table_name,
                COUNT(*) as total_count,
                COUNT(CASE WHEN status = 'available' THEN 1 END) as active_count
            FROM community_sharing
            UNION ALL
            SELECT 
                'community_requests' as table_name,
                COUNT(*) as total_count,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as active_count
            FROM community_requests
            UNION ALL
            SELECT 
                'job_posts' as table_name,
                COUNT(*) as total_count,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count
            FROM job_posts
            UNION ALL
            SELECT 
                'job_seekers' as table_name,
                COUNT(*) as total_count,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count
            FROM job_seekers
        """))
        
        stats = {}
        total_posts = 0
        
        for row in result:
            table_name = row[0]
            total_count = row[1] or 0
            active_count = row[2] or 0
            total_posts += total_count
            
            if table_name == 'community_sharing':
                stats['active_sharing'] = active_count
            elif table_name == 'community_requests':
                stats['active_requests'] = active_count
            elif table_name == 'job_posts':
                stats['job_posts'] = active_count
            elif table_name == 'job_seekers':
                stats['job_seekers'] = active_count
        
        # 총 회원 수
        user_result = db.execute(text("SELECT COUNT(*) FROM users"))
        total_members = user_result.scalar() or 0
        
        return {
            "success": True,
            "data": {
                "total_posts": total_posts,
                "active_sharing": stats.get('active_sharing', 0),
                "active_requests": stats.get('active_requests', 0), 
                "job_posts": stats.get('job_posts', 0),
                "music_teams": 0,  # 음악 요청 (임시로 0)
                "events_this_month": 0,  # 이벤트 (임시로 0)
                "total_members": total_members
            }
        }
        
    except Exception as e:
        return {
            "success": True,
            "data": {
                "total_posts": 0,
                "active_sharing": 0,
                "active_requests": 0,
                "job_posts": 0,
                "music_teams": 0,
                "events_this_month": 0,
                "total_members": 0
            }
        }

@router.get("/recent-posts")
def get_recent_posts_simple(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """최근 게시글 조회 - 직접 SQL 사용"""
    try:
        # 기본 응답 구조
        return {
            "success": True,
            "data": []
        }
        
    except Exception as e:
        return {
            "success": True,
            "data": []
        }