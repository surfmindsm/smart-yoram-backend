from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
import json
import os
from datetime import datetime
import secrets
import string
import logging

from app.api.deps import get_db, get_current_active_superuser
from app.models.community_application import CommunityApplication
from app.schemas.community_application import (
    CommunityApplicationCreate,
    CommunityApplicationResponse,
    CommunityApplicationList,
    CommunityApplicationsListResponse,
    ApplicationApproval,
    ApplicationRejection,
    StandardResponse,
    AttachmentInfo
)
from app.models.user import User

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# 파일 업로드 설정
UPLOAD_DIR = "uploads/community_applications"
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 5

# 유효한 신청자 유형
VALID_APPLICANT_TYPES = {"company", "individual", "musician", "minister", "organization", "other"}
VALID_STATUS_TYPES = {"pending", "approved", "rejected"}


def safe_file_save(files: List[UploadFile], application_id: int) -> List[AttachmentInfo]:
    """파일을 안전하게 저장하고 정보를 반환합니다."""
    if not files or not any(f.filename for f in files if f):
        return []
    
    # 업로드 디렉토리 생성
    app_upload_dir = os.path.join(UPLOAD_DIR, str(application_id))
    os.makedirs(app_upload_dir, exist_ok=True)
    
    saved_files = []
    
    for file in files:
        if not file or not file.filename:
            continue
            
        try:
            # 파일 확장자 검증
            file_ext = os.path.splitext(file.filename.lower())[1]
            if file_ext not in ALLOWED_EXTENSIONS:
                logger.warning(f"Invalid file extension: {file_ext}")
                continue
            
            # 파일 내용 읽기
            file_content = file.file.read()
            if len(file_content) > MAX_FILE_SIZE:
                logger.warning(f"File too large: {len(file_content)} bytes")
                continue
            
            # 안전한 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{timestamp}_{secrets.token_hex(4)}_{file.filename}"
            file_path = os.path.join(app_upload_dir, safe_filename)
            
            # 파일 저장
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            saved_files.append(AttachmentInfo(
                filename=file.filename,
                path=file_path,
                size=len(file_content)
            ))
            
        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            continue
    
    return saved_files


@router.post("/applications", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def submit_community_application(
    applicant_type: str = Form(...),
    organization_name: str = Form(...),
    contact_person: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    description: str = Form(...),
    business_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    service_area: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    attachments: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):
    """커뮤니티 회원 신청서를 제출합니다."""
    
    try:
        # 입력 데이터 검증
        if applicant_type not in VALID_APPLICANT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid applicant_type. Must be one of: {', '.join(VALID_APPLICANT_TYPES)}"
            )
        
        # 이메일 중복 체크
        existing_app = db.query(CommunityApplication).filter(
            CommunityApplication.email == email
        ).first()
        
        if existing_app:
            return StandardResponse(
                success=False,
                message="이미 등록된 이메일입니다.",
                data={"error_code": "EMAIL_ALREADY_EXISTS"}
            )
        
        # 신청서 생성
        application = CommunityApplication(
            applicant_type=applicant_type,
            organization_name=organization_name[:200],  # 길이 제한
            contact_person=contact_person[:100],
            email=email[:255],
            phone=phone[:20],
            business_number=business_number[:50] if business_number else None,
            address=address,
            description=description,
            service_area=service_area[:200] if service_area else None,
            website=website[:500] if website else None,
            status="pending"
        )
        
        db.add(application)
        db.flush()  # ID 얻기 위해 flush
        
        # 파일 업로드 처리 (안전하게)
        if attachments and len([f for f in attachments if f and f.filename]) > MAX_FILES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"최대 {MAX_FILES}개 파일만 업로드 가능합니다."
            )
        
        saved_files = []
        if attachments:
            saved_files = safe_file_save(attachments, application.id)
            if saved_files:
                application.attachments = json.dumps([file.dict() for file in saved_files])
        
        db.commit()
        
        logger.info(f"New community application submitted: {application.id}")
        
        return StandardResponse(
            success=True,
            message="신청서가 성공적으로 제출되었습니다.",
            data={
                "application_id": application.id,
                "status": application.status,
                "submitted_at": application.submitted_at.isoformat()
            }
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Application submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="신청서 제출 중 오류가 발생했습니다."
        )


