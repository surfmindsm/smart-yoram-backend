#!/usr/bin/env python3
"""
my-posts API 로직을 직접 테스트 (API 서버 없이)
실제 production 코드와 동일한 로직으로 SQLite 데이터베이스에서 조회
"""
import os
import sys
from datetime import datetime

# 환경변수 설정
os.environ['DATABASE_URL'] = 'sqlite:///./local_test.db'
os.environ['SECRET_KEY'] = 'smart-yoram-secret-key-2025-change-in-production'

# app 디렉토리를 Python path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.community_sharing import CommunitySharing
from app.models.community_request import CommunityRequest
from app.models.job_posts import JobPost, JobSeeker
from app.models.music_team_recruitment import MusicTeamRecruitment
from app.models.music_team_seeker import MusicTeamSeeker
from app.models.church_news import ChurchNews
from app.models.church_events import ChurchEvent


def get_views_count(post):
    """조회수를 안전하게 가져오는 헬퍼 함수 (community_home.py와 동일)"""
    return getattr(post, 'view_count', 0) or getattr(post, 'views', 0) or 0


def get_author_name(post):
    """작성자 이름을 안전하게 가져오는 헬퍼 함수 (community_home.py와 동일)"""
    if hasattr(post, 'author') and post.author:
        return post.author.full_name if hasattr(post.author, 'full_name') else "익명"
    return "익명"


def format_post_response(post, post_type, type_label):
    """게시글 응답을 표준화하는 헬퍼 함수 (community_home.py와 동일)"""
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


def simulate_my_posts_logic(user_id):
    """my-posts API 로직 시뮬레이션 (community_home.py get_my_posts와 동일)"""
    print(f"🔍 [MY_POSTS] 사용자 {user_id}의 게시글 조회 시작")
    
    # SQLAlchemy 연결
    engine = create_engine('sqlite:///./local_test.db')
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 사용자 조회 (JWT에서 가져온 user_id)
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            print(f"❌ [MY_POSTS] 사용자 {user_id}를 찾을 수 없습니다!")
            return []
        
        print(f"🔍 [MY_POSTS] current_user 정보 - ID: {current_user.id}, 이름: {getattr(current_user, 'full_name', 'N/A')}, 이메일: {getattr(current_user, 'email', 'N/A')}")
        
        all_posts = []
        
        # 1. 무료 나눔 (community_sharing)
        try:
            # 실제 API와 동일하게 AttributeError 처리
            try:
                sharing_posts = db.query(CommunitySharing).filter(
                    CommunitySharing.author_id == current_user.id
                ).all()
            except AttributeError:
                # author_id가 없으면 user_id 사용
                sharing_posts = db.query(CommunitySharing).filter(
                    CommunitySharing.user_id == current_user.id
                ).all()
            print(f"🔍 [MY_POSTS] 무료 나눔: {len(sharing_posts)}개")
            
            for post in sharing_posts:
                all_posts.append(format_post_response(post, "community-sharing", "무료 나눔"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 무료 나눔 조회 오류: {e}")
        
        # 2. 물품 요청 (community_request)
        try:
            request_posts = db.query(CommunityRequest).filter(
                CommunityRequest.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 물품 요청: {len(request_posts)}개")
            
            for post in request_posts:
                all_posts.append(format_post_response(post, "community-request", "물품 요청"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 물품 요청 조회 오류: {e}")
        
        # 3. 구인 공고 (job_posts)
        try:
            job_posts = db.query(JobPost).filter(
                JobPost.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 구인 공고: {len(job_posts)}개")
            
            for post in job_posts:
                all_posts.append(format_post_response(post, "job-posts", "구인 공고"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 구인 공고 조회 오류: {e}")
        
        # 4. 구직 신청 (job_seekers)
        try:
            job_seekers = db.query(JobSeeker).filter(
                JobSeeker.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 구직 신청: {len(job_seekers)}개")
            
            for post in job_seekers:
                all_posts.append(format_post_response(post, "job-seekers", "구직 신청"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 구직 신청 조회 오류: {e}")
        
        # 5. 음악팀 모집 (music_team_recruitment)
        try:
            music_recruits = db.query(MusicTeamRecruitment).filter(
                MusicTeamRecruitment.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 음악팀 모집: {len(music_recruits)}개")
            
            for post in music_recruits:
                all_posts.append(format_post_response(post, "music-team-recruitment", "음악팀 모집"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 음악팀 모집 조회 오류: {e}")
        
        # 6. 음악팀 참여 (music_team_seekers)
        try:
            music_seekers = db.query(MusicTeamSeeker).filter(
                MusicTeamSeeker.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 음악팀 참여: {len(music_seekers)}개")
            
            for post in music_seekers:
                all_posts.append(format_post_response(post, "music-team-seekers", "음악팀 참여"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 음악팀 참여 조회 오류: {e}")
        
        # 7. 교회 소식 (church_news)
        try:
            church_news = db.query(ChurchNews).filter(
                ChurchNews.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 교회 소식: {len(church_news)}개")
            
            for post in church_news:
                all_posts.append(format_post_response(post, "church-news", "교회 소식"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 교회 소식 조회 오류: {e}")
        
        # 8. 교회 행사 (church_events)
        try:
            church_events = db.query(ChurchEvent).filter(
                ChurchEvent.author_id == current_user.id
            ).all()
            print(f"🔍 [MY_POSTS] 교회 행사: {len(church_events)}개")
            
            for post in church_events:
                all_posts.append(format_post_response(post, "church-events", "교회 행사"))
        except Exception as e:
            print(f"❌ [MY_POSTS] 교회 행사 조회 오류: {e}")
        
        # 날짜순 정렬 (최신순)
        all_posts.sort(key=lambda x: x["created_at"] or "", reverse=True)
        
        print(f"🔍 [MY_POSTS] 최종 결과: {len(all_posts)}개")
        
        return all_posts
        
    except Exception as e:
        print(f"❌ [MY_POSTS] 전체 조회 오류: {str(e)}")
        import traceback
        print(f"❌ [MY_POSTS] Traceback: {traceback.format_exc()}")
        return []
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 my-posts API 로직 직접 테스트 (SQLite)")
    print("=" * 60)
    
    # user_id 54로 my-posts 로직 실행
    posts = simulate_my_posts_logic(54)
    
    print(f"\n📊 결과 요약:")
    print(f"   총 게시글 수: {len(posts)}")
    
    if posts:
        print(f"\n📝 게시글 목록:")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. [{post['type_label']}] {post['title']}")
            print(f"     ID: {post['id']}, 상태: {post['status']}, 작성자: {post['author_name']}")
            print(f"     생성일: {post['created_at']}")
    else:
        print("❌ 게시글이 없습니다!")
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")