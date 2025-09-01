"""
교인 관리용 코드 조회 API
"""
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.api import deps

router = APIRouter()


@router.get("/member-types", response_model=List[Dict[str, str]])
def get_member_types(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    교인구분 코드 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "member_type",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/districts", response_model=List[Dict[str, Any]])
def get_districts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    구역 목록 조회 (부구역 포함)
    """
    districts = db.query(models.Code).filter(
        models.Code.type == "district",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    sub_districts = db.query(models.Code).filter(
        models.Code.type == "sub_district",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    # 구역별로 부구역 그룹화
    result = []
    for district in districts:
        district_code = district.code.split('_')[-1]  # DISTRICT_1 -> 1
        related_sub_districts = [
            {"code": sub.code, "label": sub.label}
            for sub in sub_districts
            if sub.code.startswith(f"SUB_{district_code}_")
        ]
        
        result.append({
            "code": district.code,
            "label": district.label,
            "sub_districts": related_sub_districts
        })
    
    return result


@router.get("/church-schools", response_model=List[Dict[str, str]])
def get_church_schools(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    교회학교 목록 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "church_school",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/job-categories", response_model=List[Dict[str, str]])
def get_job_categories(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    직업 분류 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "job_category",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/spiritual-grades", response_model=List[Dict[str, str]])
def get_spiritual_grades(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    신급 코드 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "spiritual_grade",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/positions", response_model=List[Dict[str, str]])
def get_positions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    직분 코드 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "position",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/contact-types", response_model=List[Dict[str, str]])
def get_contact_types(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    연락처 타입 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "contact_type",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/vehicle-types", response_model=List[Dict[str, str]])
def get_vehicle_types(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    차량 타입 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "vehicle_type",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/registration-backgrounds", response_model=List[Dict[str, str]])
def get_registration_backgrounds(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    등록배경 코드 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "registration_background",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/age-groups", response_model=List[Dict[str, str]])
def get_age_groups(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    나이그룹 코드 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "age_group",
        models.Code.church_id.in_([0, current_user.church_id])
    ).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]


@router.get("/school-years", response_model=List[Dict[str, str]])
def get_school_years(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    교회학교 연도 조회
    """
    codes = db.query(models.Code).filter(
        models.Code.type == "school_year",
        models.Code.church_id.in_([0, current_user.church_id])
    ).order_by(models.Code.code.desc()).all()
    
    return [{"code": c.code, "label": c.label} for c in codes]