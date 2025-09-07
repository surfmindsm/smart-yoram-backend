import re
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app import models


def get_client_ip(request: Request) -> Optional[str]:
    """
    안전한 클라이언트 IP 추출
    실패해도 None 반환하여 로그인에 영향 없음
    """
    try:
        # 프록시 헤더들 확인
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # 클라이언트 정보
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None
    except Exception:
        return None


def get_device_type(user_agent: Optional[str]) -> Optional[str]:
    """
    User-Agent에서 기기 타입 추출
    실패해도 None 반환
    """
    if not user_agent:
        return None
    
    try:
        user_agent = user_agent.lower()
        
        # 모바일 기기 감지
        mobile_patterns = [
            r'mobile', r'android', r'iphone', r'ipod', 
            r'blackberry', r'windows phone'
        ]
        
        for pattern in mobile_patterns:
            if re.search(pattern, user_agent):
                return "mobile"
        
        # 태블릿 감지
        tablet_patterns = [r'ipad', r'tablet', r'kindle']
        
        for pattern in tablet_patterns:
            if re.search(pattern, user_agent):
                return "tablet"
        
        # 기본값: 데스크탑
        return "desktop"
        
    except Exception:
        return None


def record_login_attempt(
    db: Session,
    user_id: int,
    request: Optional[Request] = None,
    status: str = "success"
) -> bool:
    """
    로그인 시도 기록 - 매우 안전하게 구현
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        request: FastAPI Request 객체
        status: 로그인 상태 ("success" 또는 "failed")
    
    Returns:
        bool: 기록 성공 여부 (실패해도 로그인에는 영향 없음)
    """
    try:
        # Request 정보 추출 (실패해도 계속 진행)
        ip_address = None
        user_agent = None
        device_type = None
        
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.headers.get("user-agent")
            device_type = get_device_type(user_agent)
            
            # User-Agent 길이 제한 (DB 오류 방지)
            if user_agent and len(user_agent) > 500:
                user_agent = user_agent[:500]
        
        # 로그인 기록 생성
        login_record = models.LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            device_type=device_type
        )
        
        # DB에 저장
        db.add(login_record)
        db.commit()
        
        print(f"✅ LOGIN RECORD SAVED: User {user_id}, Status: {status}, IP: {ip_address}")
        return True
        
    except Exception as e:
        # 어떤 오류가 발생해도 로그인에는 영향 없음
        print(f"⚠️ LOGIN RECORD FAILED (ignored): {str(e)}")
        try:
            db.rollback()
        except:
            pass
        return False


def record_login_success(db: Session, user_id: int, request: Optional[Request] = None) -> bool:
    """로그인 성공 기록"""
    return record_login_attempt(db, user_id, request, "success")


def record_login_failure(db: Session, user_id: int, request: Optional[Request] = None) -> bool:
    """로그인 실패 기록"""
    return record_login_attempt(db, user_id, request, "failed")


def get_recent_login(db: Session, user_id: int) -> Optional[models.LoginHistory]:
    """
    사용자의 가장 최근 로그인 기록 조회
    (현재 세션 제외하고 이전 로그인)
    """
    try:
        recent_login = (
            db.query(models.LoginHistory)
            .filter(
                models.LoginHistory.user_id == user_id,
                models.LoginHistory.status == "success"
            )
            .order_by(models.LoginHistory.timestamp.desc())
            .offset(1)  # 현재 로그인 세션 제외
            .first()
        )
        return recent_login
    except Exception as e:
        print(f"⚠️ GET RECENT LOGIN FAILED: {str(e)}")
        return None


def cleanup_old_records(db: Session, days: int = 365) -> int:
    """
    오래된 로그인 기록 정리
    기본값: 1년 (365일) 이전 기록 삭제
    """
    try:
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = (
            db.query(models.LoginHistory)
            .filter(models.LoginHistory.timestamp < cutoff_date)
            .delete()
        )
        
        db.commit()
        print(f"🗑️ CLEANUP: {deleted_count} old login records deleted")
        return deleted_count
        
    except Exception as e:
        print(f"⚠️ CLEANUP FAILED: {str(e)}")
        db.rollback()
        return 0