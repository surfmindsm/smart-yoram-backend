"""
교번 자동생성 관련 API
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.services.member_number_service import MemberNumberService

router = APIRouter()


@router.get("/next-number")
def get_next_member_number(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    다음 교번 생성
    """
    try:
        member_number = MemberNumberService.assign_member_number(db, current_user.church_id)
        
        return {
            "success": True,
            "data": {
                "member_number": member_number,
                "format": "NNNNNNN"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교번 생성 실패: {str(e)}")


@router.post("/assign-missing-numbers")
def assign_missing_member_numbers(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    교번이 없는 기존 교인들에게 교번 일괄 할당
    관리자만 실행 가능
    """
    # 관리자 권한 확인
    if current_user.role not in ["admin", "pastor", "system_admin"]:
        raise HTTPException(status_code=403, detail="관리자만 실행할 수 있습니다")
    
    try:
        updated_count = MemberNumberService.update_existing_members_with_numbers(
            db, current_user.church_id
        )
        
        return {
            "success": True,
            "message": f"{updated_count}명의 교인에게 교번을 할당했습니다",
            "updated_count": updated_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교번 일괄 할당 실패: {str(e)}")


@router.get("/validate/{member_number}")
def validate_member_number(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    member_number: str,
) -> Any:
    """
    교번 중복 확인
    """
    try:
        exists = MemberNumberService.is_member_number_exists(
            db, current_user.church_id, member_number
        )
        
        return {
            "success": True,
            "data": {
                "member_number": member_number,
                "exists": exists,
                "available": not exists
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교번 확인 실패: {str(e)}")