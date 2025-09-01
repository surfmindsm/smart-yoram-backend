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
    today = date.today()
    
    # 시스템 공지사항 - 전체 공지 (target_type = 'all')
    all_announcements_query = db.query(models.Announcement).filter(
        and_(
            models.Announcement.is_active == True,
            models.Announcement.type == 'system',
            models.Announcement.target_type == 'all',
            # 날짜 필터링
            models.Announcement.start_date <= today,
            or_(
                models.Announcement.end_date >= today,
                models.Announcement.end_date == None
            )
        )
    )
    
    # 시스템 공지사항 - 특정 교회 대상 (target_type = 'specific')
    specific_announcements_query = db.query(models.Announcement).join(
        models.AnnouncementTarget,
        models.Announcement.id == models.AnnouncementTarget.announcement_id
    ).filter(
        and_(
            models.Announcement.is_active == True,
            models.Announcement.type == 'system',
            models.Announcement.target_type == 'specific',
            models.AnnouncementTarget.church_id == current_user.church_id,
            # 날짜 필터링
            models.Announcement.start_date <= today,
            or_(
                models.Announcement.end_date >= today,
                models.Announcement.end_date == None
            )
        )
    )
    
    # 시스템 공지사항 - 단일 교회 대상 (target_type = 'single')
    single_announcements_query = db.query(models.Announcement).filter(
        and_(
            models.Announcement.is_active == True,
            models.Announcement.type == 'system',
            models.Announcement.target_type == 'single',
            models.Announcement.church_id == current_user.church_id,
            # 날짜 필터링
            models.Announcement.start_date <= today,
            or_(
                models.Announcement.end_date >= today,
                models.Announcement.end_date == None
            )
        )
    )
    
    # 교회별 공지사항
    church_announcements = db.query(models.Announcement).filter(
        and_(
            models.Announcement.is_active == True,
            models.Announcement.church_id == current_user.church_id,
            or_(
                models.Announcement.type == 'church',
                models.Announcement.type == None  # 기존 레코드 호환성
            ),
            # 날짜 필터링: start_date <= 오늘 <= end_date (end_date가 NULL이면 무제한)
            models.Announcement.start_date <= today,
            or_(
                models.Announcement.end_date >= today,
                models.Announcement.end_date == None
            )
        )
    )
    
    # 모든 공지사항 결과 합치기
    all_announcements = (
        list(all_announcements_query.all()) +
        list(specific_announcements_query.all()) + 
        list(single_announcements_query.all()) +
        list(church_announcements.all())
    )
    
    # 우선순위 정렬: urgent > important > normal, 같은 우선순위면 created_at DESC
    def sort_key(ann):
        priority_order = {'urgent': 0, 'important': 1, 'normal': 2}
        priority = getattr(ann, 'priority', 'normal')
        return (priority_order.get(priority, 2), -ann.created_at.timestamp())
    
    all_announcements.sort(key=sort_key)
    
    return all_announcements


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
    
    # 이미 읽었는지 확인 (AnnouncementRead 모델이 있다면)
    try:
        existing_read = db.query(models.AnnouncementRead).filter(
            and_(
                models.AnnouncementRead.announcement_id == announcement_id,
                models.AnnouncementRead.user_id == current_user.id
            )
        ).first()
        
        if not existing_read:
            # 읽음 기록 추가
            read_record = models.AnnouncementRead(
                announcement_id=announcement_id,
                user_id=current_user.id
            )
            db.add(read_record)
            db.commit()
    except:
        # AnnouncementRead 모델이 없는 경우 패스
        pass
    
    return {"success": True, "message": "읽음 처리 완료"}


@router.get("/admin", response_model=List[schemas.Announcement])
def get_all_announcements_admin(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    모든 공지사항 조회 (시스템 관리자용)
    권한: church_id = 0인 사용자만
    """
    if current_user.church_id != 0:
        raise HTTPException(
            status_code=403, 
            detail="시스템 관리자만 접근 가능합니다"
        )
    
    announcements = db.query(models.Announcement).order_by(
        desc(models.Announcement.created_at)
    ).all()
    
    return announcements


@router.get("/categories", response_model=Dict[str, Any])
def get_announcement_categories(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get available announcement categories and subcategories.
    """
    return get_categories()


@router.get("/churches", response_model=List[Dict[str, Any]])
def get_churches_for_announcement(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    공지사항 대상 교회 목록 조회 (시스템 관리자용)
    권한: church_id = 0인 사용자만
    """
    if current_user.church_id != 0:
        raise HTTPException(
            status_code=403,
            detail="시스템 관리자만 접근 가능합니다"
        )
    
    churches = db.query(models.Church).filter(
        and_(
            models.Church.is_active == True,
            models.Church.id != 0  # 시스템 교회 제외
        )
    ).order_by(models.Church.name).all()
    
    return [
        {
            "id": church.id,
            "name": church.name,
            "pastor_name": church.pastor_name,
            "address": church.address,
            "member_count": getattr(church, 'member_count', 0)
        }
        for church in churches
    ]


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
    
    target_type 옵션:
    - 'all': 모든 교회에 공지 (church_id = NULL, target_church_ids 무시)
    - 'specific': 특정 교회들에만 공지 (church_id = NULL, target_church_ids 사용)  
    - 'single': 단일 교회에만 공지 (기존 방식, church_id 사용)
    """
    if current_user.church_id != 0:
        raise HTTPException(
            status_code=403,
            detail="시스템 관리자만 접근 가능합니다"
        )
    
    announcement_data = announcement_in.dict(exclude={'target_church_ids'})
    target_church_ids = getattr(announcement_in, 'target_church_ids', [])
    target_type = getattr(announcement_in, 'target_type', 'all')
    
    # target_type에 따른 church_id 설정
    if target_type == 'all':
        announcement_data.update({
            'church_id': None,
            'target_type': 'all'
        })
    elif target_type == 'specific':
        if not target_church_ids:
            raise HTTPException(status_code=400, detail="특정 교회 선택 시 target_church_ids가 필요합니다")
        announcement_data.update({
            'church_id': None,
            'target_type': 'specific'
        })
    elif target_type == 'single':
        if not announcement_data.get('church_id'):
            raise HTTPException(status_code=400, detail="단일 교회 선택 시 church_id가 필요합니다")
        announcement_data['target_type'] = 'single'
    
    announcement_data.update({
        'type': 'system',
        'created_by': current_user.id,
        'author_id': current_user.id,
        'author_name': current_user.full_name or current_user.username,
    })
    
    # 공지사항 생성
    announcement = models.Announcement(**announcement_data)
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    
    # 특정 교회들 선택한 경우 대상 교회 저장
    if target_type == 'specific' and target_church_ids:
        for church_id in target_church_ids:
            target = models.AnnouncementTarget(
                announcement_id=announcement.id,
                church_id=church_id
            )
            db.add(target)
        db.commit()
    
    return announcement


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
