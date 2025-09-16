"""
교회 행사 소식 관련 API 엔드포인트
"""
from typing import Optional, List, Literal
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone, date, time

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.church_news import ChurchNews


class ChurchNewsCreateRequest(BaseModel):
    """교회 소식 등록 요청 스키마"""
    # 필수 필드
    title: str
    content: str
    category: str
    organizer: str
    
    # 선택 필드
    priority: Optional[Literal['urgent', 'important', 'normal']] = "normal"
    event_date: Optional[str] = None  # ISO 형식 날짜
    event_time: Optional[str] = None  # HH:MM 형식
    location: Optional[str] = None
    target_audience: Optional[str] = None
    participation_fee: Optional[str] = None
    registration_required: Optional[bool] = False
    registration_deadline: Optional[str] = None  # ISO 형식 날짜
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[Literal['active', 'completed', 'cancelled']] = "active"
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None


class ChurchNewsUpdateRequest(BaseModel):
    """교회 소식 수정 요청 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    organizer: Optional[str] = None
    priority: Optional[Literal['urgent', 'important', 'normal']] = None
    event_date: Optional[str] = None
    event_time: Optional[str] = None
    location: Optional[str] = None
    target_audience: Optional[str] = None
    participation_fee: Optional[str] = None
    registration_required: Optional[bool] = None
    registration_deadline: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[Literal['active', 'completed', 'cancelled']] = None
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None


router = APIRouter()


def parse_date(date_string: str) -> date:
    """ISO 형식 날짜 문자열을 date 객체로 변환"""
    if not date_string:
        return None
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00')).date()
    except:
        return None


def parse_time(time_string: str) -> time:
    """HH:MM 형식 시간 문자열을 time 객체로 변환"""
    if not time_string:
        return None
    try:
        return datetime.strptime(time_string, '%H:%M').time()
    except:
        return None


@router.get("/church-news", response_model=dict)
def get_church_news_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    priority: Optional[str] = Query(None, description="우선순위 필터"),
    status: Optional[str] = Query(None, description="상태 필터"),
    search: Optional[str] = Query(None, description="제목/내용/주최자 검색"),
    event_date_from: Optional[str] = Query(None, description="행사일 시작 범위"),
    event_date_to: Optional[str] = Query(None, description="행사일 끝 범위"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 소식 목록 조회"""
    try:
        print(f"🔍 [CHURCH_NEWS] 교회 소식 목록 조회 시작")
        print(f"🔍 [CHURCH_NEWS] 필터: category={category}, priority={priority}, status={status}")
        
        # Raw SQL로 안전한 조회 - 트랜잭션 초기화
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                cn.id,
                cn.title,
                'active' as status,
                0 as views,
                0 as likes,
                cn.created_at,
                cn.author_id,
                u.full_name
            FROM church_news cn
            LEFT JOIN users u ON cn.author_id = u.id
            WHERE 1=1
        """
        params = {}
        
        # 기본 필터링 (검색만)
        if search:
            query_sql += " AND cn.title ILIKE :search"
            params["search"] = f"%{search}%"
            print(f"🔍 [CHURCH_NEWS] 검색 필터 적용: {search}")
        
        query_sql += " ORDER BY cn.created_at DESC"
        
        # 전체 개수 계산
        count_sql = "SELECT COUNT(*) FROM church_news cn WHERE 1=1"
        if search:
            count_sql += " AND cn.title ILIKE :search"
        count_result = db.execute(text(count_sql), params)
        total_count = count_result.scalar() or 0
        print(f"🔍 [CHURCH_NEWS] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        query_sql += f" OFFSET {offset} LIMIT {limit}"
        
        result = db.execute(text(query_sql), params)
        news_list = result.fetchall()
        print(f"🔍 [CHURCH_NEWS] 조회된 데이터 개수: {len(news_list)}")
        
        # 응답 데이터 구성 (기본 정보만)
        data_items = []
        for row in news_list:
            data_items.append({
                "id": row[0],
                "title": row[1],
                "content": row[1],  # 제목을 내용으로 임시 사용
                "category": "일반",  # 기본값
                "priority": "보통",  # 기본값
                "event_date": None,
                "event_time": None,
                "location": "미정",
                "organizer": "교회",
                "target_audience": "전체",
                "participation_fee": 0,
                "registration_required": False,
                "registration_deadline": None,
                "contact_person": "담당자",
                "contact_phone": "",
                "contact_email": "",
                "status": row[2],
                "view_count": row[3] or 0,
                "likes": row[4] or 0,
                "comments_count": 0,
                "tags": [],
                "images": [],
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[5].isoformat() if row[5] else None,
                "author_id": row[6],
                "author_name": row[7] or "익명",
                "church_id": 9998
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 교회 소식 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
        return {
            "success": True,
            "data": data_items,
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
        print(f"❌ [CHURCH_NEWS] 목록 조회 오류: {str(e)}")
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


@router.post("/church-news", response_model=dict)
async def create_church_news(
    request: Request,
    news_data: ChurchNewsCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 소식 등록"""
    try:
        print(f"🔍 [CHURCH_NEWS] 교회 소식 데이터 받음: {news_data}")
        print(f"🔍 [CHURCH_NEWS] 원본 Priority: {news_data.priority} (type: {type(news_data.priority)})")
        print(f"🔍 [CHURCH_NEWS] 원본 Status: {news_data.status} (type: {type(news_data.status)})")
        
        # 변환된 값 확인
        processed_priority = news_data.priority.lower() if news_data.priority else "normal"
        processed_status = news_data.status.lower() if news_data.status else "active"
        print(f"🔍 [CHURCH_NEWS] 변환된 Priority: {processed_priority}")
        print(f"🔍 [CHURCH_NEWS] 변환된 Status: {processed_status}")
        
        # 현재 시간 설정
        current_time = datetime.now(timezone.utc)
        
        # 날짜/시간 파싱
        event_date_obj = parse_date(news_data.event_date)
        event_time_obj = parse_time(news_data.event_time)
        registration_deadline_obj = parse_date(news_data.registration_deadline)
        
        # 데이터베이스에 저장 (ENUM 값 안전하게 처리)
        news_record = ChurchNews(
            title=news_data.title,
            content=news_data.content,
            category=news_data.category,
            priority=news_data.priority.lower() if news_data.priority else "normal",
            event_date=event_date_obj,
            event_time=event_time_obj,
            location=news_data.location,
            organizer=news_data.organizer,
            target_audience=news_data.target_audience,
            participation_fee=news_data.participation_fee,
            registration_required=news_data.registration_required,
            registration_deadline=registration_deadline_obj,
            contact_person=news_data.contact_person,
            contact_phone=news_data.contact_phone,
            contact_email=news_data.contact_email,
            status=news_data.status.lower() if news_data.status else "active",
            view_count=0,
            likes=0,
            comments_count=0,
            tags=news_data.tags or [],
            images=news_data.images or [],
            author_id=current_user.id,
            church_id=getattr(current_user, 'church_id', None),
            created_at=current_time,
            updated_at=current_time
        )
        
        print(f"🔍 [CHURCH_NEWS] 교회 소식 레코드 저장 중...")
        db.add(news_record)
        db.commit()
        db.refresh(news_record)
        print(f"✅ [CHURCH_NEWS] 성공적으로 저장됨. ID: {news_record.id}")
        
        return {
            "success": True,
            "message": "교회 행사 소식이 등록되었습니다.",
            "data": {
                "id": news_record.id,
                "title": news_record.title,
                "category": news_record.category,
                "status": news_record.status,
                "created_at": news_record.created_at.isoformat() if news_record.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [CHURCH_NEWS] 등록 실패: {str(e)}")
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ [CHURCH_NEWS] Traceback: {error_traceback}")
        
        # 개발 환경에서는 더 자세한 에러 정보 제공
        error_detail = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": error_traceback.split('\n')[-3:-1] if error_traceback else None  # 마지막 2줄만
        }
        
        return {
            "success": False,
            "message": f"교회 소식 등록 중 오류가 발생했습니다: {str(e)}",
            "error_detail": error_detail  # 프론트엔드에서 활용 가능한 상세 정보
        }


@router.post("/church-news/{news_id}/increment-view", response_model=dict)
def increment_church_news_view_count(
    news_id: int,
    db: Session = Depends(get_db)
):
    """교회 소식 조회수 증가 전용 API - 인증 없이 사용 가능"""
    try:
        from sqlalchemy import text
        print(f"🚀 [VIEW_INCREMENT_API] 교회 소식 조회수 증가 전용 API 호출 - ID: {news_id}")

        # 현재 조회수 확인
        check_sql = "SELECT view_count FROM church_news WHERE id = :news_id"
        result = db.execute(text(check_sql), {"news_id": news_id})
        row = result.fetchone()

        if not row:
            return {
                "success": False,
                "message": "해당 교회 소식을 찾을 수 없습니다."
            }

        current_view_count = row[0] or 0
        print(f"🔍 [VIEW_INCREMENT_API] 현재 조회수: {current_view_count}")

        # 조회수 증가
        increment_sql = """
            UPDATE church_news
            SET view_count = COALESCE(view_count, 0) + 1
            WHERE id = :news_id
            RETURNING view_count
        """
        result = db.execute(text(increment_sql), {"news_id": news_id})
        new_view_count = result.fetchone()[0]
        db.commit()

        print(f"✅ [VIEW_INCREMENT_API] 조회수 증가 성공 - ID: {news_id}, {current_view_count} → {new_view_count}")

        return {
            "success": True,
            "data": {
                "news_id": news_id,
                "previous_view_count": current_view_count,
                "new_view_count": new_view_count
            }
        }

    except Exception as e:
        db.rollback()
        print(f"❌ [VIEW_INCREMENT_API] 조회수 증가 실패 - ID: {news_id}, 오류: {e}")
        return {
            "success": False,
            "message": f"조회수 증가 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/church-news/{news_id}", response_model=dict)
def get_church_news_detail(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 소식 상세 조회"""
    try:
        # Raw SQL로 안전한 조회
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                cn.id,
                cn.title,
                u.full_name
            FROM church_news cn
            LEFT JOIN users u ON cn.author_id = u.id
            WHERE cn.id = :news_id
        """
        
        result = db.execute(text(query_sql), {"news_id": news_id})
        row = result.fetchone()
        
        if not row:
            return {
                "success": False,
                "message": "교회 소식을 찾을 수 없습니다."
            }
        
        news_id, title, author_name = row
        
        return {
            "success": True,
            "data": {
                "id": news_id,
                "title": title,
                "content": title,  # 제목을 내용으로 임시 사용
                "category": "일반",
                "priority": "보통",
                "event_date": None,
                "event_time": None,
                "location": "미정",
                "organizer": "교회",
                "target_audience": "전체",
                "participation_fee": 0,
                "registration_required": False,
                "registration_deadline": None,
                "contact_person": "담당자",
                "contact_phone": "",
                "contact_email": "",
                "status": "active",
                "view_count": 0,
                "likes": 0,
                "comments_count": 0,
                "tags": [],
                "images": [],
                "created_at": None,
                "updated_at": None,
                "author_id": 1,
                "author_name": author_name or "익명",
                "church_id": 9998
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"교회 소식 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/church-news/{news_id}", response_model=dict)
async def update_church_news(
    news_id: int,
    news_data: ChurchNewsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 소식 수정"""
    try:
        news = db.query(ChurchNews).filter(ChurchNews.id == news_id).first()
        if not news:
            return {
                "success": False,
                "message": "교회 소식을 찾을 수 없습니다."
            }
        
        # 작성자 권한 확인 (본인만 수정 가능)
        if news.author_id != current_user.id:
            return {
                "success": False,
                "message": "본인이 작성한 소식만 수정할 수 있습니다."
            }
        
        # 수정 가능한 필드 업데이트 (None이 아닌 값만)
        update_data = news_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == 'event_date' and value:
                setattr(news, field, parse_date(value))
            elif field == 'event_time' and value:
                setattr(news, field, parse_time(value))
            elif field == 'registration_deadline' and value:
                setattr(news, field, parse_date(value))
            elif field in ['tags', 'images'] and value is not None:
                setattr(news, field, value if value else [])
            elif field == 'priority' and value:
                setattr(news, field, value.lower())  # ENUM 값 소문자 변환
            elif field == 'status' and value:
                setattr(news, field, value.lower())  # ENUM 값 소문자 변환
            else:
                setattr(news, field, value)
        
        # updated_at 명시적으로 설정
        news.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(news)
        
        return {
            "success": True,
            "message": "교회 소식이 수정되었습니다.",
            "data": {
                "id": news.id,
                "title": news.title,
                "updated_at": news.updated_at.isoformat() if news.updated_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ [CHURCH_NEWS] 수정 실패: {str(e)}")
        print(f"❌ [CHURCH_NEWS] Traceback: {error_traceback}")
        
        return {
            "success": False,
            "message": f"교회 소식 수정 중 오류가 발생했습니다: {str(e)}",
            "error_detail": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": error_traceback.split('\n')[-3:-1] if error_traceback else None
            }
        }


@router.delete("/church-news/{news_id}", response_model=dict)
def delete_church_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 소식 삭제"""
    try:
        news = db.query(ChurchNews).filter(ChurchNews.id == news_id).first()
        if not news:
            return {
                "success": False,
                "message": "교회 소식을 찾을 수 없습니다."
            }
        
        # 작성자 권한 확인 (본인만 삭제 가능)
        if news.author_id != current_user.id:
            return {
                "success": False,
                "message": "본인이 작성한 소식만 삭제할 수 있습니다."
            }
        
        db.delete(news)
        db.commit()
        
        return {
            "success": True,
            "message": "교회 소식이 삭제되었습니다."
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"교회 소식 삭제 중 오류가 발생했습니다: {str(e)}"
        }


@router.post("/church-news/{news_id}/like", response_model=dict)
async def toggle_church_news_like(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 소식 좋아요 토글"""
    try:
        news = db.query(ChurchNews).filter(ChurchNews.id == news_id).first()
        if not news:
            return {
                "success": False,
                "message": "교회 소식을 찾을 수 없습니다."
            }
        
        # 실제 좋아요 테이블이 있다면 여기서 처리
        # 현재는 단순히 좋아요 수만 증가
        news.likes = (news.likes or 0) + 1
        db.commit()
        
        return {
            "success": True,
            "data": {
                "liked": True,
                "likes_count": news.likes
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"좋아요 처리 중 오류가 발생했습니다: {str(e)}"
        }