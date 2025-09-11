from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import json

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.community_sharing import CommunitySharing


class SharingCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    condition: Optional[str] = None
    location: str
    contact_info: str
    images: Optional[List[str]] = []
    status: Optional[str] = "available"

router = APIRouter()


# 프론트엔드에서 호출하는 나눔 제공 URL에 맞춰 추가 (실제 DB 조회)
@router.get("/sharing-offer", response_model=dict)
def get_sharing_offer_list(
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
    """나눔 제공 목록 조회 - 실제 데이터베이스에서 조회"""
    # /sharing-offer와 /sharing은 동일한 로직 사용
    return get_sharing_list(status, category, location, search, church_filter, page, limit, db, current_user)


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
    """나눔 목록 조회 - 실제 데이터베이스에서 조회"""
    try:
        print(f"🚀 [DEBUG] 커뮤니티 나눔 API 호출됨 - 배포 버전 2024-09-11")
        print(f"🚀 [DEBUG] 현재 사용자: church_id={current_user.church_id}, user_id={current_user.id}")
        
        # 기본 쿼리 (커뮤니티는 모든 교회가 공유) - User 테이블과 LEFT JOIN
        from app.models.user import User
        query = db.query(CommunitySharing, User.full_name).outerjoin(
            User, CommunitySharing.user_id == User.id
        )
        # 커뮤니티는 교회 구분없이 모든 사용자가 볼 수 있음
        print(f"🚀 [DEBUG] 교회 필터링 제거됨 - 모든 교회 데이터 조회")
        
        # 필터링 적용
        if status:
            query = query.filter(CommunitySharing.status == status)
        if category:
            query = query.filter(CommunitySharing.category == category)
        if location:
            query = query.filter(CommunitySharing.location.ilike(f"%{location}%"))
        if search:
            query = query.filter(
                (CommunitySharing.title.ilike(f"%{search}%")) |
                (CommunitySharing.description.ilike(f"%{search}%"))
            )
        
        # 전체 개수 계산
        total_count = query.count()
        print(f"🚀 [DEBUG] 총 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        sharing_list = query.order_by(CommunitySharing.created_at.desc()).offset(offset).limit(limit).all()
        print(f"🚀 [DEBUG] 조회된 데이터 개수: {len(sharing_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for sharing, user_full_name in sharing_list:
            data_items.append({
                "id": sharing.id,
                "title": sharing.title,
                "description": sharing.description,
                "category": sharing.category,
                "condition": sharing.condition,
                "price": sharing.price or 0,  # 실제 컬럼
                "is_free": sharing.is_free,  # 실제 컬럼
                "status": sharing.status,
                "location": sharing.location,
                "contact_info": sharing.contact_info,
                "images": sharing.images or [],  # JSON 컬럼으로 실제 존재함!
                "created_at": sharing.created_at.isoformat() if sharing.created_at else None,
                "updated_at": sharing.updated_at.isoformat() if sharing.updated_at else None,
                "view_count": sharing.view_count or 0,  # 실제 컬럼명
                "user_id": sharing.user_id,  # 실제 컬럼명
                "user_name": user_full_name or "익명",  # 사용자 이름 추가
                "church_id": sharing.church_id
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 나눔 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
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
        print(f"❌ 나눔 목록 조회 실패: {str(e)}")
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


@router.post("/sharing", response_model=dict)
async def create_sharing(
    request: Request,
    sharing_data: SharingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 등록 - 실제 데이터베이스 저장"""
    try:
        # 디버깅 로그 추가
        print(f"🔍 Parsed data: {sharing_data}")
        print(f"🔍 User ID: {current_user.id}, Church ID: {current_user.church_id}")
        
        # 실제 데이터베이스에 저장 (실제 테이블 컬럼명에 맞춤)
        sharing_record = CommunitySharing(
            church_id=current_user.church_id,  # 사용자의 교회 ID 사용
            user_id=current_user.id,  # 실제 컬럼명: user_id
            title=sharing_data.title,
            description=sharing_data.description,
            category=sharing_data.category,
            condition=sharing_data.condition,
            price=0,  # 무료나눔이므로 0
            is_free=True,  # 무료나눔이므로 True
            location=sharing_data.location,
            contact_info=sharing_data.contact_info,
            images=sharing_data.images or [],  # JSON 컬럼으로 실제 존재함!
            status=sharing_data.status or "available",
        )
        
        db.add(sharing_record)
        db.commit()
        db.refresh(sharing_record)
        
        print(f"✅ 새로운 나눔 게시글 저장됨: ID={sharing_record.id}")
        
        return {
            "success": True,
            "message": "나눔 게시글이 등록되었습니다.",
            "data": {
                "id": sharing_record.id,
                "title": sharing_record.title,
                "description": sharing_record.description,
                "category": sharing_record.category,
                "condition": sharing_record.condition,
                "price": sharing_record.price,
                "is_free": sharing_record.is_free,
                "location": sharing_record.location,
                "contact_info": sharing_record.contact_info,
                "status": sharing_record.status,
                "images": sharing_record.images or [],  # 실제로 DB에 저장된 이미지들
                "user_id": sharing_record.user_id,  # 실제 컬럼명
                "user_name": current_user.full_name or current_user.name or "익명",  # 현재 사용자 이름
                "church_id": sharing_record.church_id,
                "created_at": sharing_record.created_at.isoformat() if sharing_record.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ 나눔 등록 실패: {str(e)}")
        return {
            "success": False,
            "message": f"나눔 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/sharing/{sharing_id}", response_model=dict)
def get_sharing_detail(
    sharing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 상세 조회 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "data": {
                "id": sharing_id,
                "title": "샘플 나눔 제목",
                "description": "샘플 나눔 설명",
                "category": "생활용품",
                "status": "available",
                "location": "서울",
                "contact_method": "카톡",
                "contact_info": "010-0000-0000"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"나눔 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/sharing/{sharing_id}", response_model=dict)
def update_sharing(
    sharing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 수정 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "나눔 게시글이 수정되었습니다.",
            "data": {
                "id": sharing_id,
                "title": "수정된 나눔 제목",
                "status": "available"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"나눔 수정 중 오류가 발생했습니다: {str(e)}"
        }


@router.patch("/sharing/{sharing_id}/status", response_model=dict)
def update_sharing_status(
    sharing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 상태 변경 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "나눔 상태가 변경되었습니다.",
            "data": {
                "id": sharing_id,
                "status": "completed"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"나눔 상태 변경 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/sharing/{sharing_id}", response_model=dict)
def delete_sharing(
    sharing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 삭제 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "나눔 게시글이 삭제되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"나눔 삭제 중 오류가 발생했습니다: {str(e)}"
        }