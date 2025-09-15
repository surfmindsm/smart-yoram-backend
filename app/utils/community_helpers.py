"""
커뮤니티 API 공통 헬퍼 함수들
"""
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.enums.community import CommunityStatus, get_status_label
from app.schemas.community_common import PaginationResponse


def format_community_response(record: Any, post_type: str) -> Dict[str, Any]:
    """커뮤니티 게시글을 표준 응답 형식으로 변환"""
    
    # 작성자 정보 처리
    if hasattr(record, 'author') and record.author:
        author_name = record.author.full_name or "익명"
    elif hasattr(record, 'author_name') and record.author_name:
        author_name = record.author_name
    else:
        author_name = "익명"
    
    return {
        "id": record.id,
        "type": post_type,
        "title": record.title,
        "description": getattr(record, 'description', None),
        "status": record.status,
        "status_label": get_status_label(record.status),
        "author_id": record.author_id,
        "author_name": author_name,
        "church_id": getattr(record, 'church_id', None),
        "view_count": getattr(record, 'view_count', 0) or 0,
        "likes": getattr(record, 'likes', 0) or 0,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None
    }


def apply_pagination(
    query: Any, 
    page: int, 
    limit: int,
    db: Optional[Session] = None
) -> Tuple[List[Any], Dict[str, Any]]:
    """표준 페이지네이션 적용"""
    
    # 전체 개수 조회
    if hasattr(query, 'count'):
        total_count = query.count()
    elif db is not None and isinstance(query, str):
        # Raw SQL 쿼리인 경우
        count_query = f"SELECT COUNT(*) FROM ({query}) as count_subquery"
        result = db.execute(text(count_query))
        total_count = result.scalar()
    else:
        total_count = 0
    
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    offset = (page - 1) * limit
    
    # 데이터 조회
    if hasattr(query, 'offset'):
        items = query.offset(offset).limit(limit).all()
    elif db is not None and isinstance(query, str):
        # Raw SQL 쿼리인 경우
        paginated_query = f"{query} OFFSET {offset} LIMIT {limit}"
        result = db.execute(text(paginated_query))
        items = result.fetchall()
    else:
        items = []
    
    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "per_page": limit,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    
    return items, pagination


def format_contact_info(phone: str, email: Optional[str] = None, method: str = "phone") -> str:
    """연락처 정보 포맷팅 (하위 호환용)"""
    parts = [f"전화: {phone}"]
    if email:
        parts.append(f"이메일: {email}")
    if method and method != "phone":
        parts.append(f"선호 방법: {method}")
    return " | ".join(parts)


def parse_contact_info(contact_info: str) -> Dict[str, Optional[str]]:
    """통합 연락처 정보를 분리된 정보로 파싱"""
    result = {
        "phone": None,
        "email": None,
        "method": "phone"
    }
    
    if not contact_info:
        return result
    
    parts = contact_info.split(" | ")
    for part in parts:
        if part.startswith("전화:"):
            result["phone"] = part.replace("전화:", "").strip()
        elif part.startswith("이메일:"):
            result["email"] = part.replace("이메일:", "").strip()
        elif part.startswith("선호 방법:"):
            result["method"] = part.replace("선호 방법:", "").strip()
    
    return result


def standardize_status_response(old_status: str, status_type: str = "community") -> str:
    """기존 상태값을 표준 상태값으로 변환"""
    from app.enums.community import (
        map_sharing_status, 
        map_request_status, 
        map_job_status, 
        map_event_status
    )
    
    mapping_functions = {
        "sharing": map_sharing_status,
        "request": map_request_status,
        "job": map_job_status,
        "event": map_event_status
    }
    
    if status_type in mapping_functions:
        return mapping_functions[status_type](old_status)
    
    # 기본적으로 CommunityStatus 값인지 확인
    valid_statuses = [s.value for s in CommunityStatus]
    if old_status in valid_statuses:
        return old_status
    
    # 알 수 없는 상태는 active로 기본 설정
    return CommunityStatus.ACTIVE


def format_datetime_response(dt: Optional[datetime]) -> Optional[str]:
    """DateTime을 표준 ISO 형식으로 변환"""
    if dt is None:
        return None
    return dt.isoformat()


def create_standard_list_response(
    data: List[Any], 
    pagination: Dict[str, Any],
    success: bool = True,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """표준 목록 응답 생성"""
    response = {
        "success": success,
        "data": data,
        "pagination": pagination
    }
    
    if message:
        response["message"] = message
        
    return response


def create_standard_detail_response(
    data: Any,
    success: bool = True,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """표준 상세/생성/수정 응답 생성"""
    response = {
        "success": success,
        "data": data
    }
    
    if message:
        response["message"] = message
        
    return response


def create_standard_error_response(
    message: str,
    error_code: Optional[str] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """표준 오류 응답 생성"""
    response = {
        "success": False,
        "message": message
    }
    
    if error_code:
        response["error_code"] = error_code
        
    return response


# 검색 및 필터링 헬퍼
def build_search_conditions(
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    author_id: Optional[int] = None,
    church_id: Optional[int] = None
) -> Tuple[str, Dict[str, Any]]:
    """검색 조건 빌드"""
    conditions = []
    params = {}
    
    if search:
        conditions.append("(title ILIKE :search OR description ILIKE :search)")
        params["search"] = f"%{search}%"
    
    if status:
        conditions.append("status = :status")
        params["status"] = status
    
    if category:
        conditions.append("category = :category") 
        params["category"] = category
    
    if author_id:
        conditions.append("author_id = :author_id")
        params["author_id"] = author_id
    
    if church_id:
        conditions.append("church_id = :church_id")
        params["church_id"] = church_id
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    return where_clause, params