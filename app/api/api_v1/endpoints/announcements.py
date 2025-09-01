from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from datetime import date

from app import models, schemas
from app.api import deps
from app.core.announcement_categories import (
    get_categories,
    validate_category,
    ANNOUNCEMENT_CATEGORIES,
)

router = APIRouter()


@router.get("/active", response_model=List[schemas.Announcement])
def get_active_announcements(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    활성 공지사항 조회 (교회 관리자용)
    - 시스템 공지 (type = 'system') + 해당 교회 공지 (church_id = 사용자의 church_id)
    - start_date <= 오늘 <= end_date (end_date가 NULL이면 무제한)
    """
    try:
        today = date.today()
        
        # 기본 필터 조건
        base_filter = and_(
            models.Announcement.is_active == True,
        )
        
        # 해당 교회의 공지사항만 조회 (시스템 공지는 제외)
        announcements = db.query(models.Announcement).filter(
            and_(
                models.Announcement.is_active == True,
                models.Announcement.church_id == current_user.church_id
            )
        ).order_by(
            desc(models.Announcement.is_pinned),
            desc(models.Announcement.created_at)
        ).all()
        
        return announcements
        
    except Exception as e:
        print(f"Error in get_active_announcements: {str(e)}")
        # 빈 리스트 반환으로 fallback
        return []


@router.post("/{announcement_id}/read")
def mark_announcement_as_read(
    *,
    db: Session = Depends(deps.get_db),
    announcement_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    공지사항 읽음 처리
    """
    # 공지사항 존재 확인
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # 교회별 공지사항은 읽음 처리 기능 제거 (간소화)
    # 필요시 나중에 추가 구현
        pass
    
    return {"success": True, "message": "읽음 처리 완료"}


@router.get("/church-admin")
def get_church_announcements_admin(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    교회별 공지사항 조회 (교회 관리자용) - 단순 버전
    해당 교회의 공지사항만 조회
    """
    try:
        # 해당 교회의 공지사항만 조회
        announcements = db.query(models.Announcement).filter(
            models.Announcement.church_id == current_user.church_id
        ).limit(10).all()
        
        # 직접 딕셔너리로 변환
        result = []
        for ann in announcements:
            result.append({
                "id": ann.id,
                "title": ann.title,
                "content": ann.content,
                "category": getattr(ann, 'category', 'system'),
                "church_id": ann.church_id,
                "author_id": ann.author_id,
                "author_name": getattr(ann, 'author_name', ''),
                "is_active": getattr(ann, 'is_active', True),
                "created_at": ann.created_at.isoformat() if ann.created_at else None
            })
        
        return {"announcements": result, "total": len(result)}
        
    except Exception as e:
        print(f"Error in get_all_announcements_admin: {str(e)}")
        return {"error": str(e), "announcements": []}


@router.get("/categories", response_model=Dict[str, Any])
def get_announcement_categories(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get available announcement categories and subcategories.
    """
    return get_categories()



@router.get("/", response_model=List[schemas.Announcement])
def read_announcements(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    is_pinned: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve announcements for the current user's church.
    """
    query = db.query(models.Announcement).filter(
        models.Announcement.church_id == current_user.church_id
    )

    if is_active is not None:
        query = query.filter(models.Announcement.is_active == is_active)

    if is_pinned is not None:
        query = query.filter(models.Announcement.is_pinned == is_pinned)

    if category is not None:
        query = query.filter(models.Announcement.category == category)

    if subcategory is not None:
        query = query.filter(models.Announcement.subcategory == subcategory)

    # Order by pinned first, then by created date
    announcements = (
        query.order_by(
            desc(models.Announcement.is_pinned), desc(models.Announcement.created_at)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return announcements


@router.post("/", response_model=schemas.Announcement)
def create_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_in: schemas.AnnouncementCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new announcement.
    Only church admins and ministers can create announcements.
    """
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(
            status_code=403,
            detail="Only church admins and ministers can create announcements",
        )

    # Validate category and subcategory
    if not validate_category(announcement_in.category, announcement_in.subcategory):
        raise HTTPException(
            status_code=400, detail="Invalid category or subcategory combination"
        )

    announcement = models.Announcement(
        **announcement_in.dict(),
        church_id=current_user.church_id,
        author_id=current_user.id,
        author_name=current_user.full_name or current_user.username,
    )

    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.get("/{announcement_id}", response_model=schemas.Announcement)
def read_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get announcement by ID.
    """
    announcement = (
        db.query(models.Announcement)
        .filter(models.Announcement.id == announcement_id)
        .first()
    )

    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    if announcement.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return announcement


@router.put("/{announcement_id}", response_model=schemas.Announcement)
def update_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_id: int,
    announcement_in: schemas.AnnouncementUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an announcement.
    """
    announcement = (
        db.query(models.Announcement)
        .filter(models.Announcement.id == announcement_id)
        .first()
    )

    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    if announcement.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Only author or admin can update
    if announcement.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the author or admin can update this announcement",
        )

    update_data = announcement_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)

    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.delete("/{announcement_id}")
def delete_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an announcement.
    """
    announcement = (
        db.query(models.Announcement)
        .filter(models.Announcement.id == announcement_id)
        .first()
    )

    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    if announcement.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Only author or admin can delete
    if announcement.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the author or admin can delete this announcement",
        )

    db.delete(announcement)
    db.commit()
    return {"message": "Announcement deleted successfully"}


@router.put("/{announcement_id}/toggle-pin", response_model=schemas.Announcement)
def toggle_pin_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Toggle pin status of an announcement.
    Only admins can pin/unpin announcements.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only admins can pin/unpin announcements"
        )

    announcement = (
        db.query(models.Announcement)
        .filter(models.Announcement.id == announcement_id)
        .first()
    )

    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    if announcement.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    announcement.is_pinned = not announcement.is_pinned
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


# 시스템 관리자용 CRUD 엔드포인트 (church_id = 0인 사용자만)
@router.post("/admin", response_model=schemas.Announcement)
def create_system_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_in: schemas.AnnouncementCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    시스템 공지사항 생성 (시스템 관리자용)
    권한: church_id = 0인 사용자만
    
    단순화된 버전: 일단 전체 공지만 지원
    """
    try:
        if current_user.church_id != 0:
            raise HTTPException(
                status_code=403,
                detail="시스템 관리자만 접근 가능합니다"
            )
        
        # 기존 테이블 구조에 맞는 데이터 처리
        announcement_data = {
            'title': announcement_in.title,
            'content': announcement_in.content,
            'category': getattr(announcement_in, 'category', 'system'),
            'church_id': None,  # 시스템 공지는 NULL
            'author_id': current_user.id,
            'author_name': current_user.full_name or current_user.username,
            'is_active': True,
        }
        
        # 공지사항 생성
        announcement = models.Announcement(**announcement_data)
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        
        return announcement
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_system_announcement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/admin/{announcement_id}", response_model=schemas.Announcement)  
def update_system_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_id: int,
    announcement_in: schemas.AnnouncementUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    시스템 공지사항 수정 (시스템 관리자용)
    권한: church_id = 0인 사용자만
    """
    if current_user.church_id != 0:
        raise HTTPException(
            status_code=403,
            detail="시스템 관리자만 접근 가능합니다"
        )
    
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # 시스템 공지사항만 수정 가능
    if announcement.type != 'system':
        raise HTTPException(
            status_code=403,
            detail="시스템 공지사항만 수정 가능합니다"
        )
    
    update_data = announcement_in.dict(exclude_unset=True, exclude={'target_church_ids'})
    target_church_ids = getattr(announcement_in, 'target_church_ids', [])
    
    # target_type 변경 처리
    if 'target_type' in update_data:
        target_type = update_data['target_type']
        
        if target_type == 'all':
            update_data['church_id'] = None
        elif target_type == 'specific':
            update_data['church_id'] = None
            if not target_church_ids:
                raise HTTPException(status_code=400, detail="특정 교회 선택 시 target_church_ids가 필요합니다")
        elif target_type == 'single':
            if not update_data.get('church_id'):
                raise HTTPException(status_code=400, detail="단일 교회 선택 시 church_id가 필요합니다")
    
    # 기본 필드 업데이트
    for field, value in update_data.items():
        setattr(announcement, field, value)
    
    db.add(announcement)
    db.commit()
    
    # target_type이 'specific'으로 변경된 경우 대상 교회 업데이트
    if 'target_type' in update_data and update_data['target_type'] == 'specific':
        # 기존 대상 교회 삭제
        db.query(models.AnnouncementTarget).filter(
            models.AnnouncementTarget.announcement_id == announcement_id
        ).delete()
        
        # 새 대상 교회 추가
        for church_id in target_church_ids:
            target = models.AnnouncementTarget(
                announcement_id=announcement_id,
                church_id=church_id
            )
            db.add(target)
        db.commit()
    
    db.refresh(announcement)
    return announcement


@router.delete("/admin/{announcement_id}")
def delete_system_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    시스템 공지사항 삭제 (시스템 관리자용)
    권한: church_id = 0인 사용자만
    """
    if current_user.church_id != 0:
        raise HTTPException(
            status_code=403,
            detail="시스템 관리자만 접근 가능합니다"
        )
    
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # 시스템 공지사항만 삭제 가능
    if announcement.type != 'system':
        raise HTTPException(
            status_code=403,
            detail="시스템 공지사항만 삭제 가능합니다"
        )
    
    db.delete(announcement)
    db.commit()
    return {"message": "System announcement deleted successfully"}
