from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import json

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.community_sharing import CommunitySharing
from app.schemas.community_sharing import CommunitySharing as SharingSchemas
from app.utils.file_handler import file_handler, COMMUNITY_ALLOWED_EXTENSIONS, COMMUNITY_MAX_FILE_SIZE, COMMUNITY_MAX_FILES

router = APIRouter()


@router.get("/sharing", response_model=dict)
def get_sharing_list(
    status: Optional[str] = Query(None, description="상태 필터: available, reserved, completed"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    location: Optional[str] = Query(None, description="지역 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    church_filter: Optional[int] = Query(None, description="교회 필터 (선택사항)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 목록 조회 - 모든 교회의 나눔 게시글 조회 가능"""
    try:
        # 기본 쿼리 - 모든 교회의 나눔 게시글
        query = db.query(CommunitySharing)
        
        # 선택적 교회 필터링
        if church_filter:
            query = query.filter(CommunitySharing.church_id == church_filter)
        
        # 상태 필터
        if status:
            query = query.filter(CommunitySharing.status == status)
        
        # 카테고리 필터
        if category:
            query = query.filter(CommunitySharing.category == category)
        
        # 지역 필터
        if location:
            query = query.filter(CommunitySharing.location.contains(location))
        
        # 검색
        if search:
            search_filter = or_(
                CommunitySharing.title.contains(search),
                CommunitySharing.description.contains(search)
            )
            query = query.filter(search_filter)
        
        # 정렬 및 페이징
        total_count = query.count()
        skip = (page - 1) * limit
        sharing_posts = query.order_by(desc(CommunitySharing.created_at)).offset(skip).limit(limit).all()
        
        # 페이지네이션 정보
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "data": [SharingSchemas.Response.from_orm(post) for post in sharing_posts],
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
            detail=f"나눔 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/sharing", response_model=dict)
async def create_sharing(
    title: str = Form(..., description="제목"),
    description: str = Form(..., description="상세 설명"),
    category: str = Form(..., description="카테고리"),
    condition: Optional[str] = Form(None, description="상태"),
    location: str = Form(..., description="지역"),
    contact_method: str = Form(..., description="연락 방법"),
    contact_info: str = Form(..., description="연락처"),
    pickup_location: Optional[str] = Form(None, description="픽업 장소"),
    available_times: Optional[str] = Form(None, description="가능한 시간"),
    expires_at: Optional[str] = Form(None, description="만료일시 (ISO format)"),
    images: List[UploadFile] = File(None, description="이미지 파일들"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 등록"""
    try:
        # 이미지 파일 검증 및 업로드
        image_urls = []
        if images and len(images) > 0 and images[0].filename:
            if len(images) > COMMUNITY_MAX_FILES:
                raise HTTPException(
                    status_code=400,
                    detail=f"최대 {COMMUNITY_MAX_FILES}개의 파일만 업로드 가능합니다."
                )
            
            for image in images:
                if image.size > COMMUNITY_MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"파일 크기는 최대 {COMMUNITY_MAX_FILE_SIZE // (1024*1024)}MB입니다."
                    )
                
                # 파일 확장자 검증
                file_ext = image.filename.split('.')[-1].lower()
                if file_ext not in [ext for ext in COMMUNITY_ALLOWED_EXTENSIONS.keys() if ext in ['jpg', 'jpeg', 'png']]:
                    raise HTTPException(
                        status_code=400,
                        detail="jpg, jpeg, png 파일만 업로드 가능합니다."
                    )
        
        # 커뮤니티 사용자는 church_id 9998
        church_id = 9998 if current_user.church_id == 9998 else current_user.church_id
        
        # 나눔 게시글 생성
        sharing_data = {
            "title": title,
            "description": description,
            "category": category,
            "condition": condition,
            "location": location,
            "contact_method": contact_method,
            "contact_info": contact_info,
            "pickup_location": pickup_location,
            "available_times": available_times,
            "images": image_urls,
            "author_id": current_user.id,
            "church_id": church_id,
            "status": "available"
        }
        
        # expires_at 처리
        if expires_at:
            from datetime import datetime
            try:
                sharing_data["expires_at"] = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except:
                pass  # 날짜 파싱 실패시 무시
        
        db_sharing = CommunitySharing(**sharing_data)
        db.add(db_sharing)
        db.commit()
        db.refresh(db_sharing)
        
        return {
            "success": True,
            "message": "나눔 게시글이 등록되었습니다.",
            "data": SharingSchemas.Response.from_orm(db_sharing)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"나눔 등록 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/sharing/{sharing_id}", response_model=dict)
def get_sharing_detail(
    sharing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 상세 조회"""
    try:
        sharing = db.query(CommunitySharing).filter(CommunitySharing.id == sharing_id).first()
        
        if not sharing:
            raise HTTPException(status_code=404, detail="해당 나눔 게시글을 찾을 수 없습니다.")
        
        # 조회수 증가
        sharing.views += 1
        db.commit()
        
        return {
            "success": True,
            "data": SharingSchemas.Response.from_orm(sharing)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"나눔 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/sharing/{sharing_id}", response_model=dict)
def update_sharing(
    sharing_id: int,
    updates: SharingSchemas.Update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 수정"""
    try:
        sharing = db.query(CommunitySharing).filter(CommunitySharing.id == sharing_id).first()
        
        if not sharing:
            raise HTTPException(status_code=404, detail="해당 나눔 게시글을 찾을 수 없습니다.")
        
        # 작성자만 수정 가능
        if sharing.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 수정할 수 있습니다.")
        
        # 업데이트
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sharing, field, value)
        
        db.commit()
        db.refresh(sharing)
        
        return {
            "success": True,
            "message": "나눔 게시글이 수정되었습니다.",
            "data": SharingSchemas.Response.from_orm(sharing)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"나눔 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/sharing/{sharing_id}/status", response_model=dict)
def update_sharing_status(
    sharing_id: int,
    status_update: SharingSchemas.StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 상태 변경"""
    try:
        sharing = db.query(CommunitySharing).filter(CommunitySharing.id == sharing_id).first()
        
        if not sharing:
            raise HTTPException(status_code=404, detail="해당 나눔 게시글을 찾을 수 없습니다.")
        
        # 작성자만 상태 변경 가능
        if sharing.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 상태 변경할 수 있습니다.")
        
        # 상태 업데이트
        sharing.status = status_update.status
        if status_update.recipient_info:
            sharing.recipient_info = status_update.recipient_info
        
        db.commit()
        db.refresh(sharing)
        
        return {
            "success": True,
            "message": "나눔 상태가 변경되었습니다.",
            "data": SharingSchemas.Response.from_orm(sharing)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"나눔 상태 변경 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/sharing/{sharing_id}", response_model=dict)
def delete_sharing(
    sharing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 삭제"""
    try:
        sharing = db.query(CommunitySharing).filter(CommunitySharing.id == sharing_id).first()
        
        if not sharing:
            raise HTTPException(status_code=404, detail="해당 나눔 게시글을 찾을 수 없습니다.")
        
        # 작성자만 삭제 가능 (또는 슈퍼어드민)
        if sharing.author_id != current_user.id and current_user.church_id != 0:
            raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 삭제할 수 있습니다.")
        
        db.delete(sharing)
        db.commit()
        
        return {
            "success": True,
            "message": "나눔 게시글이 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"나눔 삭제 중 오류가 발생했습니다: {str(e)}"
        )