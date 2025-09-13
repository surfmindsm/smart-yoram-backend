"""
음악팀 지원자(Music Team Seekers) 관련 API 엔드포인트
연주자/팀이 교회 행사에 지원하는 시스템
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.music_team_seeker import MusicTeamSeeker


class MusicTeamSeekerCreateRequest(BaseModel):
    """음악팀 지원서 등록 요청 스키마"""
    # 필수 필드
    title: str
    instrument: str
    contact_phone: str
    
    # 선택 필드
    team_name: Optional[str] = None
    experience: Optional[str] = None
    portfolio: Optional[str] = None
    preferred_location: Optional[List[str]] = None
    available_days: Optional[List[str]] = None
    available_time: Optional[str] = None
    contact_email: Optional[str] = None


class MusicTeamSeekerUpdateRequest(BaseModel):
    """음악팀 지원서 수정 요청 스키마"""
    title: Optional[str] = None
    team_name: Optional[str] = None
    instrument: Optional[str] = None
    experience: Optional[str] = None
    portfolio: Optional[str] = None
    preferred_location: Optional[List[str]] = None
    available_days: Optional[List[str]] = None
    available_time: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None


router = APIRouter()


@router.get("/music-team-seekers", response_model=dict)
def get_music_team_seekers_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    status: Optional[str] = Query(None, description="상태 필터"),
    instrument: Optional[str] = Query(None, description="팀 형태 필터"),
    location: Optional[str] = Query(None, description="지역 필터"),
    day: Optional[str] = Query(None, description="요일 필터"),
    time: Optional[str] = Query(None, description="시간대 필터"),
    search: Optional[str] = Query(None, description="제목/경력 검색"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 목록 조회"""
    try:
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 지원서 목록 조회 시작")
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 필터: status={status}, instrument={instrument}, location={location}")
        
        # 기본 쿼리
        query = db.query(MusicTeamSeeker)
        
        # 필터링 적용
        if status:
            query = query.filter(MusicTeamSeeker.status == status)
        
        if instrument:
            query = query.filter(MusicTeamSeeker.instrument == instrument)
        
        if location:
            query = query.filter(MusicTeamSeeker.preferred_location.op('?')(location))
        
        if day:
            query = query.filter(MusicTeamSeeker.available_days.op('?')(day))
        
        if time:
            query = query.filter(MusicTeamSeeker.available_time.ilike(f"%{time}%"))
        
        if search:
            query = query.filter(
                (MusicTeamSeeker.title.ilike(f"%{search}%")) |
                (MusicTeamSeeker.experience.ilike(f"%{search}%"))
            )
        
        # 전체 개수 계산
        total_count = query.count()
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        seekers_list = query.order_by(MusicTeamSeeker.created_at.desc()).offset(offset).limit(limit).all()
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 조회된 데이터 개수: {len(seekers_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for seeker in seekers_list:
            data_items.append({
                "id": seeker.id,
                "title": seeker.title,
                "team_name": seeker.team_name,
                "instrument": seeker.instrument,
                "experience": seeker.experience,
                "portfolio": seeker.portfolio,
                "preferred_location": seeker.preferred_location or [],
                "available_days": seeker.available_days or [],
                "available_time": seeker.available_time,
                "contact_phone": seeker.contact_phone,
                "contact_email": seeker.contact_email,
                "status": seeker.status,
                "author_id": seeker.author_id,
                "author_name": seeker.author_name,
                "church_id": seeker.church_id,
                "church_name": seeker.church_name,
                "views": seeker.views or 0,
                "likes": seeker.likes or 0,
                "matches": seeker.matches or 0,
                "applications": seeker.applications or 0,
                "created_at": seeker.created_at.isoformat() if seeker.created_at else None,
                "updated_at": seeker.updated_at.isoformat() if seeker.updated_at else None
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 음악팀 지원서 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
        return {
            "success": True,
            "data": {
                "items": data_items,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": total_pages
                }
            }
        }
        
    except Exception as e:
        print(f"❌ [MUSIC_TEAM_SEEKERS] 목록 조회 오류: {str(e)}")
        return {
            "success": True,
            "data": {
                "items": [],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": 0,
                    "pages": 0
                }
            }
        }


@router.post("/music-team-seekers", response_model=dict)
async def create_music_team_seeker(
    request: Request,
    seeker_data: MusicTeamSeekerCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 등록"""
    try:
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 지원서 데이터 받음: {seeker_data}")
        
        # 현재 시간 설정
        current_time = datetime.now(timezone.utc)
        
        # 데이터베이스에 저장 - PostgreSQL text[] 타입과 호환되도록 배열 처리
        seeker_record = MusicTeamSeeker(
            title=seeker_data.title,
            team_name=seeker_data.team_name,
            instrument=seeker_data.instrument,
            experience=seeker_data.experience,
            portfolio=seeker_data.portfolio,
            preferred_location=seeker_data.preferred_location if seeker_data.preferred_location else [],
            available_days=seeker_data.available_days if seeker_data.available_days else [],
            available_time=seeker_data.available_time,
            contact_phone=seeker_data.contact_phone,
            contact_email=seeker_data.contact_email,
            status="available",  # 기본 상태
            author_id=current_user.id,
            author_name=current_user.full_name or "익명",
            church_id=getattr(current_user, 'church_id', None),
            church_name=getattr(current_user, 'church_name', None),
            views=0,
            likes=0,
            matches=0,
            applications=0,
            created_at=current_time,
            updated_at=current_time
        )
        
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 지원서 레코드 저장 중...")
        db.add(seeker_record)
        db.commit()
        db.refresh(seeker_record)
        print(f"✅ [MUSIC_TEAM_SEEKERS] 성공적으로 저장됨. ID: {seeker_record.id}")
        
        return {
            "success": True,
            "message": "지원서가 성공적으로 등록되었습니다",
            "data": {
                "id": seeker_record.id,
                "created_at": seeker_record.created_at.isoformat() if seeker_record.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [MUSIC_TEAM_SEEKERS] 등록 실패: {str(e)}")
        import traceback
        print(f"❌ [MUSIC_TEAM_SEEKERS] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"지원서 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/music-team-seekers/{seeker_id}", response_model=dict)
def get_music_team_seeker_detail(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 상세 조회"""
    try:
        seeker = db.query(MusicTeamSeeker).filter(MusicTeamSeeker.id == seeker_id).first()
        if not seeker:
            return {
                "success": False,
                "message": "지원서를 찾을 수 없습니다."
            }
        
        # 조회수 증가
        seeker.views = (seeker.views or 0) + 1
        db.commit()
        
        return {
            "success": True,
            "data": {
                "id": seeker.id,
                "title": seeker.title,
                "team_name": seeker.team_name,
                "instrument": seeker.instrument,
                "experience": seeker.experience,
                "portfolio": seeker.portfolio,
                "preferred_location": seeker.preferred_location or [],
                "available_days": seeker.available_days or [],
                "available_time": seeker.available_time,
                "contact_phone": seeker.contact_phone,
                "contact_email": seeker.contact_email,
                "status": seeker.status,
                "author_id": seeker.author_id,
                "author_name": seeker.author_name,
                "church_id": seeker.church_id,
                "church_name": seeker.church_name,
                "views": seeker.views or 0,
                "likes": seeker.likes or 0,
                "matches": seeker.matches or 0,
                "applications": seeker.applications or 0,
                "created_at": seeker.created_at.isoformat() if seeker.created_at else None,
                "updated_at": seeker.updated_at.isoformat() if seeker.updated_at else None
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"지원서 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/music-team-seekers/{seeker_id}", response_model=dict)
async def update_music_team_seeker(
    seeker_id: int,
    seeker_data: MusicTeamSeekerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 수정"""
    try:
        seeker = db.query(MusicTeamSeeker).filter(MusicTeamSeeker.id == seeker_id).first()
        if not seeker:
            return {
                "success": False,
                "message": "지원서를 찾을 수 없습니다."
            }
        
        # 작성자 권한 확인
        if seeker.author_id != current_user.id:
            return {
                "success": False,
                "message": "본인이 작성한 지원서만 수정할 수 있습니다."
            }
        
        # 수정 가능한 필드 업데이트 (None이 아닌 값만)
        update_data = seeker_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            # PostgreSQL text[] 타입과 호환되도록 배열 필드 처리
            if field in ['preferred_location', 'available_days'] and value is not None:
                setattr(seeker, field, value if value else [])
            else:
                setattr(seeker, field, value)
        
        # updated_at 명시적으로 설정
        seeker.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(seeker)
        
        return {
            "success": True,
            "message": "지원서가 수정되었습니다.",
            "data": {
                "id": seeker.id,
                "title": seeker.title,
                "updated_at": seeker.updated_at.isoformat() if seeker.updated_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"지원서 수정 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/music-team-seekers/{seeker_id}", response_model=dict)
def delete_music_team_seeker(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 삭제"""
    try:
        seeker = db.query(MusicTeamSeeker).filter(MusicTeamSeeker.id == seeker_id).first()
        if not seeker:
            return {
                "success": False,
                "message": "지원서를 찾을 수 없습니다."
            }
        
        # 작성자 권한 확인
        if seeker.author_id != current_user.id:
            return {
                "success": False,
                "message": "본인이 작성한 지원서만 삭제할 수 있습니다."
            }
        
        db.delete(seeker)
        db.commit()
        
        return {
            "success": True,
            "message": "지원서가 삭제되었습니다."
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"지원서 삭제 중 오류가 발생했습니다: {str(e)}"
        }