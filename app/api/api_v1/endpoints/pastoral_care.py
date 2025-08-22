from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from app import models, schemas
from app.api import deps
from app.models.pastoral_care import PastoralCareRequest
from app.schemas.pastoral_care import (
    PastoralCareRequestCreate,
    PastoralCareRequestUpdate,
    PastoralCareRequestAdminUpdate,
    PastoralCareRequestComplete,
    PastoralCareRequest as PastoralCareRequestSchema,
    PastoralCareRequestList,
    PastoralCareStats,
    LocationQuery,
    PastoralCareRequestWithDistance,
)

router = APIRouter()


# Mobile User Endpoints
@router.post("/requests", response_model=PastoralCareRequestSchema)
def create_pastoral_care_request(
    *,
    db: Session = Depends(deps.get_db),
    request_in: PastoralCareRequestCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new pastoral care request.
    """
    request = PastoralCareRequest(
        **request_in.dict(), church_id=current_user.church_id, member_id=current_user.id
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/requests/my", response_model=List[PastoralCareRequestSchema])
def read_my_pastoral_care_requests(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve my pastoral care requests.
    """
    query = db.query(PastoralCareRequest).filter(
        PastoralCareRequest.member_id == current_user.id,
        PastoralCareRequest.church_id == current_user.church_id,
    )

    if status:
        query = query.filter(PastoralCareRequest.status == status)

    requests = (
        query.order_by(desc(PastoralCareRequest.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return requests


@router.put("/requests/{request_id}", response_model=PastoralCareRequestSchema)
def update_pastoral_care_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    request_in: PastoralCareRequestUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update pastoral care request (only when status is pending).
    """
    request = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.id == request_id,
            PastoralCareRequest.member_id == current_user.id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Pastoral care request not found")

    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Can only update pending requests")

    update_data = request_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.delete("/requests/{request_id}")
def delete_pastoral_care_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancel pastoral care request (only when status is pending).
    """
    request = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.id == request_id,
            PastoralCareRequest.member_id == current_user.id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Pastoral care request not found")

    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Can only cancel pending requests")

    request.status = "cancelled"
    db.commit()

    return {"success": True, "message": "Request cancelled successfully"}


# Admin Endpoints
@router.get("/admin/requests", response_model=PastoralCareRequestList)
def read_all_pastoral_care_requests(
    *,
    db: Session = Depends(deps.get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all pastoral care requests for admin.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    query = db.query(PastoralCareRequest).filter(
        PastoralCareRequest.church_id == current_user.church_id
    )

    if status:
        query = query.filter(PastoralCareRequest.status == status)
    if priority:
        query = query.filter(PastoralCareRequest.priority == priority)

    total = query.count()
    skip = (page - 1) * per_page

    requests = (
        query.order_by(
            PastoralCareRequest.priority.desc(), desc(PastoralCareRequest.created_at)
        )
        .offset(skip)
        .limit(per_page)
        .all()
    )

    return {"items": requests, "total": total, "page": page, "per_page": per_page}


@router.get("/admin/requests/{request_id}", response_model=PastoralCareRequestSchema)
def read_pastoral_care_request_detail(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get specific pastoral care request detail for admin.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.id == request_id,
            PastoralCareRequest.church_id == current_user.church_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Pastoral care request not found")

    return request


@router.put("/admin/requests/{request_id}", response_model=PastoralCareRequestSchema)
def admin_update_pastoral_care_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    request_in: PastoralCareRequestAdminUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update pastoral care request status/schedule (admin only).
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.id == request_id,
            PastoralCareRequest.church_id == current_user.church_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Pastoral care request not found")

    update_data = request_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.put(
    "/admin/requests/{request_id}/assign", response_model=PastoralCareRequestSchema
)
def assign_pastor_to_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    pastor_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Assign pastor to pastoral care request.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.id == request_id,
            PastoralCareRequest.church_id == current_user.church_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Pastoral care request not found")

    # Verify pastor exists and is a minister
    pastor = (
        db.query(models.User)
        .filter(
            models.User.id == pastor_id,
            models.User.church_id == current_user.church_id,
            models.User.role.in_(["admin", "minister"]),
        )
        .first()
    )

    if not pastor:
        raise HTTPException(
            status_code=404, detail="Pastor not found or not authorized"
        )

    request.assigned_pastor_id = pastor_id
    request.status = "approved"

    db.commit()
    db.refresh(request)
    return request


@router.post(
    "/admin/requests/{request_id}/complete", response_model=PastoralCareRequestSchema
)
def complete_pastoral_care_request(
    *,
    db: Session = Depends(deps.get_db),
    request_id: int,
    completion: PastoralCareRequestComplete,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark pastoral care request as completed.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    request = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.id == request_id,
            PastoralCareRequest.church_id == current_user.church_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(status_code=404, detail="Pastoral care request not found")

    request.status = "completed"
    request.completion_notes = completion.completion_notes
    request.completed_at = datetime.now()

    db.commit()
    db.refresh(request)
    return request


@router.get("/admin/stats", response_model=PastoralCareStats)
def get_pastoral_care_statistics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get pastoral care statistics for admin dashboard.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Total requests
    total_requests = (
        db.query(PastoralCareRequest)
        .filter(PastoralCareRequest.church_id == current_user.church_id)
        .count()
    )

    # Count by status
    pending_count = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.status == "pending",
        )
        .count()
    )

    scheduled_count = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.status == "scheduled",
        )
        .count()
    )

    completed_count = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.status == "completed",
        )
        .count()
    )

    # Completed this month
    from datetime import datetime, timedelta

    start_of_month = datetime.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    completed_this_month = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.status == "completed",
            PastoralCareRequest.completed_at >= start_of_month,
        )
        .count()
    )

    # Urgent count
    urgent_count = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.priority == "urgent",
            PastoralCareRequest.status.in_(["pending", "approved", "scheduled"]),
        )
        .count()
    )

    # Calculate average completion days
    completed_requests = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.status == "completed",
            PastoralCareRequest.completed_at.isnot(None),
        )
        .all()
    )

    total_days = 0
    count = 0
    for req in completed_requests:
        if req.completed_at and req.created_at:
            days = (req.completed_at - req.created_at).days
            total_days += days
            count += 1

    average_completion_days = total_days / count if count > 0 else 0

    return {
        "total_requests": total_requests,
        "pending_count": pending_count,
        "scheduled_count": scheduled_count,
        "completed_count": completed_count,
        "completed_this_month": completed_this_month,
        "urgent_count": urgent_count,
        "average_completion_days": average_completion_days,
    }


