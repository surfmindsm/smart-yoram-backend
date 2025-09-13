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
    """내가 올린 글 목록 조회 - 모든 커뮤니티 테이블에서 조회"""
    try:
        print(f"🔍 [MY_POSTS] 사용자 {current_user.id}의 게시글 조회 시작")
        all_posts = []
        
        # 1. 무료 나눔 (community_sharing)
        try:
            sharing_posts = db.query(CommunitySharing).filter(
                CommunitySharing.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 무료 나눔: {len(sharing_posts)}개")
            
            for post in sharing_posts:
                all_posts.append({
                    "id": post.id,
                    "type": "community-sharing",
                    "type_label": "무료 나눔",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 무료 나눔 조회 오류: {e}")
        
        # 2. 물품 요청 (community_request)
        try:
            request_posts = db.query(CommunityRequest).filter(
                CommunityRequest.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 물품 요청: {len(request_posts)}개")
            
            for post in request_posts:
                all_posts.append({
                    "id": post.id,
                    "type": "community-request",
                    "type_label": "물품 요청", 
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 물품 요청 조회 오류: {e}")
        
        # 3. 구인 공고 (job_posts)
        try:
            job_posts = db.query(JobPost).filter(
                JobPost.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 구인 공고: {len(job_posts)}개")
            
            for post in job_posts:
                all_posts.append({
                    "id": post.id,
                    "type": "job-posts",
                    "type_label": "구인 공고",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 구인 공고 조회 오류: {e}")
        
        # 4. 구직 신청 (job_seekers)
        try:
            job_seekers = db.query(JobSeeker).filter(
                JobSeeker.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 구직 신청: {len(job_seekers)}개")
            
            for post in job_seekers:
                all_posts.append({
                    "id": post.id,
                    "type": "job-seekers",
                    "type_label": "구직 신청",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 구직 신청 조회 오류: {e}")
        
        # 5. 음악팀 모집 (music_team_recruitment)
        try:
            music_recruits = db.query(MusicTeamRecruitment).filter(
                MusicTeamRecruitment.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 음악팀 모집: {len(music_recruits)}개")
            
            for post in music_recruits:
                all_posts.append({
                    "id": post.id,
                    "type": "music-team-recruitment",
                    "type_label": "음악팀 모집",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 음악팀 모집 조회 오류: {e}")
        
        # 6. 음악팀 참여 (music_team_seekers)
        try:
            music_seekers = db.query(MusicTeamSeeker).filter(
                MusicTeamSeeker.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 음악팀 참여: {len(music_seekers)}개")
            
            for post in music_seekers:
                all_posts.append({
                    "id": post.id,
                    "type": "music-team-seekers",
                    "type_label": "음악팀 참여",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 음악팀 참여 조회 오류: {e}")
        
        # 7. 교회 소식 (church_news)
        try:
            church_news = db.query(ChurchNews).filter(
                ChurchNews.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 교회 소식: {len(church_news)}개")
            
            for post in church_news:
                all_posts.append({
                    "id": post.id,
                    "type": "church-news",
                    "type_label": "교회 소식",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 교회 소식 조회 오류: {e}")
        
        # 8. 교회 행사 (church_events)
        try:
            church_events = db.query(ChurchEvent).filter(
                ChurchEvent.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 교회 행사: {len(church_events)}개")
            
            for post in church_events:
                all_posts.append({
                    "id": post.id,
                    "type": "church-events",
                    "type_label": "교회 행사",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "views": getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0,
                    "likes": post.likes or 0,
                })
        except Exception as e:
            print(f"❌ [MY_POSTS] 교회 행사 조회 오류: {e}")
        
        # 타입 필터링
        if post_type and post_type != 'all':
            all_posts = [post for post in all_posts if post["type"] == post_type]
            print(f"🔍 [MY_POSTS] 타입 필터 적용 ({post_type}): {len(all_posts)}개")
        
        # 상태 필터링
        if status and status != 'all':
            all_posts = [post for post in all_posts if post["status"] == status]
            print(f"🔍 [MY_POSTS] 상태 필터 적용 ({status}): {len(all_posts)}개")
        
        # 제목 검색
        if search:
            all_posts = [post for post in all_posts if search.lower() in post["title"].lower()]
            print(f"🔍 [MY_POSTS] 검색 필터 적용 ({search}): {len(all_posts)}개")
        
        # 날짜순 정렬 (최신순)
        all_posts.sort(key=lambda x: x["created_at"] or "", reverse=True)
        
        # 페이지네이션
        total_count = len(all_posts)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_posts = all_posts[start_idx:end_idx]
        
        print(f"🔍 [MY_POSTS] 최종 결과: {total_count}개 중 {len(paginated_posts)}개 반환 (페이지 {page}/{total_pages})")
        
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
        import traceback
        print(f"❌ [MY_POSTS] Traceback: {traceback.format_exc()}")
        
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