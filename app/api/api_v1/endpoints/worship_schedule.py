from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models import User, Church, WorshipService, WorshipServiceCategory
from app.schemas.worship_schedule import (
    WorshipService as WorshipServiceSchema,
    WorshipServiceCreate,
    WorshipServiceUpdate,
    WorshipServiceCategory as WorshipServiceCategorySchema,
    WorshipServiceCategoryCreate,
    WorshipServiceCategoryUpdate,
    WorshipScheduleResponse
)
from app.crud.base import CRUDBase

router = APIRouter()


@router.get("/schedule", response_model=WorshipScheduleResponse)
def get_worship_schedule(
    church_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """교회의 전체 예배 스케줄 조회"""
    # If church_id is not provided, use the current user's church_id
    if church_id is None:
        church_id = current_user.church_id
    
    if current_user.church_id != church_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다"
        )
    
    categories = db.query(WorshipServiceCategory).filter(
        WorshipServiceCategory.church_id == church_id
    ).order_by(WorshipServiceCategory.order_index).all()
    
    services = db.query(WorshipService).filter(
        WorshipService.church_id == church_id,
        WorshipService.is_active == True
    ).order_by(WorshipService.order_index).all()
    
    return WorshipScheduleResponse(categories=categories, services=services)


@router.get("/services", response_model=List[WorshipServiceSchema])
def get_worship_services(
    church_id: Optional[int] = None,
    service_type: Optional[str] = None,
    target_group: Optional[str] = None,
    day_of_week: Optional[int] = None,
    is_online: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 서비스 목록 조회"""
    # If church_id is not provided, use the current user's church_id
    if church_id is None:
        church_id = current_user.church_id
        
    if current_user.church_id != church_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다"
        )
    
    query = db.query(WorshipService).filter(
        WorshipService.church_id == church_id,
        WorshipService.is_active == True
    )
    
    if service_type:
        query = query.filter(WorshipService.service_type == service_type)
    if target_group:
        query = query.filter(WorshipService.target_group == target_group)
    if day_of_week is not None:
        query = query.filter(WorshipService.day_of_week == day_of_week)
    if is_online is not None:
        query = query.filter(WorshipService.is_online == is_online)
    
    services = query.order_by(WorshipService.order_index).all()
    return services


@router.post("/services", response_model=WorshipServiceSchema)
def create_worship_service(
    service: WorshipServiceCreate,
    church_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 서비스 생성"""
    # If church_id is not provided, use the current user's church_id
    if church_id is None:
        church_id = current_user.church_id
        
    if current_user.church_id != church_id or current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="예배 일정 생성 권한이 없습니다"
        )
    
    db_service = WorshipService(
        church_id=church_id,
        **service.dict()
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.get("/services/{service_id}", response_model=WorshipServiceSchema)
def get_worship_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """특정 예배 서비스 조회"""
    service = db.query(WorshipService).filter(WorshipService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="예배 서비스를 찾을 수 없습니다"
        )
    
    if current_user.church_id != service.church_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다"
        )
    
    return service


@router.patch("/services/{service_id}", response_model=WorshipServiceSchema)
def update_worship_service(
    service_id: int,
    service_update: WorshipServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 서비스 수정"""
    service = db.query(WorshipService).filter(WorshipService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="예배 서비스를 찾을 수 없습니다"
        )
    
    if current_user.church_id != service.church_id or current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="예배 일정 수정 권한이 없습니다"
        )
    
    for field, value in service_update.dict(exclude_unset=True).items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    return service


@router.delete("/services/{service_id}")
def delete_worship_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 서비스 삭제"""
    service = db.query(WorshipService).filter(WorshipService.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="예배 서비스를 찾을 수 없습니다"
        )
    
    if current_user.church_id != service.church_id or current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="예배 일정 삭제 권한이 없습니다"
        )
    
    db.delete(service)
    db.commit()
    return {"message": "예배 서비스가 삭제되었습니다"}


@router.get("/categories", response_model=List[WorshipServiceCategorySchema])
def get_worship_categories(
    church_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 카테고리 목록 조회"""
    # If church_id is not provided, use the current user's church_id
    if church_id is None:
        church_id = current_user.church_id
        
    if current_user.church_id != church_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다"
        )
    
    categories = db.query(WorshipServiceCategory).filter(
        WorshipServiceCategory.church_id == church_id
    ).order_by(WorshipServiceCategory.order_index).all()
    
    return categories


@router.post("/categories", response_model=WorshipServiceCategorySchema)
def create_worship_category(
    category: WorshipServiceCategoryCreate,
    church_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 카테고리 생성"""
    # If church_id is not provided, use the current user's church_id
    if church_id is None:
        church_id = current_user.church_id
        
    if current_user.church_id != church_id or current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="카테고리 생성 권한이 없습니다"
        )
    
    db_category = WorshipServiceCategory(
        church_id=church_id,
        **category.dict()
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.patch("/categories/{category_id}", response_model=WorshipServiceCategorySchema)
def update_worship_category(
    category_id: int,
    category_update: WorshipServiceCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 카테고리 수정"""
    category = db.query(WorshipServiceCategory).filter(
        WorshipServiceCategory.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="카테고리를 찾을 수 없습니다"
        )
    
    if current_user.church_id != category.church_id or current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="카테고리 수정 권한이 없습니다"
        )
    
    for field, value in category_update.dict(exclude_unset=True).items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_worship_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """예배 카테고리 삭제"""
    category = db.query(WorshipServiceCategory).filter(
        WorshipServiceCategory.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="카테고리를 찾을 수 없습니다"
        )
    
    if current_user.church_id != category.church_id or current_user.role not in ["admin", "pastor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="카테고리 삭제 권한이 없습니다"
        )
    
    db.delete(category)
    db.commit()
    return {"message": "카테고리가 삭제되었습니다"}