# Location-based endpoints
@router.post("/admin/requests/search/location", response_model=List[PastoralCareRequestWithDistance])
def search_requests_by_location(
    *,
    db: Session = Depends(deps.get_db),
    location_query: LocationQuery,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search pastoral care requests by location (admin only).
    Returns requests within specified radius with distance calculation.
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    from decimal import Decimal
    import math
    
    query = db.query(PastoralCareRequest).filter(
        PastoralCareRequest.church_id == current_user.church_id,
        PastoralCareRequest.latitude.isnot(None),
        PastoralCareRequest.longitude.isnot(None),
    )
    
    requests = query.all()
    requests_with_distance = []
    
    # Calculate distance for each request
    for request in requests:
        if request.latitude and request.longitude:
            # Haversine formula for distance calculation
            lat1, lon1 = float(location_query.latitude), float(location_query.longitude)
            lat2, lon2 = float(request.latitude), float(request.longitude)
            
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance = 6371 * c  # Radius of Earth in km
            
            # Only include requests within the specified radius
            if distance <= location_query.radius_km:
                # Convert request to dict and add distance
                request_dict = {
                    **{column.name: getattr(request, column.name) for column in request.__table__.columns},
                    "distance_km": round(distance, 2)
                }
                requests_with_distance.append(request_dict)
    
    # Sort by distance
    requests_with_distance.sort(key=lambda x: x["distance_km"])
    
    return requests_with_distance


@router.get("/admin/requests/urgent", response_model=List[PastoralCareRequestSchema])
def get_urgent_requests(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all urgent pastoral care requests (admin only).
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    requests = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.is_urgent == True,
            PastoralCareRequest.status.in_(["pending", "approved", "scheduled"])
        )
        .order_by(desc(PastoralCareRequest.created_at))
        .all()
    )
    
    return requests


@router.get("/admin/requests/with-location", response_model=List[PastoralCareRequestSchema])
def get_requests_with_location(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all pastoral care requests that have location information (admin only).
    """
    # Check admin permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    requests = (
        db.query(PastoralCareRequest)
        .filter(
            PastoralCareRequest.church_id == current_user.church_id,
            PastoralCareRequest.latitude.isnot(None),
            PastoralCareRequest.longitude.isnot(None),
        )
        .order_by(desc(PastoralCareRequest.created_at))
        .all()
    )
    
    return requests
