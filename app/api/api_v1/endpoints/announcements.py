from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app import models, schemas
from app.api import deps
from app.core.announcement_categories import (
    get_categories,
    validate_category,
    ANNOUNCEMENT_CATEGORIES
)

router = APIRouter()


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
    announcements = query.order_by(
        desc(models.Announcement.is_pinned),
        desc(models.Announcement.created_at)
    ).offset(skip).limit(limit).all()
    
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
            detail="Only church admins and ministers can create announcements"
        )
    
    # Validate category and subcategory
    if not validate_category(announcement_in.category, announcement_in.subcategory):
        raise HTTPException(
            status_code=400,
            detail="Invalid category or subcategory combination"
        )
    
    announcement = models.Announcement(
        **announcement_in.dict(),
        church_id=current_user.church_id,
        author_id=current_user.id,
        author_name=current_user.full_name or current_user.username
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
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    
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
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    if announcement.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Only author or admin can update
    if announcement.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the author or admin can update this announcement"
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
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    if announcement.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Only author or admin can delete
    if announcement.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the author or admin can delete this announcement"
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
            status_code=403,
            detail="Only admins can pin/unpin announcements"
        )
    
    announcement = db.query(models.Announcement).filter(
        models.Announcement.id == announcement_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    if announcement.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    announcement.is_pinned = not announcement.is_pinned
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement