from typing import Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app import models
from app.api import deps
from app.schemas.simple_login_history import (
    LoginHistoryResponse,
    LoginHistoryRecent,
    LoginHistoryList
)
from app.utils.simple_login_tracker import get_recent_login

router = APIRouter()


@router.get("/recent", response_model=LoginHistoryRecent)
def get_recent_login_info(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    최근 로그인 정보 조회 (헤더 표시용)
    안전하게 구현 - 실패해도 빈 데이터 반환
    """
    try:
        recent_login = get_recent_login(db, current_user.id)
        
        if not recent_login:
            return LoginHistoryRecent(
                id=None,
                timestamp=None,
                ip_address=None,
                device_info=None,
                location="위치 정보 없음"
            )
        
        # 간단한 device info 생성
        device_info = "알 수 없는 기기"
        if recent_login.device_type:
            device_info = f"{recent_login.device_type.title()}"
            if recent_login.user_agent:
                # 브라우저 정보 간단히 추출
                user_agent = recent_login.user_agent.lower()
                if "chrome" in user_agent:
                    device_info += " - Chrome"
                elif "firefox" in user_agent:
                    device_info += " - Firefox"
                elif "safari" in user_agent and "chrome" not in user_agent:
                    device_info += " - Safari"
                elif "edge" in user_agent:
                    device_info += " - Edge"
        
        return LoginHistoryRecent(
            id=recent_login.id,
            timestamp=recent_login.timestamp,
            ip_address=recent_login.ip_address,
            device_info=device_info,
            location=recent_login.location or "위치 정보 없음"
        )
        
    except Exception as e:
        print(f"⚠️ GET RECENT LOGIN ERROR: {str(e)}")
        # 에러 발생해도 빈 데이터 반환 (안전)
        return LoginHistoryRecent(
            id=None,
            timestamp=None,
            ip_address=None,
            device_info=None,
            location="위치 정보 없음"
        )


@router.get("", response_model=LoginHistoryList)
def get_login_history(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    limit: int = Query(default=20, ge=1, le=100, description="페이지당 항목 수"),
    start_date: Optional[str] = Query(None, description="조회 시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="조회 종료일 (YYYY-MM-DD)")
) -> Any:
    """
    로그인 기록 목록 조회
    사용자는 본인 기록만, 관리자는 모든 기록 조회 가능
    """
    try:
        # 권한 확인
        if current_user.is_superuser:
            # 관리자는 모든 사용자 기록 조회 가능
            query = db.query(models.LoginHistory)
        else:
            # 일반 사용자는 본인 기록만 조회 가능
            query = db.query(models.LoginHistory).filter(
                models.LoginHistory.user_id == current_user.id
            )
        
        # 날짜 필터 적용
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(models.LoginHistory.timestamp >= start_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="시작 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
        
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
                query = query.filter(models.LoginHistory.timestamp < end_datetime)
            except ValueError:
                raise HTTPException(status_code=400, detail="종료 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD)")
        
        # 총 개수 조회
        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit
        
        # 페이지네이션 적용
        records = (
            query
            .order_by(desc(models.LoginHistory.timestamp))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return LoginHistoryList(
            records=records,
            pagination={
                "total": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ GET LOGIN HISTORY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 기록 조회 실패: {str(e)}")


@router.get("/stats")
def get_login_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    로그인 통계 정보
    관리자만 접근 가능
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다")
        
        from sqlalchemy import func
        
        # 총 로그인 횟수
        total_logins = db.query(models.LoginHistory).filter(
            models.LoginHistory.status == "success"
        ).count()
        
        # 실패한 로그인 횟수
        failed_logins = db.query(models.LoginHistory).filter(
            models.LoginHistory.status == "failed"
        ).count()
        
        # 오늘 로그인
        today = datetime.utcnow().date()
        today_logins = db.query(models.LoginHistory).filter(
            func.date(models.LoginHistory.timestamp) == today,
            models.LoginHistory.status == "success"
        ).count()
        
        # 주간 로그인 (최근 7일)
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_logins = db.query(models.LoginHistory).filter(
            models.LoginHistory.timestamp >= week_ago,
            models.LoginHistory.status == "success"
        ).count()
        
        # 디바이스별 통계
        device_stats = db.query(
            models.LoginHistory.device_type,
            func.count(models.LoginHistory.id).label('count')
        ).filter(
            models.LoginHistory.status == "success",
            models.LoginHistory.device_type.isnot(None)
        ).group_by(models.LoginHistory.device_type).all()
        
        device_breakdown = {device: count for device, count in device_stats}
        
        return {
            "total_logins": total_logins,
            "failed_logins": failed_logins,
            "today_logins": today_logins,
            "week_logins": week_logins,
            "device_breakdown": device_breakdown
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ GET LOGIN STATS ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")


@router.post("/cleanup")
def cleanup_old_records(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    days: int = Query(default=365, description="삭제할 기록의 기준 일수")
) -> Any:
    """
    오래된 로그인 기록 삭제
    관리자만 접근 가능
    """
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다")
        
        from app.utils.simple_login_tracker import cleanup_old_records
        
        deleted_count = cleanup_old_records(db, days)
        
        return {
            "success": True,
            "message": f"{days}일 이전 로그인 기록 정리 완료",
            "deleted_count": deleted_count,
            "cleanup_date": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ CLEANUP ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"정리 작업 실패: {str(e)}")