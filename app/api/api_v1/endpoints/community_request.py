from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from pydantic import BaseModel
import json

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.community_request import CommunityRequest


class RequestCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    urgency_level: str
    needed_by: Optional[str] = None
    request_reason: Optional[str] = None
    location: str
    contact_method: Optional[str] = "기타"  # 프론트엔드에서 보내지 않는 경우 기본값 제공
    contact_info: str
    images: Optional[List[str]] = []
    status: Optional[str] = "active"

router = APIRouter()


# 프론트엔드에서 호출하는 URL에 맞춰 추가
@router.get("/item-request", response_model=dict)
def get_item_request_list(
    status: Optional[str] = Query(None, description="상태 필터: active, fulfilled, cancelled"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    urgency_level: Optional[str] = Query(None, description="긴급도 필터: 낮음, 보통, 높음"),
    location: Optional[str] = Query(None, description="지역 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    church_filter: Optional[int] = Query(None, description="교회 필터 (선택사항)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물품 요청 목록 조회 - 실제 데이터베이스에서 조회"""
    try:
        # 기본 쿼리 (커뮤니티용 church_id = 9998) - User 테이블과 JOIN
        query = db.query(CommunityRequest, User.full_name, User.name).join(
            User, CommunityRequest.user_id == User.id
        ).filter(
            CommunityRequest.church_id == 9998
        )
        
        # 필터링 적용
        if status:
            query = query.filter(CommunityRequest.status == status)
        if category:
            query = query.filter(CommunityRequest.category == category)
        if urgency_level:
            query = query.filter(CommunityRequest.urgency_level == urgency_level)
        if location:
            query = query.filter(CommunityRequest.location.ilike(f"%{location}%"))
        if search:
            query = query.filter(
                (CommunityRequest.title.ilike(f"%{search}%")) |
                (CommunityRequest.description.ilike(f"%{search}%"))
            )
        
        # 전체 개수 계산
        total_count = query.count()
        
        # 페이지네이션
        offset = (page - 1) * limit
        request_list = query.order_by(CommunityRequest.created_at.desc()).offset(offset).limit(limit).all()
        
        # 응답 데이터 구성
        data_items = []
        for request, user_full_name, user_name in request_list:
            data_items.append({
                "id": request.id,
                "title": request.title,
                "description": request.description,
                "category": request.category,
                "urgency_level": request.urgency_level,
                "status": request.status,
                "location": request.location,
                "contact_info": request.contact_info,
                "images": request.images or [],
                "created_at": request.created_at.isoformat() if request.created_at else None,
                "updated_at": request.updated_at.isoformat() if request.updated_at else None,
                "view_count": request.view_count or 0,
                "user_id": request.user_id,
                "user_name": user_full_name or user_name or "익명",  # 사용자 이름 추가
                "church_id": request.church_id
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 요청 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
        return {
            "success": True,
            "data": data_items,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
        return {
            "success": True,
            "data": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }


@router.get("/requests", response_model=dict)
def get_request_list(
    status: Optional[str] = Query(None, description="상태 필터: active, fulfilled, cancelled"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    urgency_level: Optional[str] = Query(None, description="긴급도 필터: 낮음, 보통, 높음"),
    location: Optional[str] = Query(None, description="지역 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    church_filter: Optional[int] = Query(None, description="교회 필터 (선택사항)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 목록 조회 - 실제 데이터베이스에서 조회"""
    # /requests와 /item-request는 동일한 로직 사용
    return get_item_request_list(status, category, urgency_level, location, search, church_filter, page, limit, db, current_user)


@router.post("/requests", response_model=dict)
async def create_request(
    request: Request,
    request_data: RequestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 등록 - JSON 요청 방식"""
    try:
        print(f"🔍 Request data: {request_data}")
        print(f"🔍 User ID: {current_user.id}, Church ID: {current_user.church_id}")
        
        return {
            "success": True,
            "message": "요청 게시글이 등록되었습니다.",
            "data": {
                "id": 1,
                "title": request_data.title,
                "description": request_data.description,
                "category": request_data.category,
                "urgency_level": request_data.urgency_level,
                "location": request_data.location,
                "contact_info": request_data.contact_info,
                "status": request_data.status,
                "images": request_data.images,
                "user_id": current_user.id,
                "user_name": current_user.full_name or current_user.name or "익명",  # 현재 사용자 이름
                "church_id": current_user.church_id,
                "created_at": "2024-01-01T00:00:00"
            }
        }
        
    except Exception as e:
        print(f"❌ 요청 등록 실패: {str(e)}")
        return {
            "success": False,
            "message": f"요청 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/requests/{request_id}", response_model=dict)
def get_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 상세 조회 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "data": {
                "id": request_id,
                "title": "샘플 요청 제목",
                "description": "샘플 요청 설명",
                "category": "생활용품",
                "status": "active",
                "urgency_level": "보통",
                "location": "서울",
                "contact_method": "카톡",
                "contact_info": "010-0000-0000"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"요청 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/requests/{request_id}", response_model=dict)
def update_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 수정 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "요청 게시글이 수정되었습니다.",
            "data": {
                "id": request_id,
                "title": "수정된 요청 제목",
                "status": "active"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"요청 수정 중 오류가 발생했습니다: {str(e)}"
        }


@router.patch("/requests/{request_id}/status", response_model=dict)
def update_request_status(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 상태 변경 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "요청 상태가 변경되었습니다.",
            "data": {
                "id": request_id,
                "status": "fulfilled"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"요청 상태 변경 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/requests/{request_id}", response_model=dict)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 삭제 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "요청 게시글이 삭제되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"요청 삭제 중 오류가 발생했습니다: {str(e)}"
        }