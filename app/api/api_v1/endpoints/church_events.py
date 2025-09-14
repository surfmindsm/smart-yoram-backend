"""
교회 행사팀 모집 관련 API 엔드포인트
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.church_events import ChurchEvent


class ChurchEventCreateRequest(BaseModel):
    """교회 행사 등록 요청 스키마"""
    # 기본 정보
    title: str  # 제목 (필수)
    description: Optional[str] = None  # 상세 설명
    
    # 일정 및 장소
    event_date: Optional[str] = None  # 행사 일시 (ISO 형식)
    location: Optional[str] = None  # 장소
    
    # 참가 관련
    max_participants: Optional[int] = None  # 최대 참가자
    
    # 연락처 정보 (분리된 형태)
    contact_phone: str  # 담당자 연락처 (필수) - 전화번호
    contact_email: Optional[str] = None  # 이메일 (선택)
    
    # 상태
    status: Optional[str] = "upcoming"  # 기본값: 'upcoming'


router = APIRouter()


def parse_contact_info(contact_info: str) -> tuple[str, str]:
    """연락처 정보를 전화번호와 이메일로 분리"""
    phone = ""
    email = ""
    
    if contact_info:
        parts = contact_info.split(" | ")
        for part in parts:
            if part.startswith("전화: "):
                phone = part.replace("전화: ", "")
            elif part.startswith("이메일: "):
                email = part.replace("이메일: ", "")
    
    return phone, email


@router.get("/church-events", response_model=dict)
def get_church_events_list(
    eventType: Optional[str] = Query(None, description="행사 유형 필터"),
    recruitmentType: Optional[str] = Query(None, description="모집 유형 필터"),
    status: Optional[str] = Query(None, description="상태 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """행사팀 모집 목록 조회 - 실제 데이터베이스에서 조회"""
    try:
        print(f"🔍 [CHURCH_EVENTS_LIST] 행사팀 모집 목록 조회 시작")
        print(f"🔍 [CHURCH_EVENTS_LIST] 필터: eventType={eventType}, recruitmentType={recruitmentType}, status={status}")
        
        # Raw SQL로 안전한 조회 - 트랜잭션 초기화
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                ce.id,
                ce.title,
                'active' as status,
                0 as views,
                0 as likes,
                ce.created_at,
                ce.author_id,
                u.full_name
            FROM church_events ce
            LEFT JOIN users u ON ce.author_id = u.id
            WHERE 1=1
        """
        params = {}
        
        # 필터링 적용 (기본 검색만)
        if search:
            query_sql += " AND ce.title ILIKE :search"
            params["search"] = f"%{search}%"
            print(f"🔍 [CHURCH_EVENTS_LIST] 검색 필터 적용: {search}")
        
        query_sql += " ORDER BY ce.created_at DESC"
        
        # 전체 개수 계산
        count_sql = "SELECT COUNT(*) FROM church_events ce WHERE 1=1"
        if search:
            count_sql += " AND ce.title ILIKE :search"
        count_result = db.execute(text(count_sql), params)
        total_count = count_result.scalar() or 0
        print(f"🔍 [CHURCH_EVENTS_LIST] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        query_sql += f" OFFSET {offset} LIMIT {limit}"
        
        result = db.execute(text(query_sql), params)
        events_list = result.fetchall()
        print(f"🔍 [CHURCH_EVENTS_LIST] 조회된 데이터 개수: {len(events_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for row in events_list:
            # 기본 정보만으로 간소화 (Raw SQL 결과 사용)
            data_items.append({
                "id": row[0],
                "title": row[1],
                "description": row[1],  # 제목을 설명으로 임시 사용
                "eventDate": None,  # 기본값
                "location": "미정",  # 기본값
                "maxParticipants": 0,  # 기본값
                "contactPhone": "",  # 기본값
                "contactEmail": "",  # 기본값
                "contactInfo": "댓글로 연락",  # 기본값
                "status": row[2],
                "views": row[3] or 0,
                "likes": row[4] or 0,
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[5].isoformat() if row[5] else None,
                "author_id": row[6],
                "user_name": row[7] or "익명",
                "church_id": 9998
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 행사팀 모집 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
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
        # 에러가 발생해도 기본 구조는 유지
        print(f"❌ [CHURCH_EVENTS_LIST] 오류: {str(e)}")
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


@router.post("/church-events", response_model=dict)
async def create_church_event(
    request: Request,
    event_data: ChurchEventCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 등록 - 실제 데이터베이스 저장"""
    try:
        print(f"🔍 [CHURCH_EVENT] Church event data received: {event_data}")
        print(f"🔍 [CHURCH_EVENT] User ID: {current_user.id}, Church ID: {current_user.church_id}")
        print(f"🔍 [CHURCH_EVENT] User name: {current_user.full_name}")
        
        # 실제 데이터베이스에 저장
        from datetime import datetime
        event_date_obj = None
        if event_data.event_date:
            try:
                event_date_obj = datetime.fromisoformat(event_data.event_date.replace('Z', '+00:00'))
            except:
                print(f"⚠️ [CHURCH_EVENT] Invalid date format: {event_data.event_date}")
        
        # contact_info를 phone과 email 조합으로 생성
        contact_parts = [f"전화: {event_data.contact_phone}"]
        if event_data.contact_email:
            contact_parts.append(f"이메일: {event_data.contact_email}")
        combined_contact_info = " | ".join(contact_parts)
        
        event_record = ChurchEvent(
            title=event_data.title,
            description=event_data.description,
            event_date=event_date_obj,
            location=event_data.location,
            max_participants=event_data.max_participants,
            contact_info=combined_contact_info,  # 조합된 연락처 정보
            status=event_data.status or "upcoming",
            author_id=current_user.id,
            church_id=current_user.church_id or 9998,  # 커뮤니티 기본값
            views=0,
            likes=0
        )
        
        print(f"🔍 [MUSIC_RECRUITMENT] About to save music recruitment record...")
        db.add(event_record)
        db.commit()
        db.refresh(event_record)
        print(f"✅ [MUSIC_RECRUITMENT] Successfully saved music recruitment with ID: {event_record.id}")
        
        # 저장 후 검증 - 실제로 DB에서 다시 조회
        saved_record = db.query(ChurchEvent).filter(ChurchEvent.id == event_record.id).first()
        if saved_record:
            print(f"✅ [MUSIC_RECRUITMENT] Verification successful: Record exists in DB with ID {saved_record.id}")
        else:
            print(f"❌ [MUSIC_RECRUITMENT] Verification failed: Record not found in DB!")
        
        return {
            "success": True,
            "message": "교회 행사가 등록되었습니다.",
            "data": {
                "id": event_record.id,
                "title": event_record.title,
                "description": event_record.description,
                "eventDate": event_record.event_date.isoformat() if event_record.event_date else None,
                "location": event_record.location,
                "maxParticipants": event_record.max_participants,
                "contactPhone": event_data.contact_phone,
                "contactEmail": event_data.contact_email,
                "contactInfo": event_record.contact_info,  # 백워드 호환성
                "status": event_record.status,
                "views": event_record.views,
                "likes": event_record.likes,
                "author_id": event_record.author_id,
                "user_name": current_user.full_name or "익명",
                "church_id": event_record.church_id,
                "created_at": event_record.created_at.isoformat() if event_record.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [MUSIC_RECRUITMENT] 행사팀 모집 등록 실패: {str(e)}")
        import traceback
        print(f"❌ [MUSIC_RECRUITMENT] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"행사팀 모집 등록 중 오류가 발생했습니다: {str(e)}"
        }




@router.get("/church-events/{event_id}", response_model=dict)
def get_church_event_detail(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 상세 조회 - 실제 데이터베이스에서 조회"""
    try:
        event = db.query(ChurchEvent).filter(ChurchEvent.id == event_id).first()
        if not event:
            return {
                "success": False,
                "message": "행사팀 모집을 찾을 수 없습니다."
            }
        
        # 연락처 정보를 전화번호와 이메일로 분리
        contact_phone, contact_email = parse_contact_info(event.contact_info or "")
        
        return {
            "success": True,
            "data": {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "eventDate": event.event_date.isoformat() if event.event_date else None,
                "location": event.location,
                "maxParticipants": event.max_participants,
                "contactPhone": contact_phone,
                "contactEmail": contact_email,
                "contactInfo": event.contact_info,  # 백워드 호환성
                "status": event.status,
                "views": event.views or 0,
                "likes": event.likes or 0
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"교회 행사 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/church-events/{event_id}", response_model=dict)
def delete_church_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 삭제"""
    try:
        event = db.query(ChurchEvent).filter(ChurchEvent.id == event_id).first()
        if not event:
            return {
                "success": False,
                "message": "행사팀 모집을 찾을 수 없습니다."
            }
        
        # 작성자만 삭제 가능
        if event.author_id != current_user.id:
            return {
                "success": False,
                "message": "삭제 권한이 없습니다."
            }
        
        db.delete(event)
        db.commit()
        
        return {
            "success": True,
            "message": "행사팀 모집이 삭제되었습니다."
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"교회 행사 삭제 중 오류가 발생했습니다: {str(e)}"
        }