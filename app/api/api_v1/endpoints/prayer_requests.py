from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from app import models, schemas
from app.api import deps
from app.models.pastoral_care import PrayerRequest, PrayerParticipation
from app.schemas.pastoral_care import (
    PrayerRequestCreate,
    PrayerRequestUpdate,
    PrayerRequestTestimony,
    PrayerRequestAdminUpdate,
    PrayerRequest as PrayerRequestSchema,
    PrayerRequestList,
    PrayerRequestStats,
    PrayerParticipation as PrayerParticipationSchema,
)

router = APIRouter()


# Mobile User Endpoints
@router.post("/", response_model=PrayerRequestSchema)
def create_prayer_request(
    *,
    db: Session = Depends(deps.get_db),
    request_in: PrayerRequestCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new prayer request.
    """
    # If anonymous, clear requester info
    request_data = request_in.dict()
    if request_data.get("is_anonymous"):
        request_data["requester_name"] = "익명"
        request_data["requester_phone"] = None

    request = PrayerRequest(
        **request_data,
        church_id=current_user.church_id,
        member_id=current_user.id if not request_in.is_anonymous else None,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/", response_model=List[PrayerRequestSchema])
def read_public_prayer_requests(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    prayer_type: Optional[str] = None,
    is_urgent: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve public prayer requests.
    """
    query = db.query(PrayerRequest).filter(
        PrayerRequest.church_id == current_user.church_id,
        PrayerRequest.is_public == True,
        PrayerRequest.status == "active",
        PrayerRequest.expires_at > datetime.now(),
    )

    if prayer_type:
        query = query.filter(PrayerRequest.prayer_type == prayer_type)

    if is_urgent is not None:
        query = query.filter(PrayerRequest.is_urgent == is_urgent)

    # Order by urgent first, then by created_at
    requests = (
        query.order_by(PrayerRequest.is_urgent.desc(), desc(PrayerRequest.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return requests


@router.get("/my", response_model=List[PrayerRequestSchema])
def read_my_prayer_requests(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve my prayer requests.
    """
    query = db.query(PrayerRequest).filter(
        PrayerRequest.member_id == current_user.id,
        PrayerRequest.church_id == current_user.church_id,
    )

    if status:
        query = query.filter(PrayerRequest.status == status)

    requests = (
        query.order_by(desc(PrayerRequest.created_at)).offset(skip).limit(limit).all()
    )

    return requests


@router.post("/{request_id}/pray", response_model=dict)
def participate_in_prayer(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Participate in prayer for a request.
    """
    # Check if prayer request exists and is public
    request = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.id == request_id,
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.is_public == True,
            PrayerRequest.status == "active",
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404, detail="Prayer request not found or not public"
        )

    # Check if already participated
    existing = (
        db.query(PrayerParticipation)
        .filter(
            PrayerParticipation.prayer_request_id == request_id,
            PrayerParticipation.member_id == current_user.id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="You have already prayed for this request"
        )

    # Create participation
    participation = PrayerParticipation(
        prayer_request_id=request_id,
        member_id=current_user.id,
        church_id=current_user.church_id,
    )
    db.add(participation)

    # Update prayer count
    request.prayer_count += 1

    db.commit()

    return {
        "success": True,
        "message": "Prayer participation recorded",
        "total_prayers": request.prayer_count,
    }


@router.put("/{request_id}", response_model=PrayerRequestSchema)
def update_prayer_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    request_in: PrayerRequestUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update prayer request (only by owner).
    """
    request = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.id == request_id, PrayerRequest.member_id == current_user.id
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Prayer request not found")

    if request.status != "active":
        raise HTTPException(status_code=400, detail="Can only update active requests")

    update_data = request_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.put("/{request_id}/testimony", response_model=PrayerRequestSchema)
def add_answered_testimony(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    testimony: PrayerRequestTestimony,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add answered testimony to prayer request.
    """
    request = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.id == request_id, PrayerRequest.member_id == current_user.id
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Prayer request not found")

    request.answered_testimony = testimony.answered_testimony
    request.status = "answered"
    request.closed_at = datetime.now()

    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}")
def delete_prayer_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete/close prayer request.
    """
    request = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.id == request_id, PrayerRequest.member_id == current_user.id
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Prayer request not found")

    request.status = "closed"
    request.closed_at = datetime.now()

    db.commit()

    return {"success": True, "message": "Prayer request closed successfully"}


# Admin Endpoints
@router.get("/admin/all", response_model=PrayerRequestList)
def read_all_prayer_requests(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    is_public: Optional[bool] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all prayer requests for admin (including private).
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    query = db.query(PrayerRequest).filter(
        PrayerRequest.church_id == current_user.church_id
    )

    if status:
        query = query.filter(PrayerRequest.status == status)
    if is_public is not None:
        query = query.filter(PrayerRequest.is_public == is_public)

    total = query.count()
    skip = (page - 1) * per_page

    requests = (
        query.order_by(PrayerRequest.is_urgent.desc(), desc(PrayerRequest.created_at))
        .offset(skip)
        .limit(per_page)
        .all()
    )

    return {"items": requests, "total": total, "page": page, "per_page": per_page}


@router.get("/admin/{request_id}", response_model=PrayerRequestSchema)
def read_prayer_request_detail(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific prayer request detail for admin.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.id == request_id,
            PrayerRequest.church_id == current_user.church_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Prayer request not found")

    return request


@router.put("/admin/{request_id}", response_model=PrayerRequestSchema)
def admin_update_prayer_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    request_in: PrayerRequestAdminUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update prayer request status/visibility (admin only).
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.id == request_id,
            PrayerRequest.church_id == current_user.church_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Prayer request not found")

    update_data = request_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    if request_in.status == "closed":
        request.closed_at = datetime.now()

    db.commit()
    db.refresh(request)
    return request


@router.put("/admin/{request_id}/moderate", response_model=PrayerRequestSchema)
def moderate_prayer_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    is_approved: bool,
    admin_notes: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Approve or reject prayer request for public viewing.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.id == request_id,
            PrayerRequest.church_id == current_user.church_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Prayer request not found")

    request.is_public = is_approved
    if admin_notes:
        request.admin_notes = admin_notes

    db.commit()
    db.refresh(request)
    return request


@router.get("/admin/stats", response_model=PrayerRequestStats)
def get_prayer_request_statistics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get prayer request statistics for admin dashboard.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Total requests
    total_requests = (
        db.query(PrayerRequest)
        .filter(PrayerRequest.church_id == current_user.church_id)
        .count()
    )

    # Count by status
    active_count = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.status == "active",
        )
        .count()
    )

    answered_count = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.status == "answered",
        )
        .count()
    )

    closed_count = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.status == "closed",
        )
        .count()
    )

    # Urgent and public counts
    urgent_count = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.is_urgent == True,
            PrayerRequest.status == "active",
        )
        .count()
    )

    public_count = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.is_public == True,
        )
        .count()
    )

    # Total prayers
    total_prayers = (
        db.query(func.sum(PrayerRequest.prayer_count))
        .filter(PrayerRequest.church_id == current_user.church_id)
        .scalar()
        or 0
    )

    # Answered this month
    from datetime import datetime

    start_of_month = datetime.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    answered_this_month = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.status == "answered",
            PrayerRequest.closed_at >= start_of_month,
        )
        .count()
    )

    return {
        "total_requests": total_requests,
        "active_count": active_count,
        "answered_count": answered_count,
        "closed_count": closed_count,
        "urgent_count": urgent_count,
        "public_count": public_count,
        "total_prayers": total_prayers,
        "answered_this_month": answered_this_month,
    }


@router.get("/admin/bulletin", response_model=List[PrayerRequestSchema])
def get_bulletin_prayer_requests(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=50),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get prayer requests for church bulletin.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Get public, active prayer requests ordered by urgency and date
    requests = (
        db.query(PrayerRequest)
        .filter(
            PrayerRequest.church_id == current_user.church_id,
            PrayerRequest.is_public == True,
            PrayerRequest.status == "active",
            PrayerRequest.expires_at > datetime.now(),
        )
        .order_by(PrayerRequest.is_urgent.desc(), desc(PrayerRequest.created_at))
        .limit(limit)
        .all()
    )

    return requests
