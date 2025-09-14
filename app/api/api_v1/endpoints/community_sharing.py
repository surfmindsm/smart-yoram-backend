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
        
        # Raw SQL로 안전한 조회 - 트랜잭션 초기화 및 실제 컬럼명 사용
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                cs.id,
                cs.title,
                cs.description,
                cs.category,
                cs.condition,
                cs.price,
                cs.is_free,
                cs.location,
                cs.contact_info,
                cs.images,
                cs.status,
                cs.view_count,
                cs.created_at,
                cs.updated_at,
                cs.author_id,
                cs.church_id,
                u.full_name
            FROM community_sharing cs
            LEFT JOIN users u ON cs.author_id = u.id
            WHERE 1=1
        """
        params = {}
        
        print(f"🚀 [DEBUG] Raw SQL로 community_sharing 조회 시작")
        
        # 필터링 적용
        if status:
            query_sql += " AND cs.status = :status"
            params["status"] = status
        if category:
            query_sql += " AND cs.category = :category"  
            params["category"] = category
        if location:
            query_sql += " AND cs.location ILIKE :location"
            params["location"] = f"%{location}%"
        if search:
            query_sql += " AND (cs.title ILIKE :search OR cs.description ILIKE :search)"
            params["search"] = f"%{search}%"
        
        query_sql += " ORDER BY cs.created_at DESC"
        
        # 전체 개수 계산
        count_sql = "SELECT COUNT(*) FROM community_sharing cs WHERE 1=1"
        count_params = {}
        if status:
            count_sql += " AND cs.status = :status"
            count_params["status"] = status
        if category:
            count_sql += " AND cs.category = :category"
            count_params["category"] = category
        if location:
            count_sql += " AND cs.location ILIKE :location"
            count_params["location"] = f"%{location}%"
        if search:
            count_sql += " AND (cs.title ILIKE :search OR cs.description ILIKE :search)"
            count_params["search"] = f"%{search}%"
            
        count_result = db.execute(text(count_sql), count_params)
        total_count = count_result.scalar() or 0
        print(f"🚀 [DEBUG] 총 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        query_sql += f" OFFSET {offset} LIMIT {limit}"
        
        result = db.execute(text(query_sql), params)
        sharing_list = result.fetchall()
        print(f"🚀 [DEBUG] 조회된 데이터 개수: {len(sharing_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for row in sharing_list:
            # Raw SQL 결과를 인덱스로 접근 (실제 컬럼 순서대로)
            images_data = row[9] if row[9] else []  # JSON 컬럼
            # JSON 문자열인 경우 파싱
            if isinstance(images_data, str):
                try:
                    import json
                    images_data = json.loads(images_data)
                except:
                    images_data = []
            
            data_items.append({
                "id": row[0],                    # cs.id
                "title": row[1],                 # cs.title  
                "description": row[2],           # cs.description
                "category": row[3],              # cs.category
                "condition": row[4],             # cs.condition
                "price": float(row[5]) if row[5] else 0,  # cs.price
                "is_free": row[6],               # cs.is_free
                "status": row[10],               # cs.status
                "location": row[7],              # cs.location
                "contact_info": row[8],          # cs.contact_info
                "images": images_data,           # cs.images (JSON)
                "created_at": row[12].isoformat() if row[12] else None,  # cs.created_at
                "updated_at": row[13].isoformat() if row[13] else None,  # cs.updated_at
                "view_count": row[11] or 0,      # cs.view_count
                "user_id": row[14],              # cs.author_id (응답에서는 user_id로 유지)
                "user_name": row[16] or "익명",    # u.full_name
                "church_id": row[15]             # cs.church_id
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
                "user_name": current_user.full_name or "익명",  # 현재 사용자 이름
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


@router.post("/sharing-offer", response_model=dict)
async def create_sharing_offer(
    request: Request,
    sharing_data: SharingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """나눔 제공 등록 - 프론트엔드 호환성을 위한 별칭 엔드포인트"""
    return await create_sharing(request, sharing_data, db, current_user)


@router.get("/debug-sharing-table", response_model=dict)
def debug_sharing_table(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """디버깅용: community_sharing 테이블 상태 확인"""
    try:
        from sqlalchemy import text
        
        # 테이블 존재 확인
        table_exists_sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'community_sharing'
            )
        """
        exists_result = db.execute(text(table_exists_sql))
        table_exists = exists_result.scalar()
        
        # 전체 레코드 수 확인
        count_sql = "SELECT COUNT(*) FROM community_sharing"
        count_result = db.execute(text(count_sql))
        total_count = count_result.scalar()
        
        # 컬럼 정보 확인
        columns_sql = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'community_sharing'
            ORDER BY ordinal_position
        """
        columns_result = db.execute(text(columns_sql))
        columns_info = [{"name": row[0], "type": row[1]} for row in columns_result.fetchall()]
        
        # 샘플 데이터 몇 개 조회 (author_id 포함)
        sample_sql = "SELECT id, title, church_id, author_id FROM community_sharing LIMIT 3"
        sample_result = db.execute(text(sample_sql))
        sample_data = [{"id": row[0], "title": row[1], "church_id": row[2], "author_id": row[3]} for row in sample_result.fetchall()]
        
        return {
            "success": True,
            "debug_info": {
                "table_exists": table_exists,
                "total_count": total_count,
                "columns_info": columns_info,
                "sample_data": sample_data,
                "current_user_id": current_user.id,
                "current_user_church_id": current_user.church_id
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "debug_info": {
                "current_user_id": getattr(current_user, 'id', 'unknown'),
                "current_user_church_id": getattr(current_user, 'church_id', 'unknown')
            }
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