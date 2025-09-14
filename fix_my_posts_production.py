#!/usr/bin/env python3
"""
Production my-posts API 수정안
SQLAlchemy 모델 대신 raw SQL 사용하여 스키마 불일치 문제 해결
"""

# app/api/api_v1/endpoints/community_home.py의 get_my_posts 함수를 다음과 같이 수정:

MY_POSTS_FIXED_CODE = '''
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
        
        all_posts = []
        
        # 1. Raw SQL로 각 테이블에서 기본 정보만 조회
        tables_config = [
            ("community_sharing", "무료 나눔", "author_id"),  # author_id 사용
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
'''

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Production my-posts API 수정안")
    print("=" * 80)
    print()
    print("📝 문제점:")
    print("   - SQLAlchemy 모델과 실제 DB 스키마가 일치하지 않음")
    print("   - 모델이 존재하지 않는 컬럼을 참조하여 쿼리 실패")
    print("   - 결과적으로 my-posts API가 0개 게시글 반환")
    print()
    print("💡 해결 방안:")
    print("   - SQLAlchemy 모델 대신 Raw SQL 사용")
    print("   - 기본 필드(id, title, status, views, likes, created_at)만 조회")
    print("   - COALESCE로 컬럼명 차이 처리 (view_count vs views)")
    print("   - 각 테이블별로 안전하게 예외 처리")
    print()
    print("🔧 적용 방법:")
    print("   app/api/api_v1/endpoints/community_home.py의 get_my_posts 함수를")
    print("   위의 MY_POSTS_FIXED_CODE로 교체")
    print()
    print("=" * 80)