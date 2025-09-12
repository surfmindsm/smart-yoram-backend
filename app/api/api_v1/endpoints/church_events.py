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
    title: str  # 모집 제목 (필수)
    churchName: str  # 교회명 (필수)
    recruitmentType: str  # 행사 유형 (필수)
    
    # 모집 상세
    instruments: List[str]  # 모집 악기/포지션 배열 (필수)
    schedule: str  # 일정 정보
    location: str  # 장소 정보
    
    # 상세 내용
    description: str  # 상세 설명
    requirements: Optional[str] = None  # 자격 요건
    compensation: Optional[str] = None  # 보상/사례비
    
    # 연락처 (분리된 형태)
    contactPhone: str  # 전화번호 (필수)
    contactEmail: Optional[str] = None  # 이메일 (선택)
    
    # 시스템 필드
    status: Optional[str] = "open"  # 기본값: 'open'
    applications: Optional[int] = 0  # 초기값: 0


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
            User, ChurchEvent.user_id == User.id
        )
        
        # 필터링 적용
        if eventType and eventType != 'all':
            query = query.filter(ChurchEvent.recruitment_type == eventType)
            print(f"🔍 [CHURCH_EVENTS_LIST] 행사 유형 필터 적용: {eventType}")
        if recruitmentType and recruitmentType != 'all':
            query = query.filter(ChurchEvent.recruitment_type == recruitmentType)
            print(f"🔍 [CHURCH_EVENTS_LIST] 모집 유형 필터 적용: {recruitmentType}")
        if status and status != 'all':
            query = query.filter(ChurchEvent.status == status)
            print(f"🔍 [CHURCH_EVENTS_LIST] 상태 필터 적용: {status}")
        if search:
            query = query.filter(
                (ChurchEvent.title.ilike(f"%{search}%")) |
                (ChurchEvent.description.ilike(f"%{search}%")) |
                (ChurchEvent.church_name.ilike(f"%{search}%"))
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
            # contact_info에서 전화번호와 이메일 분리
            contact_phone = event.contact_phone or ""
            contact_email = event.contact_email or ""
            
            data_items.append({
                "id": event.id,
                "title": event.title,
                "churchName": event.church_name,
                "recruitmentType": event.recruitment_type,
                "instruments": event.instruments or [],
                "schedule": event.schedule,
                "location": event.location,
                "description": event.description,
                "requirements": event.requirements,
                "compensation": event.compensation,
                "contactPhone": contact_phone,
                "contactEmail": contact_email,
                "contact": event.contact_info,  # 프론트엔드 호환성
                "contactInfo": event.contact_info,  # 프론트엔드 호환성
                "status": event.status,
                "applications": event.applications or 0,
                "created_at": event.created_at.isoformat() if event.created_at else None,
                "updated_at": event.updated_at.isoformat() if event.updated_at else None,
                "view_count": event.view_count or 0,
                "user_id": event.user_id,
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
        
        # contact_info를 phone과 email 조합으로 생성
        contact_parts = [f"전화: {recruitment_data.contactPhone}"]
        if recruitment_data.contactEmail:
            contact_parts.append(f"이메일: {recruitment_data.contactEmail}")
        combined_contact_info = " | ".join(contact_parts)
        
        # 실제 데이터베이스에 저장
        event_record = ChurchEvent(
            title=recruitment_data.title,
            church_name=recruitment_data.churchName,
            recruitment_type=recruitment_data.recruitmentType,
            instruments=recruitment_data.instruments,  # JSON 배열로 저장
            schedule=recruitment_data.schedule,
            location=recruitment_data.location,
            description=recruitment_data.description,
            requirements=recruitment_data.requirements,
            compensation=recruitment_data.compensation,
            contact_info=combined_contact_info,  # 조합된 연락처 정보
            contact_phone=recruitment_data.contactPhone,
            contact_email=recruitment_data.contactEmail,
            status=recruitment_data.status or "open",
            applications=recruitment_data.applications or 0,
            user_id=current_user.id,
            author_id=current_user.id,  # 중복 필드도 채움
            church_id=current_user.church_id or 9998,  # 커뮤니티 기본값
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
                "churchName": event_record.church_name,
                "recruitmentType": event_record.recruitment_type,
                "instruments": event_record.instruments,
                "schedule": event_record.schedule,
                "location": event_record.location,
                "description": event_record.description,
                "requirements": event_record.requirements,
                "compensation": event_record.compensation,
                "contactPhone": event_record.contact_phone,
                "contactEmail": event_record.contact_email,
                "contact": combined_contact_info,  # 프론트엔드 호환성
                "contactInfo": combined_contact_info,  # 프론트엔드 호환성
                "status": event_record.status,
                "applications": event_record.applications,
                "user_id": event_record.user_id,
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
                "churchName": event.church_name,
                "recruitmentType": event.recruitment_type,
                "instruments": event.instruments or [],
                "schedule": event.schedule,
                "location": event.location,
                "description": event.description,
                "requirements": event.requirements,
                "compensation": event.compensation,
                "contactPhone": event.contact_phone,
                "contactEmail": event.contact_email,
                "contact": event.contact_info,
                "status": event.status,
                "applications": event.applications or 0
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
        if event.user_id != current_user.id:
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