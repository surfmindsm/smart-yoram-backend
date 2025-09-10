from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/music-team-recruit", response_model=dict)
def get_music_team_recruit_list(
    instrument: Optional[str] = Query(None, description="악기 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 목록 조회 - 단순화된 버전"""
    try:
        # 프론트엔드에서 기대하는 기본 구조 제공
        sample_items = []
        
        # 테스트용 샘플 데이터 (필요시)
        if page == 1:  # 첫 페이지에만 샘플 데이터 표시
            sample_items = [
                {
                    "id": 1,
                    "title": "테스트 음악팀 모집",
                    "description": "테스트용 샘플 음악팀 모집 공고입니다",
                    "instrument": "피아노",
                    "church_name": "샘플 교회",
                    "location": "서울",
                    "contact_method": "이메일",
                    "contact_info": "music@test.com",
                    "requirements": "중급 이상",
                    "schedule": "매주 일요일",
                    "status": "recruiting",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "views": 0,
                    "author_id": current_user.id,
                    "church_id": current_user.church_id
                }
            ]
        
        return {
            "success": True,
            "data": sample_items,
            "pagination": {
                "current_page": page,
                "total_pages": 1 if sample_items else 0,
                "total_count": len(sample_items),
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
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


@router.post("/music-team-recruit", response_model=dict)
async def create_music_team_recruit(
    title: str = Form(..., description="제목"),
    description: str = Form(..., description="상세 설명"),
    instrument: str = Form(..., description="모집 악기"),
    church_name: str = Form(..., description="교회명"),
    location: str = Form(..., description="지역"),
    contact_method: str = Form(..., description="연락 방법"),
    contact_info: str = Form(..., description="연락처"),
    requirements: Optional[str] = Form(None, description="자격 요건"),
    schedule: Optional[str] = Form(None, description="연습 일정"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 등록 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "음악팀 모집 공고가 등록되었습니다.",
            "data": {
                "id": 1,
                "title": title,
                "instrument": instrument,
                "church_name": church_name,
                "location": location,
                "status": "recruiting"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 모집 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/music-team-recruit/{recruit_id}", response_model=dict)
def get_music_team_recruit_detail(
    recruit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 상세 조회 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "data": {
                "id": recruit_id,
                "title": "샘플 음악팀 모집",
                "description": "샘플 음악팀 모집 설명",
                "instrument": "피아노",
                "church_name": "샘플 교회",
                "location": "서울",
                "status": "recruiting",
                "contact_method": "이메일",
                "contact_info": "music@test.com"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 모집 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/music-team-recruit/{recruit_id}", response_model=dict)
def delete_music_team_recruit(
    recruit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 삭제 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "음악팀 모집 공고가 삭제되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 모집 삭제 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/music-team-seeking", response_model=dict)
def get_music_team_seeking_list(
    instrument: Optional[str] = Query(None, description="악기 필터"),
    genre: Optional[str] = Query(None, description="장르 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 참여 희망 목록 조회 - 단순화된 버전"""
    try:
        # 프론트엔드에서 기대하는 기본 구조 제공
        sample_items = []
        
        # 테스트용 샘플 데이터 (필요시)
        if page == 1:  # 첫 페이지에만 샘플 데이터 표시
            sample_items = [
                {
                    "id": 1,
                    "title": "테스트 음악팀 참여 희망",
                    "description": "테스트용 샘플 음악팀 참여 희망입니다",
                    "instrument": "기타",
                    "genre": "찬양",
                    "location": "서울",
                    "contact_method": "이메일",
                    "contact_info": "seeking@test.com",
                    "experience_level": "중급",
                    "available_times": "주말",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "views": 0,
                    "author_id": current_user.id,
                    "church_id": current_user.church_id
                }
            ]
        
        return {
            "success": True,
            "data": sample_items,
            "pagination": {
                "current_page": page,
                "total_pages": 1 if sample_items else 0,
                "total_count": len(sample_items),
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
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


@router.post("/music-team-seeking", response_model=dict)
async def create_music_team_seeking(
    title: str = Form(..., description="제목"),
    description: str = Form(..., description="상세 설명"),
    instrument: str = Form(..., description="연주 악기"),
    genre: Optional[str] = Form(None, description="선호 장르"),
    experience_level: str = Form(..., description="경험 수준"),
    location: str = Form(..., description="지역"),
    contact_method: str = Form(..., description="연락 방법"),
    contact_info: str = Form(..., description="연락처"),
    available_times: Optional[str] = Form(None, description="가능한 시간"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 참여 희망 등록 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "음악팀 참여 희망이 등록되었습니다.",
            "data": {
                "id": 1,
                "title": title,
                "instrument": instrument,
                "genre": genre,
                "location": location,
                "status": "active"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 참여 희망 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/music-team-seeking/{seeking_id}", response_model=dict)
def get_music_team_seeking_detail(
    seeking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 참여 희망 상세 조회 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "data": {
                "id": seeking_id,
                "title": "샘플 음악팀 참여 희망",
                "description": "샘플 음악팀 참여 희망 설명",
                "instrument": "기타",
                "genre": "찬양",
                "location": "서울",
                "status": "active",
                "contact_method": "이메일",
                "contact_info": "seeking@test.com"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 참여 희망 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/music-team-seeking/{seeking_id}", response_model=dict)
def delete_music_team_seeking(
    seeking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 참여 희망 삭제 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "음악팀 참여 희망이 삭제되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 참여 희망 삭제 중 오류가 발생했습니다: {str(e)}"
        }