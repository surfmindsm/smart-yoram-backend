from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/recent", response_model=schemas.LoginHistoryRecent)
def get_recent_login(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the most recent login information for header display
    """
    try:
        # Get the most recent successful login (excluding the current one)
        recent_login = (
            db.query(models.LoginHistory)
            .filter(
                models.LoginHistory.user_id == current_user.id,
                models.LoginHistory.status == "success"
            )
            .order_by(desc(models.LoginHistory.login_time))
            .offset(1)  # Skip the current login session
            .first()
        )
        
        if not recent_login:
            return {
                "last_login": None,
                "ip_address": None,
                "location": None,
                "device": None
            }
        
        return {
            "last_login": recent_login.login_time,
            "ip_address": recent_login.ip_address,
            "location": recent_login.location,
            "device": recent_login.device
        }
        
    except Exception as e:
        print(f"Error fetching recent login: {e}")
        # Return empty data if error occurs
        return {
            "last_login": None,
            "ip_address": None,
            "location": None,
            "device": None
        }


@router.get("/", response_model=List[schemas.LoginHistoryDetail])
def get_login_history(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    limit: int = Query(default=20, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status: success or failed")
) -> Any:
    """
    Get detailed login history for modal display
    """
    try:
        query = db.query(models.LoginHistory).filter(
            models.LoginHistory.user_id == current_user.id
        )
        
        # Apply status filter if provided
        if status and status in ["success", "failed"]:
            query = query.filter(models.LoginHistory.status == status)
        
        # Order by login time descending and apply limit
        login_history = (
            query
            .order_by(desc(models.LoginHistory.login_time))
            .limit(limit)
            .all()
        )
        
        # Convert to response format
        result = []
        for login in login_history:
            result.append({
                "id": login.id,
                "login_time": login.login_time,
                "ip_address": login.ip_address,
                "location": login.location or "위치 정보 없음",
                "device": login.device or "기기 정보 없음",
                "status": login.status,
                "session_duration": login.session_duration or "계산 중..."
            })
        
        return result
        
    except Exception as e:
        print(f"Error fetching login history: {e}")
        return []


@router.get("/stats")
def get_login_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get login statistics for the current user
    """
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Total login count
        total_logins = (
            db.query(models.LoginHistory)
            .filter(
                models.LoginHistory.user_id == current_user.id,
                models.LoginHistory.status == "success"
            )
            .count()
        )
        
        # Failed login attempts
        failed_logins = (
            db.query(models.LoginHistory)
            .filter(
                models.LoginHistory.user_id == current_user.id,
                models.LoginHistory.status == "failed"
            )
            .count()
        )
        
        # Logins in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_logins = (
            db.query(models.LoginHistory)
            .filter(
                models.LoginHistory.user_id == current_user.id,
                models.LoginHistory.status == "success",
                models.LoginHistory.login_time >= thirty_days_ago
            )
            .count()
        )
        
        # Unique devices count
        unique_devices = (
            db.query(models.LoginHistory.device)
            .filter(
                models.LoginHistory.user_id == current_user.id,
                models.LoginHistory.status == "success",
                models.LoginHistory.device.isnot(None)
            )
            .distinct()
            .count()
        )
        
        return {
            "total_logins": total_logins,
            "failed_logins": failed_logins,
            "recent_logins_30d": recent_logins,
            "unique_devices": unique_devices
        }
        
    except Exception as e:
        print(f"Error fetching login stats: {e}")
        return {
            "total_logins": 0,
            "failed_logins": 0,
            "recent_logins_30d": 0,
            "unique_devices": 0
        }