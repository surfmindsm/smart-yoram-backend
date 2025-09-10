from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.community_sharing import CommunitySharing
from app.models.community_request import CommunityRequest
from app.models.job_post import JobPost, JobSeeker
from app.models.music_team import MusicTeamRecruit, MusicTeamApplication
from app.models.church_event import ChurchEvent

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
def get_community_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """커뮤니티 홈 통계 조회"""
    try:
        # 기본 테이블들만 사용해서 안전하게 계산
        sharing_count = db.query(CommunitySharing).count()
        request_count = db.query(CommunityRequest).count()
        job_post_count = db.query(JobPost).count()
        job_seeker_count = db.query(JobSeeker).count()
        music_request_count = 0  # music_requests 테이블 사용
        event_count = 0  # event_announcements 테이블 사용
        
        # 존재하는 테이블들만 안전하게 쿼리
        try:
            from app.models.music_request import MusicRequest
            music_request_count = db.query(MusicRequest).count()
        except:
            music_request_count = 0
            
        try:
            from app.models.event_announcement import EventAnnouncement
            event_count = db.query(EventAnnouncement).count()
        except:
            event_count = 0
        
        total_posts = (
            sharing_count + request_count + job_post_count + 
            job_seeker_count + music_request_count + event_count
        )
        
        # 활성 상태별 통계 (안전하게)
        active_sharing = db.query(CommunitySharing).filter(
            CommunitySharing.status == "available"
        ).count()
        
        active_requests = db.query(CommunityRequest).filter(
            CommunityRequest.status == "open"
        ).count()
        
        open_job_posts = db.query(JobPost).filter(
            JobPost.status == "active"
        ).count()
        
        open_music_requests = music_request_count  # 모든 음악 요청
        
        # 이번 달 행사 수
        events_this_month = event_count  # 모든 이벤트
        
        # 총 회원 수 (모든 사용자)
        total_members = db.query(User).count()
        
        return {
            "success": True,
            "data": {
                "total_posts": total_posts,
                "active_sharing": active_sharing,
                "active_requests": active_requests,
                "job_posts": open_job_posts,
                "music_teams": open_music_requests,
                "events_this_month": events_this_month,
                "total_members": total_members
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/recent-posts")
def get_recent_posts(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """최근 게시글 조회"""
    try:
        recent_posts = []
        
        # 최근 나눔 게시글
        recent_sharing = db.query(CommunitySharing).order_by(
            CommunitySharing.created_at.desc()
        ).limit(limit // 2).all()
        
        for post in recent_sharing:
            recent_posts.append({
                "id": post.id,
                "type": "free-sharing",
                "title": post.title,
                "user_id": post.user_id,  # author_id 대신 user_id 사용
                "church_id": post.church_id,
                "created_at": post.created_at,
                "status": post.status,
                "views": getattr(post, 'view_count', 0),  # views 대신 view_count 사용
                "likes": 0  # likes 컬럼이 없으므로 기본값 0
            })
        
        # 최근 요청 게시글
        recent_requests = db.query(CommunityRequest).order_by(
            CommunityRequest.created_at.desc()
        ).limit(limit // 2).all()
        
        for post in recent_requests:
            recent_posts.append({
                "id": post.id,
                "type": "item-request",
                "title": post.title,
                "user_id": post.user_id,  # author_id 대신 user_id 사용
                "church_id": post.church_id,
                "created_at": post.created_at,
                "status": post.status,
                "views": getattr(post, 'view_count', 0),  # views 대신 view_count 사용
                "likes": 0  # likes 컬럼이 없으므로 기본값 0
            })
        
        # 생성일 기준으로 정렬
        recent_posts.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "data": recent_posts[:limit]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"최근 게시글 조회 중 오류가 발생했습니다: {str(e)}"
        )


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
    """내가 올린 글 목록 조회"""
    try:
        my_posts = []
        
        # 나눔 게시글
        if not post_type or post_type == "free-sharing":
            sharing_query = db.query(CommunitySharing).filter(
                CommunitySharing.user_id == current_user.id
            )
            if status:
                sharing_query = sharing_query.filter(CommunitySharing.status == status)
            if search:
                sharing_query = sharing_query.filter(CommunitySharing.title.contains(search))
            
            sharing_posts = sharing_query.all()
            for post in sharing_posts:
                my_posts.append({
                    "id": post.id,
                    "type": "free-sharing",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at,
                    "views": getattr(post, 'view_count', 0),  # views 대신 view_count 사용
                    "likes": 0,  # likes 컬럼이 없으므로 기본값 0
                    "church_id": post.church_id,
                    "location": post.location
                })
        
        # 요청 게시글
        if not post_type or post_type == "item-request":
            request_query = db.query(CommunityRequest).filter(
                CommunityRequest.user_id == current_user.id
            )
            if status:
                request_query = request_query.filter(CommunityRequest.status == status)
            if search:
                request_query = request_query.filter(CommunityRequest.title.contains(search))
            
            request_posts = request_query.all()
            for post in request_posts:
                my_posts.append({
                    "id": post.id,
                    "type": "item-request",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at,
                    "views": getattr(post, 'view_count', 0),  # views 대신 view_count 사용
                    "likes": 0,  # likes 컬럼이 없으므로 기본값 0
                    "church_id": post.church_id,
                    "location": post.location
                })
        
        # 구인 공고
        if not post_type or post_type == "job-post":
            job_query = db.query(JobPost).filter(
                JobPost.user_id == current_user.id
            )
            if status:
                job_query = job_query.filter(JobPost.status == status)
            if search:
                job_query = job_query.filter(JobPost.title.contains(search))
            
            job_posts = job_query.all()
            for post in job_posts:
                my_posts.append({
                    "id": post.id,
                    "type": "job-post",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at,
                    "views": getattr(post, 'view_count', 0),  # views 대신 view_count 사용
                    "likes": 0,  # likes 컬럼이 없으므로 기본값 0
                    "church_id": post.church_id,
                    "location": post.location
                })
        
        # 구직 신청
        if not post_type or post_type == "job-seeker":
            seeker_query = db.query(JobSeeker).filter(
                JobSeeker.user_id == current_user.id
            )
            if status:
                seeker_query = seeker_query.filter(JobSeeker.status == status)
            if search:
                seeker_query = seeker_query.filter(JobSeeker.title.contains(search))
            
            seeker_posts = seeker_query.all()
            for post in seeker_posts:
                my_posts.append({
                    "id": post.id,
                    "type": "job-seeker",
                    "title": post.title,
                    "status": post.status,
                    "created_at": post.created_at,
                    "views": getattr(post, 'view_count', 0),  # views 대신 view_count 사용
                    "likes": 0,  # likes 컬럼이 없으므로 기본값 0
                    "church_id": post.church_id,
                    "location": post.desired_location
                })
        
        # 생성일 기준으로 정렬
        my_posts.sort(key=lambda x: x["created_at"], reverse=True)
        
        # 페이징
        total_count = len(my_posts)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_posts = my_posts[start_idx:end_idx]
        
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "data": paginated_posts,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"내 게시글 조회 중 오류가 발생했습니다: {str(e)}"
        )