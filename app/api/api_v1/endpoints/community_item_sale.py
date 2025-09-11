"""
커뮤니티 물건 판매 관련 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.community_sharing import CommunitySharing

class ItemSaleCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    condition: Optional[str] = "good"
    price: int  # 필수 - 유료 판매
    location: str
    contact_info: str
    images: Optional[List[str]] = []
    status: Optional[str] = "available"

router = APIRouter()


@router.get("/item-sale", response_model=dict)
def get_item_sale_list(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    min_price: Optional[int] = Query(None, description="최소 가격"),
    max_price: Optional[int] = Query(None, description="최대 가격"),
    location: Optional[str] = Query(None, description="지역 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물건 판매 목록 조회"""
    try:
        print(f"🚀 [DEBUG] 커뮤니티 물건 판매 API 호출됨")
        print(f"🚀 [DEBUG] 현재 사용자: church_id={current_user.church_id}, user_id={current_user.id}")
        
        # 기본 쿼리 - 유료 판매만 (is_free=False)
        from app.models.user import User
        query = db.query(CommunitySharing, User.full_name).outerjoin(
            User, CommunitySharing.user_id == User.id
        ).filter(CommunitySharing.is_free == False)  # 유료 판매만
        
        # 필터링 적용
        if category:
            query = query.filter(CommunitySharing.category == category)
        if min_price:
            query = query.filter(CommunitySharing.price >= min_price)
        if max_price:
            query = query.filter(CommunitySharing.price <= max_price)
        if location:
            query = query.filter(CommunitySharing.location.ilike(f"%{location}%"))
        if search:
            query = query.filter(
                (CommunitySharing.title.ilike(f"%{search}%")) |
                (CommunitySharing.description.ilike(f"%{search}%"))
            )
        
        # 전체 개수 계산
        total_count = query.count()
        print(f"🚀 [DEBUG] 총 판매 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        sale_list = query.order_by(CommunitySharing.created_at.desc()).offset(offset).limit(limit).all()
        print(f"🚀 [DEBUG] 조회된 판매 데이터 개수: {len(sale_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for sale_item, user_full_name in sale_list:
            data_items.append({
                "id": sale_item.id,
                "title": sale_item.title,
                "description": sale_item.description,
                "category": sale_item.category,
                "condition": sale_item.condition,
                "price": sale_item.price,
                "is_free": sale_item.is_free,
                "status": sale_item.status,
                "location": sale_item.location,
                "contact_info": sale_item.contact_info,
                "images": sale_item.images or [],
                "created_at": sale_item.created_at.isoformat() if sale_item.created_at else None,
                "updated_at": sale_item.updated_at.isoformat() if sale_item.updated_at else None,
                "view_count": sale_item.view_count or 0,
                "user_id": sale_item.user_id,
                "user_name": user_full_name or "익명",
                "church_id": sale_item.church_id
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 물건 판매 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
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
        print(f"❌ 물건 판매 목록 조회 실패: {str(e)}")
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


@router.post("/item-sale", response_model=dict)
async def create_item_sale(
    request: Request,
    sale_data: ItemSaleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물건 판매 등록"""
    try:
        print(f"🔍 Item sale data: {sale_data}")
        print(f"🔍 User ID: {current_user.id}, Church ID: {current_user.church_id}")
        
        # 가격이 0보다 큰지 확인
        if sale_data.price <= 0:
            return {
                "success": False,
                "message": "판매 가격은 0원보다 커야 합니다."
            }
        
        # 실제 데이터베이스에 저장 (유료 판매)
        sale_record = CommunitySharing(
            church_id=current_user.church_id,
            user_id=current_user.id,
            title=sale_data.title,
            description=sale_data.description,
            category=sale_data.category,
            condition=sale_data.condition,
            price=sale_data.price,  # 유료 가격
            is_free=False,  # 유료 판매
            location=sale_data.location,
            contact_info=sale_data.contact_info,
            images=sale_data.images or [],
            status=sale_data.status or "available",
        )
        
        db.add(sale_record)
        db.commit()
        db.refresh(sale_record)
        
        print(f"✅ 새로운 물건 판매 게시글 저장됨: ID={sale_record.id}")
        
        return {
            "success": True,
            "message": "물건 판매 게시글이 등록되었습니다.",
            "data": {
                "id": sale_record.id,
                "title": sale_record.title,
                "description": sale_record.description,
                "category": sale_record.category,
                "condition": sale_record.condition,
                "price": sale_record.price,
                "is_free": sale_record.is_free,
                "location": sale_record.location,
                "contact_info": sale_record.contact_info,
                "status": sale_record.status,
                "images": sale_record.images or [],
                "user_id": sale_record.user_id,
                "user_name": current_user.full_name or "익명",
                "church_id": sale_record.church_id,
                "created_at": sale_record.created_at.isoformat() if sale_record.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ 물건 판매 등록 실패: {str(e)}")
        return {
            "success": False,
            "message": f"물건 판매 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/item-sale/{sale_id}", response_model=dict)
def get_item_sale_detail(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물건 판매 상세 조회"""
    try:
        # 실제 데이터 조회
        sale_item = db.query(CommunitySharing).filter(
            CommunitySharing.id == sale_id,
            CommunitySharing.is_free == False
        ).first()
        
        if not sale_item:
            return {
                "success": False,
                "message": "판매 게시글을 찾을 수 없습니다."
            }
        
        # 조회수 증가
        sale_item.view_count = (sale_item.view_count or 0) + 1
        db.commit()
        
        # 작성자 정보 조회
        from app.models.user import User
        author = db.query(User).filter(User.id == sale_item.user_id).first()
        
        return {
            "success": True,
            "data": {
                "id": sale_item.id,
                "title": sale_item.title,
                "description": sale_item.description,
                "category": sale_item.category,
                "condition": sale_item.condition,
                "price": sale_item.price,
                "is_free": sale_item.is_free,
                "location": sale_item.location,
                "contact_info": sale_item.contact_info,
                "images": sale_item.images or [],
                "status": sale_item.status,
                "view_count": sale_item.view_count,
                "user_id": sale_item.user_id,
                "user_name": author.full_name if author else "익명",
                "church_id": sale_item.church_id,
                "created_at": sale_item.created_at.isoformat() if sale_item.created_at else None,
                "updated_at": sale_item.updated_at.isoformat() if sale_item.updated_at else None
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"물건 판매 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/item-sale/{sale_id}", response_model=dict)
def update_item_sale(
    sale_id: int,
    sale_data: ItemSaleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물건 판매 수정"""
    try:
        sale_item = db.query(CommunitySharing).filter(
            CommunitySharing.id == sale_id,
            CommunitySharing.user_id == current_user.id,
            CommunitySharing.is_free == False
        ).first()
        
        if not sale_item:
            return {
                "success": False,
                "message": "수정할 판매 게시글을 찾을 수 없거나 권한이 없습니다."
            }
        
        # 데이터 업데이트
        sale_item.title = sale_data.title
        sale_item.description = sale_data.description
        sale_item.category = sale_data.category
        sale_item.condition = sale_data.condition
        sale_item.price = sale_data.price
        sale_item.location = sale_data.location
        sale_item.contact_info = sale_data.contact_info
        sale_item.images = sale_data.images or []
        sale_item.status = sale_data.status
        
        db.commit()
        
        return {
            "success": True,
            "message": "물건 판매 게시글이 수정되었습니다.",
            "data": {
                "id": sale_item.id,
                "title": sale_item.title,
                "price": sale_item.price,
                "status": sale_item.status
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"물건 판매 수정 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/item-sale/{sale_id}", response_model=dict)
def delete_item_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물건 판매 삭제"""
    try:
        sale_item = db.query(CommunitySharing).filter(
            CommunitySharing.id == sale_id,
            CommunitySharing.user_id == current_user.id,
            CommunitySharing.is_free == False
        ).first()
        
        if not sale_item:
            return {
                "success": False,
                "message": "삭제할 판매 게시글을 찾을 수 없거나 권한이 없습니다."
            }
        
        db.delete(sale_item)
        db.commit()
        
        return {
            "success": True,
            "message": "물건 판매 게시글이 삭제되었습니다."
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"물건 판매 삭제 중 오류가 발생했습니다: {str(e)}"
        }


@router.patch("/item-sale/{sale_id}/status", response_model=dict)
def update_item_sale_status(
    sale_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물건 판매 상태 변경"""
    try:
        sale_item = db.query(CommunitySharing).filter(
            CommunitySharing.id == sale_id,
            CommunitySharing.user_id == current_user.id,
            CommunitySharing.is_free == False
        ).first()
        
        if not sale_item:
            return {
                "success": False,
                "message": "상태를 변경할 판매 게시글을 찾을 수 없거나 권한이 없습니다."
            }
        
        sale_item.status = status
        db.commit()
        
        return {
            "success": True,
            "message": "물건 판매 상태가 변경되었습니다.",
            "data": {
                "id": sale_item.id,
                "status": sale_item.status
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"물건 판매 상태 변경 중 오류가 발생했습니다: {str(e)}"
        }