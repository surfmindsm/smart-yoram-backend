from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import json

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.community_request import CommunityRequest
from app.schemas.community_request import CommunityRequest as RequestSchemas

router = APIRouter()


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
    """요청 목록 조회 - 모든 교회의 요청 게시글 조회 가능"""
    try:
        # 기본 쿼리 - 모든 교회의 요청 게시글
        query = db.query(CommunityRequest)
        
        # 선택적 교회 필터링
        if church_filter:
            query = query.filter(CommunityRequest.church_id == church_filter)
        
        # 상태 필터
        if status:
            query = query.filter(CommunityRequest.status == status)
        
        # 카테고리 필터
        if category:
            query = query.filter(CommunityRequest.category == category)
        
        # 긴급도 필터
        if urgency_level:
            query = query.filter(CommunityRequest.urgency_level == urgency_level)
        
        # 지역 필터
        if location:
            query = query.filter(CommunityRequest.location.contains(location))
        
        # 검색
        if search:
            search_filter = or_(
                CommunityRequest.title.contains(search),
                CommunityRequest.description.contains(search)
            )
            query = query.filter(search_filter)
        
        # 정렬 및 페이징 (긴급도 높은 순, 최신 순)
        total_count = query.count()
        skip = (page - 1) * limit
        request_posts = query.order_by(
            desc(CommunityRequest.urgency_level == "높음"),
            desc(CommunityRequest.urgency_level == "보통"),
            desc(CommunityRequest.created_at)
        ).offset(skip).limit(limit).all()
        
        # 페이지네이션 정보
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "data": [RequestSchemas.Response.from_orm(post) for post in request_posts],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"요청 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/requests", response_model=dict)
async def create_request(
    title: str = Form(..., description="제목"),
    description: str = Form(..., description="상세 설명"),
    category: str = Form(..., description="카테고리"),
    urgency_level: str = Form(..., description="긴급도: 낮음, 보통, 높음"),
    needed_by: Optional[str] = Form(None, description="필요한 날짜 (ISO format)"),
    request_reason: Optional[str] = Form(None, description="요청 사유"),
    location: str = Form(..., description="지역"),
    contact_method: str = Form(..., description="연락 방법"),
    contact_info: str = Form(..., description="연락처"),
    images: List[UploadFile] = File(None, description="참고 이미지 파일들"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 등록"""
    try:
        # 이미지 파일 처리 (나중에 구현)
        image_urls = []
        
        # 커뮤니티 사용자는 church_id 9998
        church_id = 9998 if current_user.church_id == 9998 else current_user.church_id
        
        # 요청 게시글 생성
        request_data = {
            "title": title,
            "description": description,
            "category": category,
            "urgency_level": urgency_level,
            "request_reason": request_reason,
            "location": location,
            "contact_method": contact_method,
            "contact_info": contact_info,
            "images": image_urls,
            "author_id": current_user.id,
            "church_id": church_id,
            "status": "active"
        }
        
        # needed_by 처리
        if needed_by:
            from datetime import datetime
            try:
                request_data["needed_by"] = datetime.fromisoformat(needed_by.replace('Z', '+00:00'))
            except:
                pass  # 날짜 파싱 실패시 무시
        
        db_request = CommunityRequest(**request_data)
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        
        return {
            "success": True,
            "message": "요청 게시글이 등록되었습니다.",
            "data": RequestSchemas.Response.from_orm(db_request)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"요청 등록 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/requests/{request_id}", response_model=dict)
def get_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 상세 조회"""
    try:
        request = db.query(CommunityRequest).filter(CommunityRequest.id == request_id).first()
        
        if not request:
            raise HTTPException(status_code=404, detail="해당 요청 게시글을 찾을 수 없습니다.")
        
        # 조회수 증가
        request.views += 1
        db.commit()
        
        return {
            "success": True,
            "data": RequestSchemas.Response.from_orm(request)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"요청 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/requests/{request_id}", response_model=dict)
def update_request(
    request_id: int,
    updates: RequestSchemas.Update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 수정"""
    try:
        request = db.query(CommunityRequest).filter(CommunityRequest.id == request_id).first()
        
        if not request:
            raise HTTPException(status_code=404, detail="해당 요청 게시글을 찾을 수 없습니다.")
        
        # 작성자만 수정 가능
        if request.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 수정할 수 있습니다.")
        
        # 업데이트
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(request, field, value)
        
        db.commit()
        db.refresh(request)
        
        return {
            "success": True,
            "message": "요청 게시글이 수정되었습니다.",
            "data": RequestSchemas.Response.from_orm(request)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"요청 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/requests/{request_id}/status", response_model=dict)
def update_request_status(
    request_id: int,
    status_update: RequestSchemas.StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 상태 변경"""
    try:
        request = db.query(CommunityRequest).filter(CommunityRequest.id == request_id).first()
        
        if not request:
            raise HTTPException(status_code=404, detail="해당 요청 게시글을 찾을 수 없습니다.")
        
        # 작성자만 상태 변경 가능
        if request.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 상태 변경할 수 있습니다.")
        
        # 상태 업데이트
        request.status = status_update.status
        if status_update.provider_info:
            request.provider_info = status_update.provider_info
        
        db.commit()
        db.refresh(request)
        
        return {
            "success": True,
            "message": "요청 상태가 변경되었습니다.",
            "data": RequestSchemas.Response.from_orm(request)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"요청 상태 변경 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/requests/{request_id}", response_model=dict)
def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 삭제"""
    try:
        request = db.query(CommunityRequest).filter(CommunityRequest.id == request_id).first()
        
        if not request:
            raise HTTPException(status_code=404, detail="해당 요청 게시글을 찾을 수 없습니다.")
        
        # 작성자만 삭제 가능 (또는 슈퍼어드민)
        if request.author_id != current_user.id and current_user.church_id != 0:
            raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 삭제할 수 있습니다.")
        
        db.delete(request)
        db.commit()
        
        return {
            "success": True,
            "message": "요청 게시글이 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"요청 삭제 중 오류가 발생했습니다: {str(e)}"
        )