@router.get("/admin/applications/debug", response_model=dict)
def debug_community_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """디버깅용 Mock 데이터 엔드포인트"""
    try:
        # 테이블 존재 확인
        table_count = db.execute(text("SELECT COUNT(*) FROM community_applications")).scalar()
        
        return {
            "status": "success",
            "table_exists": True,
            "record_count": table_count,
            "mock_data": {
                "applications": [
                    {
                        "id": 1,
                        "applicant_type": "company",
                        "organization_name": "(주)교회음향시스템",
                        "contact_person": "김테스트",
                        "email": "test@company.com",
                        "phone": "010-1234-5678",
                        "status": "pending",
                        "submitted_at": "2024-09-08T10:00:00Z",
                        "reviewed_at": None
                    }
                ],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "total_count": 1,
                    "per_page": 20
                },
                "statistics": {
                    "pending": 1,
                    "approved": 0,
                    "rejected": 0,
                    "total": 1
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "table_exists": False
        }


@router.get("/admin/applications", response_model=CommunityApplicationsListResponse)
def get_community_applications(
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[str] = None,
    applicant_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "submitted_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """신청서 목록을 조회합니다 (슈퍼어드민 전용)."""
    
    try:
        # 기본 쿼리
        query = db.query(CommunityApplication)
        
        # 필터링
        if status_filter and status_filter != "all" and status_filter in VALID_STATUS_TYPES:
            query = query.filter(CommunityApplication.status == status_filter)
        
        if applicant_type and applicant_type != "all" and applicant_type in VALID_APPLICANT_TYPES:
            query = query.filter(CommunityApplication.applicant_type == applicant_type)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (CommunityApplication.organization_name.ilike(search_term)) |
                (CommunityApplication.contact_person.ilike(search_term)) |
                (CommunityApplication.email.ilike(search_term))
            )
        
        # 정렬
        if sort_by == "submitted_at":
            if sort_order == "desc":
                query = query.order_by(CommunityApplication.submitted_at.desc())
            else:
                query = query.order_by(CommunityApplication.submitted_at.asc())
        elif sort_by == "organization_name":
            if sort_order == "desc":
                query = query.order_by(CommunityApplication.organization_name.desc())
            else:
                query = query.order_by(CommunityApplication.organization_name.asc())
        else:
            query = query.order_by(CommunityApplication.submitted_at.desc())
        
        # 총 개수
        total_count = query.count()
        
        # 페이지네이션
        if limit > 100:  # 최대 제한
            limit = 100
        offset = (page - 1) * limit
        applications = query.offset(offset).limit(limit).all()
        
        # attachments JSON 파싱 처리
        for app in applications:
            if app.attachments:
                try:
                    app.attachments = json.loads(app.attachments)
                except:
                    app.attachments = None
            else:
                app.attachments = None
        
        # 통계 계산
        stats_query = db.query(CommunityApplication)
        statistics = {
            "pending": stats_query.filter(CommunityApplication.status == "pending").count(),
            "approved": stats_query.filter(CommunityApplication.status == "approved").count(),
            "rejected": stats_query.filter(CommunityApplication.status == "rejected").count(),
            "total": stats_query.count()
        }
        
        return CommunityApplicationsListResponse(
            applications=applications,
            pagination={
                "current_page": page,
                "total_pages": (total_count + limit - 1) // limit,
                "total_count": total_count,
                "per_page": limit
            },
            statistics=statistics
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Application list error: {str(e)}")
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"신청서 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/admin/applications/{application_id}", response_model=CommunityApplicationResponse)
def get_community_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """신청서 상세 정보를 조회합니다 (슈퍼어드민 전용)."""
    
    application = db.query(CommunityApplication).filter(
        CommunityApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="신청서를 찾을 수 없습니다."
        )
    
    # 첨부파일 정보 파싱
    if application.attachments:
        try:
            attachments_data = json.loads(application.attachments)
            application.attachments = attachments_data
        except:
            application.attachments = None
    
    return application


@router.put("/admin/applications/{application_id}/approve", response_model=StandardResponse)
def approve_community_application(
    application_id: int,
    request: ApplicationApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """신청서를 승인합니다 (슈퍼어드민 전용)."""
    
    try:
        application = db.query(CommunityApplication).filter(
            CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="신청서를 찾을 수 없습니다."
            )
        
        if application.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 처리된 신청서입니다."
            )
        
        # 승인 처리
        application.status = "approved"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        application.notes = request.notes
        
        db.commit()
        
        logger.info(f"Application approved: {application_id} by user {current_user.id}")
        
        # TODO: 사용자 계정 생성 및 이메일 발송
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        username = f"{application.organization_name.lower().replace(' ', '_')}_community"
        
        return StandardResponse(
            success=True,
            message="신청서가 승인되었습니다.",
            data={
                "application_id": application.id,
                "status": application.status,
                "reviewed_at": application.reviewed_at.isoformat(),
                "user_account": {
                    "username": username,
                    "temporary_password": temp_password,
                    "login_url": "https://admin.smartyoram.com/login"
                }
            }
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Application approval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="승인 처리 중 오류가 발생했습니다."
        )


@router.put("/admin/applications/{application_id}/reject", response_model=StandardResponse)
def reject_community_application(
    application_id: int,
    request: ApplicationRejection,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """신청서를 반려합니다 (슈퍼어드민 전용)."""
    
    try:
        application = db.query(CommunityApplication).filter(
            CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="신청서를 찾을 수 없습니다."
            )
        
        if application.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 처리된 신청서입니다."
            )
        
        # 반려 처리
        application.status = "rejected"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        application.rejection_reason = request.rejection_reason
        application.notes = request.notes
        
        db.commit()
        
        logger.info(f"Application rejected: {application_id} by user {current_user.id}")
        
        # TODO: 반려 이메일 발송
        
        return StandardResponse(
            success=True,
            message="신청서가 반려되었습니다.",
            data={
                "application_id": application.id,
                "status": application.status,
                "reviewed_at": application.reviewed_at.isoformat()
            }
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Application rejection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="반려 처리 중 오류가 발생했습니다."
        )