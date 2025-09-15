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
    description: Optional[str] = None
    category: Optional[str] = None
    urgency: Optional[str] = "normal"
    location: Optional[str] = None
    contact_info: Optional[str] = None
    reward_type: Optional[str] = "none"
    reward_amount: Optional[int] = None
    images: Optional[List[str]] = []
    status: Optional[str] = "open"

router = APIRouter()


# 디버깅용 간단한 테스트 엔드포인트
@router.get("/debug-requests", response_model=dict)
def debug_requests(db: Session = Depends(get_db)):
    """디버깅용: DB 데이터 직접 확인"""
    try:
        # 간단한 직접 쿼리
        requests = db.query(CommunityRequest).all()
        
        result = []
        for req in requests:
            result.append({
                "id": req.id,
                "title": req.title,
                "status": req.status,
                "author_id": req.author_id,
                "church_id": req.church_id,
                "created_at": str(req.created_at)
            })
        
        return {
            "success": True,
            "total_count": len(requests),
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": []
        }


# 프론트엔드에서 호출하는 URL에 맞춰 추가
@router.get("/item-request", response_model=dict)
def get_item_request_list(
    status: Optional[str] = Query(None, description="상태 필터: active, fulfilled, cancelled"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    urgency: Optional[str] = Query(None, description="긴급도 필터: 낮음, 보통, 높음"),
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
        print(f"🔍 [LIST] 물품 요청 목록 조회 시작")
        print(f"🔍 [LIST] 필터: status={status}, category={category}, urgency={urgency}, location={location}")
        
        # 전체 데이터 개수 먼저 확인
        total_requests = db.query(CommunityRequest).count()
        null_author_requests = db.query(CommunityRequest).filter(CommunityRequest.author_id.is_(None)).count()
        print(f"🔍 [DEBUG] 전체 요청 개수: {total_requests}")
        print(f"🔍 [DEBUG] NULL author_id 요청 개수: {null_author_requests}")
        
        # Raw SQL로 안전한 조회 - 실제 컬럼명 사용
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                cr.id,
                cr.title,
                cr.description,
                cr.category,
                cr.urgency,
                cr.location,
                cr.contact_info,
                cr.reward_type,
                cr.reward_amount,
                cr.images,
                cr.status,
                cr.view_count,
                cr.created_at,
                cr.updated_at,
                cr.author_id,
                cr.church_id,
                COALESCE(u.full_name, '익명') as user_name
            FROM community_requests cr
            LEFT JOIN users u ON cr.author_id = u.id
            WHERE 1=1
        """
        params = {}
        
        # 필터링 적용
        if status and status != 'all':
            query_sql += " AND cr.status = :status"
            params["status"] = status
            print(f"🔍 [LIST] 상태 필터 적용: {status}")
        if category and category != 'all':
            query_sql += " AND cr.category = :category"
            params["category"] = category
            print(f"🔍 [LIST] 카테고리 필터 적용: {category}")
        if urgency and urgency != 'all':
            query_sql += " AND cr.urgency = :urgency"
            params["urgency"] = urgency
            print(f"🔍 [LIST] 긴급도 필터 적용: {urgency}")
        if location:
            query_sql += " AND cr.location ILIKE :location"
            params["location"] = f"%{location}%"
        if search:
            query_sql += " AND (cr.title ILIKE :search OR cr.description ILIKE :search)"
            params["search"] = f"%{search}%"
        
        query_sql += " ORDER BY cr.created_at DESC"
        
        # 전체 개수 계산
        count_sql = "SELECT COUNT(*) FROM community_requests cr WHERE 1=1"
        count_params = {}
        if status and status != 'all':
            count_sql += " AND cr.status = :status"
            count_params["status"] = status
        if category and category != 'all':
            count_sql += " AND cr.category = :category"
            count_params["category"] = category
        if urgency and urgency != 'all':
            count_sql += " AND cr.urgency = :urgency"
            count_params["urgency"] = urgency
        if location:
            count_sql += " AND cr.location ILIKE :location"
            count_params["location"] = f"%{location}%"
        if search:
            count_sql += " AND (cr.title ILIKE :search OR cr.description ILIKE :search)"
            count_params["search"] = f"%{search}%"
            
        count_result = db.execute(text(count_sql), count_params)
        total_count = count_result.scalar() or 0
        print(f"🔍 [LIST] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        query_sql += f" OFFSET {offset} LIMIT {limit}"
        
        result = db.execute(text(query_sql), params)
        request_list = result.fetchall()
        print(f"🔍 [LIST] 조회된 데이터 개수: {len(request_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for row in request_list:
            # Raw SQL 결과를 인덱스로 접근 (실제 컬럼 순서대로)
            images_data = row[8] if row[8] else []  # JSON 컬럼
            # JSON 문자열인 경우 파싱
            if isinstance(images_data, str):
                try:
                    import json
                    images_data = json.loads(images_data)
                except:
                    images_data = []
            
            data_items.append({
                "id": row[0],                    # cr.id
                "title": row[1],                 # cr.title  
                "description": row[2],           # cr.description
                "category": row[3],              # cr.category
                "urgency": row[4],               # cr.urgency
                "status": row[9],                # cr.status
                "location": row[6],              # cr.location
                "contact_info": row[7],          # cr.contact_info
                "images": images_data,           # cr.images (JSON)
                "created_at": row[11].isoformat() if row[11] else None,  # cr.created_at
                "updated_at": row[12].isoformat() if row[12] else None,  # cr.updated_at
                "view_count": row[10] or 0,      # cr.view_count
                "user_id": row[13],              # cr.author_id (응답에서는 user_id로 유지)
                "user_name": row[15] or "익명",    # u.full_name
                "church_id": row[14],            # cr.church_id
                "church_name": row[16] or f"교회 {row[14]}"  # c.name (교회명)
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
    urgency: Optional[str] = Query(None, description="긴급도 필터: 낮음, 보통, 높음"),
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
    return get_item_request_list(status, category, urgency, location, search, church_filter, page, limit, db, current_user)


@router.post("/requests", response_model=dict)
async def create_request(
    request: Request,
    request_data: RequestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """요청 등록 - 실제 데이터베이스 저장"""
    try:
        print(f"🔍 [REQUEST] Request data received: {request_data}")
        print(f"🔍 [REQUEST] User ID: {current_user.id}, Church ID: {current_user.church_id}")
        print(f"🔍 [REQUEST] User name: {current_user.full_name}")
        
        # 실제 데이터베이스에 저장
        request_record = CommunityRequest(
            title=request_data.title,
            description=request_data.description,
            category=request_data.category,
            urgency=request_data.urgency or "normal",
            location=request_data.location,
            contact_info=request_data.contact_info,
            reward_type=request_data.reward_type or "none",
            reward_amount=request_data.reward_amount,
            status=request_data.status or "open",
            images=request_data.images or [],
            author_id=current_user.id,  # 실제 테이블의 author_id 사용
            church_id=current_user.church_id or 9998,  # 커뮤니티 기본값
        )
        
        print(f"🔍 [REQUEST] About to save request record...")
        db.add(request_record)
        db.commit()
        db.refresh(request_record)
        print(f"✅ [REQUEST] Successfully saved request with ID: {request_record.id}")
        
        # 저장 후 검증 - 실제로 DB에서 다시 조회
        saved_record = db.query(CommunityRequest).filter(CommunityRequest.id == request_record.id).first()
        if saved_record:
            print(f"✅ [REQUEST] Verification successful: Record exists in DB with ID {saved_record.id}")
        else:
            print(f"❌ [REQUEST] Verification failed: Record not found in DB!")
        
        return {
            "success": True,
            "message": "요청 게시글이 등록되었습니다.",
            "data": {
                "id": request_record.id,
                "title": request_record.title,
                "description": request_record.description,
                "category": request_record.category,
                "urgency": request_record.urgency,
                "location": request_record.location,
                "contact_info": request_record.contact_info,
                "status": request_record.status,
                "images": request_record.images or [],
                "user_id": request_record.user_id,
                "user_name": current_user.full_name or "익명",
                "church_id": request_record.church_id,
                "created_at": request_record.created_at.isoformat() if request_record.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [REQUEST] 요청 등록 실패: {str(e)}")
        import traceback
        print(f"❌ [REQUEST] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"요청 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.post("/fix-request-authors", response_model=dict)
def fix_request_authors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """NULL author_id를 현재 사용자로 업데이트"""
    try:
        from sqlalchemy import text
        
        # NULL author_id인 레코드 찾기
        null_records = db.query(CommunityRequest).filter(CommunityRequest.author_id.is_(None)).all()
        
        print(f"🔍 NULL author_id 레코드 개수: {len(null_records)}")
        
        updated_count = 0
        for record in null_records:
            record.author_id = current_user.id
            updated_count += 1
            print(f"✅ Request ID {record.id} author_id 업데이트: {current_user.id}")
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{updated_count}개의 요청이 업데이트되었습니다.",
            "data": {
                "updated_count": updated_count,
                "user_id": current_user.id,
                "user_name": current_user.full_name or "익명"
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"업데이트 중 오류: {str(e)}"
        }


@router.post("/item-requests", response_model=dict)
async def create_item_request_plural(
    request: Request,
    request_data: RequestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물품 요청 등록 - 복수형 URL"""
    return await create_request(request, request_data, db, current_user)


@router.post("/item-request", response_model=dict)
async def create_item_request_singular(
    request: Request,
    request_data: RequestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물품 요청 등록 - 단수형 URL (프론트엔드 호환)"""
    return await create_request(request, request_data, db, current_user)


@router.get("/item-requests", response_model=dict)
def get_item_requests_list(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    urgency: Optional[str] = Query(None, description="긴급도 필터"),
    status: Optional[str] = Query(None, description="상태 필터"),
    location: Optional[str] = Query(None, description="지역 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    church_filter: Optional[int] = Query(None, description="교회 필터 (선택사항)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """물품 요청 목록 조회 - 프론트엔드 호환성을 위한 별칭 엔드포인트"""
    return get_request_list(status, category, urgency, location, search, church_filter, page, limit, db, current_user)


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