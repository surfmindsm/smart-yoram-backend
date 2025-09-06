from typing import Any, List, Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_

from app import models, schemas
from app.api import deps
from app.schemas.activity_log import (
    ActivityLogBatch, ActivityLogCreateResponse, ActivityLogErrorResponse,
    ActivityLogListResponse, ActivityLogQuery, ActivityLogStats,
    ActivityLogSummary, ActivityLogResponse
)
from app.utils.activity_logger import activity_logger

router = APIRouter()


@router.post("", response_model=ActivityLogCreateResponse)
async def create_activity_logs(
    log_batch: ActivityLogBatch,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Store activity logs in batch for GDPR/Privacy law compliance
    
    All users can log their activities, but IP address and User-Agent 
    are extracted server-side for security.
    """
    try:
        # Validate that all logs belong to the current user (security check)
        for log in log_batch.logs:
            if log.user_id != str(current_user.id):
                raise HTTPException(
                    status_code=403,
                    detail=f"Cannot create logs for other users. Expected user_id: {current_user.id}"
                )
        
        # Process batch with automatic IP and session detection
        result = await activity_logger.log_batch_activities(db, log_batch.logs, request)
        
        if result["success"]:
            return ActivityLogCreateResponse(
                success=True,
                message="활동 로그가 성공적으로 저장되었습니다",
                inserted_count=result["inserted_count"],
                timestamp=result["timestamp"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Activity log creation error: {e}")
        raise HTTPException(status_code=500, detail=f"로그 저장 실패: {str(e)}")


@router.get("", response_model=ActivityLogListResponse)
def get_activity_logs(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    limit: int = Query(default=50, ge=1, le=200, description="페이지당 항목 수"),
    user_id: Optional[str] = Query(None, description="특정 사용자 필터링"),
    action: Optional[str] = Query(None, description="액션 타입 필터링"),
    resource: Optional[str] = Query(None, description="리소스 타입 필터링"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="대상 이름 검색"),
    ip_address: Optional[str] = Query(None, description="IP 주소 필터링")
) -> Any:
    """
    Get activity logs with filtering and pagination
    
    Admin users can view all logs, regular users can only view their own logs.
    """
    try:
        # Permission check: Only admins can view all logs
        if not current_user.is_superuser and not current_user.role == "admin":
            # Regular users can only see their own logs
            if user_id and user_id != str(current_user.id):
                raise HTTPException(
                    status_code=403,
                    detail="일반 사용자는 본인의 로그만 조회할 수 있습니다"
                )
            user_id = str(current_user.id)
        
        # Build base query
        query = db.query(models.ActivityLog)
        
        # Apply filters
        if user_id:
            query = query.filter(models.ActivityLog.user_id == user_id)
        
        if action:
            try:
                action_enum = models.ActionType(action)
                query = query.filter(models.ActivityLog.action == action_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"유효하지 않은 액션: {action}")
        
        if resource:
            try:
                resource_enum = models.ResourceType(resource)
                query = query.filter(models.ActivityLog.resource == resource_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"유효하지 않은 리소스: {resource}")
        
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(models.ActivityLog.timestamp >= start_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="시작 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
        
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(models.ActivityLog.timestamp < end_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="종료 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
        
        if search:
            query = query.filter(
                or_(
                    models.ActivityLog.target_name.ilike(f"%{search}%"),
                    models.ActivityLog.page_name.ilike(f"%{search}%")
                )
            )
        
        if ip_address:
            query = query.filter(models.ActivityLog.ip_address == ip_address)
        
        # Get total count for pagination
        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit
        
        # Apply pagination and ordering
        logs = (
            query
            .order_by(desc(models.ActivityLog.timestamp))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        # Convert to summary format for list view
        log_summaries = []
        for log in logs:
            sensitive_count = len(log.sensitive_data) if log.sensitive_data else 0
            log_summaries.append({
                "id": log.id,
                "user_id": log.user_id,
                "timestamp": log.timestamp,
                "action": log.action.value,
                "resource": log.resource.value,
                "target_id": log.target_id,
                "target_name": log.target_name,
                "page_name": log.page_name,
                "ip_address": log.ip_address,
                "sensitive_data_count": sensitive_count
            })
        
        return ActivityLogListResponse(
            success=True,
            data={
                "logs": log_summaries,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Activity log query error: {e}")
        raise HTTPException(status_code=500, detail=f"로그 조회 실패: {str(e)}")


@router.get("/{log_id}", response_model=ActivityLogResponse)
def get_activity_log_detail(
    log_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed activity log by ID
    
    Only admins and the log owner can view detailed logs.
    """
    try:
        log = db.query(models.ActivityLog).filter(models.ActivityLog.id == log_id).first()
        
        if not log:
            raise HTTPException(status_code=404, detail="활동 로그를 찾을 수 없습니다")
        
        # Permission check
        if not current_user.is_superuser and not current_user.role == "admin":
            if log.user_id != str(current_user.id):
                raise HTTPException(
                    status_code=403,
                    detail="본인의 로그만 상세 조회할 수 있습니다"
                )
        
        return ActivityLogResponse(
            id=log.id,
            user_id=log.user_id,
            session_id=log.session_id,
            timestamp=log.timestamp,
            action=log.action.value,
            resource=log.resource.value,
            target_id=log.target_id,
            target_name=log.target_name,
            page_path=log.page_path,
            page_name=log.page_name,
            details=log.details,
            sensitive_data=log.sensitive_data,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Activity log detail error: {e}")
        raise HTTPException(status_code=500, detail=f"로그 상세 조회 실패: {str(e)}")


@router.get("/stats/summary", response_model=ActivityLogStats)
def get_activity_log_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    user_id: Optional[str] = Query(None, description="특정 사용자 통계 (관리자만)")
) -> Any:
    """
    Get activity log statistics
    
    Admins can view all stats, regular users only see their own stats.
    """
    try:
        # Permission check
        if not current_user.is_superuser and not current_user.role == "admin":
            user_id = str(current_user.id)
        
        # Base query
        base_query = db.query(models.ActivityLog)
        if user_id:
            base_query = base_query.filter(models.ActivityLog.user_id == user_id)
        
        # Calculate time ranges
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Total logs
        total_logs = base_query.count()
        
        # Today's logs
        today_logs = base_query.filter(models.ActivityLog.timestamp >= today_start).count()
        
        # Week's logs
        week_logs = base_query.filter(models.ActivityLog.timestamp >= week_start).count()
        
        # Month's logs
        month_logs = base_query.filter(models.ActivityLog.timestamp >= month_start).count()
        
        # Action breakdown
        action_stats = (
            db.query(
                models.ActivityLog.action,
                func.count(models.ActivityLog.id).label('count')
            )
            .filter(models.ActivityLog.user_id == user_id if user_id else True)
            .group_by(models.ActivityLog.action)
            .all()
        )
        action_breakdown = {action.value: count for action, count in action_stats}
        
        # Resource breakdown
        resource_stats = (
            db.query(
                models.ActivityLog.resource,
                func.count(models.ActivityLog.id).label('count')
            )
            .filter(models.ActivityLog.user_id == user_id if user_id else True)
            .group_by(models.ActivityLog.resource)
            .all()
        )
        resource_breakdown = {resource.value: count for resource, count in resource_stats}
        
        # Top users (admin only)
        top_users = []
        if current_user.is_superuser or current_user.role == "admin":
            user_stats = (
                db.query(
                    models.ActivityLog.user_id,
                    func.count(models.ActivityLog.id).label('count')
                )
                .group_by(models.ActivityLog.user_id)
                .order_by(desc('count'))
                .limit(10)
                .all()
            )
            top_users = [{"user_id": user_id, "log_count": count} for user_id, count in user_stats]
        
        # Sensitive data access count
        sensitive_query = base_query.filter(
            models.ActivityLog.sensitive_data.isnot(None)
        )
        sensitive_data_access_count = sensitive_query.count()
        
        return ActivityLogStats(
            total_logs=total_logs,
            today_logs=today_logs,
            week_logs=week_logs,
            month_logs=month_logs,
            action_breakdown=action_breakdown,
            resource_breakdown=resource_breakdown,
            top_users=top_users,
            sensitive_data_access_count=sensitive_data_access_count
        )
        
    except Exception as e:
        print(f"Activity log stats error: {e}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_old_logs(
    days: int = Query(default=2555, description="삭제할 로그의 기준 일수 (기본: 7년)"),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Clean up old activity logs for GDPR/Privacy law compliance
    
    Only super administrators can perform cleanup operations.
    Default: Delete logs older than 7 years (2555 days)
    """
    try:
        # Only superusers can perform cleanup
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="로그 정리는 슈퍼 관리자만 수행할 수 있습니다"
            )
        
        deleted_count = await activity_logger.cleanup_old_logs(db, days)
        
        return {
            "success": True,
            "message": f"{days}일 이전 로그 정리 완료",
            "deleted_count": deleted_count,
            "cleanup_date": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Log cleanup error: {e}")
        raise HTTPException(status_code=500, detail=f"로그 정리 실패: {str(e)}")


# Export endpoint for compliance reporting
@router.get("/export/csv")
def export_activity_logs_csv(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_date: str = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="종료 날짜 (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="특정 사용자 필터링")
) -> Any:
    """
    Export activity logs to CSV for compliance reporting
    
    Only administrators can export logs.
    """
    try:
        # Only admins can export
        if not current_user.is_superuser and not current_user.role == "admin":
            raise HTTPException(
                status_code=403,
                detail="로그 내보내기는 관리자만 수행할 수 있습니다"
            )
        
        # This would implement CSV export functionality
        # For now, return a success message
        return {
            "success": True,
            "message": "CSV 내보내기 기능은 구현 예정입니다",
            "export_params": {
                "start_date": start_date,
                "end_date": end_date,
                "user_id": user_id,
                "requested_by": current_user.id,
                "requested_at": datetime.utcnow()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Log export error: {e}")
        raise HTTPException(status_code=500, detail=f"내보내기 실패: {str(e)}")