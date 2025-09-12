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


class MusicRecruitmentCreateRequest(BaseModel):
    """행사팀 모집 등록 요청 스키마"""
    # 기본 정보
    title: str  # 제목 (필수)
    event_type: Optional[str] = None  # 행사 유형
    description: Optional[str] = None  # 상세 설명
    
    # 일정 및 장소
    location: Optional[str] = None  # 장소
    address: Optional[str] = None  # 주소
    organizer: Optional[str] = None  # 주최자
    
    # 연락처
    contact_method: Optional[str] = None  # 연락 방법
    contact_info: Optional[str] = None  # 연락처
    
    # 참가 관련
    capacity: Optional[int] = None  # 정원
    fee: Optional[str] = None  # 참가비
    fee_description: Optional[str] = None  # 참가비 설명
    target_audience: Optional[str] = None  # 대상
    requirements: Optional[str] = None  # 요구사항
    includes: Optional[str] = None  # 포함사항
    
    # 상태
    status: Optional[str] = "active"  # 기본값: 'active'


router = APIRouter()


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
        
        # 기본 쿼리 - User 테이블과 LEFT JOIN
        query = db.query(ChurchEvent, User.full_name).outerjoin(
            User, ChurchEvent.author_id == User.id
        )
        
        # 필터링 적용
        if eventType and eventType != 'all':
            query = query.filter(ChurchEvent.event_type == eventType)
            print(f"🔍 [CHURCH_EVENTS_LIST] 행사 유형 필터 적용: {eventType}")
        if recruitmentType and recruitmentType != 'all':
            query = query.filter(ChurchEvent.event_type == recruitmentType)
            print(f"🔍 [CHURCH_EVENTS_LIST] 모집 유형 필터 적용: {recruitmentType}")
        if status and status != 'all':
            query = query.filter(ChurchEvent.status == status)
            print(f"🔍 [CHURCH_EVENTS_LIST] 상태 필터 적용: {status}")
        if search:
            query = query.filter(
                (ChurchEvent.title.ilike(f"%{search}%")) |
                (ChurchEvent.description.ilike(f"%{search}%")) |
                (ChurchEvent.organizer.ilike(f"%{search}%"))
            )
        
        # 전체 개수 계산
        total_count = query.count()
        print(f"🔍 [CHURCH_EVENTS_LIST] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        events_list = query.order_by(ChurchEvent.created_at.desc()).offset(offset).limit(limit).all()
        print(f"🔍 [CHURCH_EVENTS_LIST] 조회된 데이터 개수: {len(events_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for event, user_full_name in events_list:
            data_items.append({
                "id": event.id,
                "title": event.title,
                "eventType": event.event_type,
                "description": event.description,
                "location": event.location,
                "address": event.address,
                "organizer": event.organizer,
                "contactMethod": event.contact_method,
                "contactInfo": event.contact_info,
                "status": event.status,
                "capacity": event.capacity,
                "currentParticipants": event.current_participants or 0,
                "fee": event.fee,
                "feeDescription": event.fee_description,
                "targetAudience": event.target_audience,
                "requirements": event.requirements,
                "includes": event.includes,
                "startDate": event.start_date.isoformat() if event.start_date else None,
                "endDate": event.end_date.isoformat() if event.end_date else None,
                "registrationDeadline": event.registration_deadline.isoformat() if event.registration_deadline else None,
                "created_at": event.created_at.isoformat() if event.created_at else None,
                "updated_at": event.updated_at.isoformat() if event.updated_at else None,
                "views": event.views or 0,
                "likes": event.likes or 0,
                "author_id": event.author_id,
                "user_name": user_full_name or "익명",
                "church_id": event.church_id
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


@router.post("/music-recruitment", response_model=dict)
async def create_music_recruitment(
    request: Request,
    recruitment_data: MusicRecruitmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """행사팀 모집 등록 - 실제 데이터베이스 저장"""
    try:
        print(f"🔍 [MUSIC_RECRUITMENT] Music recruitment data received: {recruitment_data}")
        print(f"🔍 [MUSIC_RECRUITMENT] User ID: {current_user.id}, Church ID: {current_user.church_id}")
        print(f"🔍 [MUSIC_RECRUITMENT] User name: {current_user.full_name}")
        
        # 실제 데이터베이스에 저장
        event_record = ChurchEvent(
            title=recruitment_data.title,
            event_type=recruitment_data.event_type,
            description=recruitment_data.description,
            location=recruitment_data.location,
            address=recruitment_data.address,
            organizer=recruitment_data.organizer,
            contact_method=recruitment_data.contact_method,
            contact_info=recruitment_data.contact_info,
            capacity=recruitment_data.capacity,
            current_participants=0,
            fee=recruitment_data.fee,
            fee_description=recruitment_data.fee_description,
            target_audience=recruitment_data.target_audience,
            requirements=recruitment_data.requirements,
            includes=recruitment_data.includes,
            status=recruitment_data.status or "active",
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
            "message": "행사팀 모집이 등록되었습니다.",
            "data": {
                "id": event_record.id,
                "title": event_record.title,
                "eventType": event_record.event_type,
                "description": event_record.description,
                "location": event_record.location,
                "address": event_record.address,
                "organizer": event_record.organizer,
                "contactMethod": event_record.contact_method,
                "contactInfo": event_record.contact_info,
                "capacity": event_record.capacity,
                "currentParticipants": event_record.current_participants,
                "fee": event_record.fee,
                "feeDescription": event_record.fee_description,
                "targetAudience": event_record.target_audience,
                "requirements": event_record.requirements,
                "includes": event_record.includes,
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


@router.post("/church-events", response_model=dict)
async def create_church_event(
    request: Request,
    recruitment_data: MusicRecruitmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회 행사 등록 - music-recruitment와 동일한 로직 (별칭 엔드포인트)"""
    return await create_music_recruitment(request, recruitment_data, db, current_user)


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
        
        return {
            "success": True,
            "data": {
                "id": event.id,
                "title": event.title,
                "eventType": event.event_type,
                "description": event.description,
                "location": event.location,
                "address": event.address,
                "organizer": event.organizer,
                "contactMethod": event.contact_method,
                "contactInfo": event.contact_info,
                "capacity": event.capacity,
                "currentParticipants": event.current_participants or 0,
                "fee": event.fee,
                "feeDescription": event.fee_description,
                "targetAudience": event.target_audience,
                "requirements": event.requirements,
                "includes": event.includes,
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