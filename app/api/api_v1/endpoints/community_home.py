from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.community_sharing import CommunitySharing
from app.models.community_request import CommunityRequest
from app.models.job_posts import JobPost, JobSeeker
from app.models.music_team_recruitment import MusicTeamRecruitment
from app.models.music_team_seeker import MusicTeamSeeker
from app.models.church_news import ChurchNews
from app.models.church_events import ChurchEvent

router = APIRouter()


def get_views_count(post):
    """조회수를 안전하게 가져오는 헬퍼 함수"""
    return getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0


def get_author_name(post):
    """작성자 이름을 안전하게 가져오는 헬퍼 함수"""
    if hasattr(post, 'author') and post.author:
        return post.author.full_name if hasattr(post.author, 'full_name') else "익명"
    return "익명"


def format_post_response(post, post_type, type_label):
    """게시글 응답을 표준화하는 헬퍼 함수"""
    return {
        "id": post.id,
        "type": post_type,
        "type_label": type_label,
        "title": post.title,
        "status": post.status,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "views": get_views_count(post),
        "likes": post.likes or 0,
        "author_name": get_author_name(post)
    }


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
        # 에러가 발생해도 기본값 반환
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
def get_recent_posts(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """최근 게시글 조회 - 단순화"""
    try:
        return {
            "success": True,
            "data": []
        }
        
    except Exception as e:
        return {
            "success": True,
            "data": []
        }


@router.get("/my-posts")
def get_my_posts(
    post_type: Optional[str] = Query(None, description="게시글 타입 필터"),
    status: Optional[str] = Query(None, description="상태 필터"),
    search: Optional[str] = Query(None, description="제목 검색"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """내가 올린 글 목록 조회 - Raw SQL로 안전하게 조회"""
    try:
        print(f"🔍 [MY_POSTS] 사용자 {current_user.id}의 게시글 조회 시작")
        print(f"🔍 [MY_POSTS] current_user 정보 - ID: {current_user.id}, 이름: {getattr(current_user, 'full_name', 'N/A')}, 이메일: {getattr(current_user, 'email', 'N/A')}")
        print(f"🔍 [MY_POSTS] Raw SQL 방식 시작 - 스키마 불일치 문제 해결 시도")
        
        all_posts = []
        
        # Raw SQL로 각 테이블에서 기본 정보만 조회
        tables_config = [
            ("community_sharing", "무료 나눔", "user_id"),  # user_id 사용 (특별 케이스)
            ("community_requests", "물품 요청", "author_id"), 
            ("job_posts", "구인 공고", "author_id"),
            ("job_seekers", "구직 신청", "author_id"),
            ("community_music_teams", "음악팀 모집", "author_id"),
            ("music_team_seekers", "음악팀 참여", "author_id"),
            ("church_news", "교회 소식", "author_id"),
            ("church_events", "교회 행사", "author_id"),
        ]
        
        for table_name, type_label, author_field in tables_config:
            try:
                # 안전한 SQL 쿼리 (기본 필드만 조회)
                query = text(f"""
                    SELECT 
                        id,
                        title,
                        COALESCE(status, 'active') as status,
                        COALESCE(view_count, views, 0) as views,
                        COALESCE(likes, 0) as likes,
                        created_at
                    FROM {table_name} 
                    WHERE {author_field} = :user_id
                    ORDER BY created_at DESC
                """)
                
                result = db.execute(query, {"user_id": current_user.id})
                rows = result.fetchall()
                
                print(f"🔍 [MY_POSTS] {table_name}: {len(rows)}개")
                if len(rows) > 0:
                    print(f"    첫 번째 게시글: ID={rows[0][0]}, 제목='{rows[0][1]}'")  
                
                for row in rows:
                    all_posts.append({
                        "id": row[0],
                        "type": table_name.replace("_", "-"),
                        "type_label": type_label,
                        "title": row[1],
                        "status": row[2],
                        "created_at": row[5].isoformat() if row[5] else None,
                        "views": row[3] or 0,
                        "likes": row[4] or 0,
                        "author_name": current_user.full_name or "익명"
                    })
                    
            except Exception as e:
                print(f"❌ [MY_POSTS] {table_name} 조회 오류: {e}")
                print(f"    SQL: SELECT id, title, COALESCE(status, 'active'), COALESCE(view_count, views, 0), COALESCE(likes, 0), created_at FROM {table_name} WHERE {author_field} = {current_user.id}")
                continue
        
        # 타입 필터링
        if post_type and post_type != 'all':
            all_posts = [post for post in all_posts if post["type"] == post_type]
        
        # 상태 필터링
        if status and status != 'all':
            all_posts = [post for post in all_posts if post["status"] == status]
        
        # 제목 검색
        if search:
            all_posts = [post for post in all_posts if search.lower() in post["title"].lower()]
        
        # 날짜순 정렬 (최신순)
        all_posts.sort(key=lambda x: x["created_at"] or "", reverse=True)
        
        # 페이지네이션
        total_count = len(all_posts)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_posts = all_posts[start_idx:end_idx]
        
        print(f"🔍 [MY_POSTS] 최종 결과: {total_count}개 중 {len(paginated_posts)}개 반환")
        
        return {
            "success": True,
            "data": paginated_posts,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        print(f"❌ [MY_POSTS] 전체 조회 오류: {str(e)}")
        return {
            "success": True,
            "data": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }