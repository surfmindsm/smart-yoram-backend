from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json
import os
from datetime import datetime
import secrets
import string

from app import crud
from app.api import deps
from app.core.config import settings
from app.api.deps import get_db
from app.models.community_application import CommunityApplication
from app.schemas.community_application import (
    CommunityApplicationCreate,
    CommunityApplicationResponse,
    CommunityApplicationList,
    CommunityApplicationsListResponse,
    ApplicationApproval,
    ApplicationRejection,
    ApplicationSubmissionResponse,
    ApplicationApprovalResponse,
    ApplicantType,
    ApplicationStatus,
    AttachmentInfo
)
from app.models.user import User

router = APIRouter()

# 파일 업로드 설정
UPLOAD_DIR = "uploads/community_applications"
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 5


def save_uploaded_files(files: List[UploadFile], application_id: int) -> List[AttachmentInfo]:
    """업로드된 파일들을 저장하고 정보를 반환합니다."""
    if not files:
        return []
    
    app_upload_dir = os.path.join(UPLOAD_DIR, str(application_id))
    os.makedirs(app_upload_dir, exist_ok=True)
    
    saved_files = []
    
    for file in files:
        if not file.filename:
            continue
            
        # 파일 확장자 검증
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"허용되지 않는 파일 형식입니다: {file_ext}")
        
        # 파일 크기 검증 (안전하게 처리)
        try:
            file_content = file.file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"파일 크기가 10MB를 초과합니다: {file.filename}")
        except Exception:
            raise HTTPException(status_code=400, detail="파일 읽기 오류")
        
        # 안전한 파일명 생성
        safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(app_upload_dir, safe_filename)
        
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            saved_files.append(AttachmentInfo(
                filename=file.filename,
                path=file_path,
                size=len(file_content)
            ))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"파일 저장 실패: {str(e)}")
    
    return saved_files


@router.post("/applications", response_model=ApplicationSubmissionResponse)
async def submit_application(
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
    
    # 이메일 중복 체크
    existing_app = db.query(CommunityApplication).filter(
        CommunityApplication.email == email
    ).first()
    
    if existing_app:
        return ApplicationSubmissionResponse(
            success=False,
            message="이미 등록된 이메일입니다.",
            data={"error_code": "EMAIL_ALREADY_EXISTS"}
        )
    
    # 신청자 유형 검증
    try:
        ApplicantType(applicant_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="유효하지 않은 신청자 유형입니다.")
    
    try:
        # 신청서 생성
        application = CommunityApplication(
            applicant_type=applicant_type,
            organization_name=organization_name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            business_number=business_number,
            address=address,
            description=description,
            service_area=service_area,
            website=website,
            status="pending"
        )
        
        db.add(application)
        db.flush()  # ID 얻기 위해 flush
        
        # 파일 업로드 처리
        if attachments and len(attachments) > MAX_FILES:
            raise HTTPException(status_code=400, detail=f"최대 {MAX_FILES}개 파일만 업로드 가능합니다.")
        
        saved_files = []
        if attachments:
            saved_files = save_uploaded_files(attachments, application.id)
            # JSON 문자열로 저장
            application.attachments = json.dumps([file.dict() for file in saved_files])
        
        db.commit()
        
        return ApplicationSubmissionResponse(
            success=True,
            message="신청서가 성공적으로 제출되었습니다.",
            data={
                "application_id": application.id,
                "status": application.status,
                "submitted_at": application.submitted_at.isoformat()
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"신청서 제출 중 오류가 발생했습니다: {str(e)}")


@router.get("/admin/applications", response_model=CommunityApplicationsListResponse)
def get_applications(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    applicant_type: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "submitted_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """신청서 목록을 조회합니다 (슈퍼어드민 전용)."""
    
    query = db.query(CommunityApplication)
    
    # 필터링
    if status and status != "all":
        query = query.filter(CommunityApplication.status == status)
    
    if applicant_type and applicant_type != "all":
        query = query.filter(CommunityApplication.applicant_type == applicant_type)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (CommunityApplication.organization_name.ilike(search_filter)) |
            (CommunityApplication.contact_person.ilike(search_filter)) |
            (CommunityApplication.email.ilike(search_filter))
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
    
    # 총 개수
    total_count = query.count()
    
    # 페이지네이션
    offset = (page - 1) * limit
    applications = query.offset(offset).limit(limit).all()
    
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


@router.get("/admin/applications/{application_id}", response_model=CommunityApplicationResponse)
def get_application_detail(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """신청서 상세 정보를 조회합니다 (슈퍼어드민 전용)."""
    
    application = db.query(CommunityApplication).filter(
        CommunityApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다.")
    
    return application


@router.put("/admin/applications/{application_id}/approve", response_model=ApplicationApprovalResponse)
def approve_application(
    application_id: int,
    request: ApplicationApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """신청서를 승인합니다 (슈퍼어드민 전용)."""
    
    application = db.query(CommunityApplication).filter(
        CommunityApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다.")
    
    if application.status != "pending":
        raise HTTPException(status_code=400, detail="이미 처리된 신청서입니다.")
    
    try:
        # 임시 비밀번호 생성
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        username = f"{application.organization_name.lower().replace(' ', '_')}_community"
        
        # 사용자 계정 생성 (간단한 버전)
        # TODO: 실제 사용자 계정 생성 로직 구현 필요
        
        # 신청서 상태 업데이트
        application.status = "approved"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        application.notes = request.notes
        
        db.commit()
        
        # TODO: 승인 이메일 발송
        
        return ApplicationApprovalResponse(
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
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"승인 처리 중 오류가 발생했습니다: {str(e)}")


@router.put("/admin/applications/{application_id}/reject", response_model=ApplicationApprovalResponse)
def reject_application(
    application_id: int,
    request: ApplicationRejection,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """신청서를 반려합니다 (슈퍼어드민 전용)."""
    
    application = db.query(CommunityApplication).filter(
        CommunityApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다.")
    
    if application.status != "pending":
        raise HTTPException(status_code=400, detail="이미 처리된 신청서입니다.")
    
    try:
        # 신청서 상태 업데이트
        application.status = "rejected"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        application.rejection_reason = request.rejection_reason
        application.notes = request.notes
        
        db.commit()
        
        # TODO: 반려 이메일 발송
        
        return ApplicationApprovalResponse(
            success=True,
            message="신청서가 반려되었습니다.",
            data={
                "application_id": application.id,
                "status": application.status,
                "reviewed_at": application.reviewed_at.isoformat()
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"반려 처리 중 오류가 발생했습니다: {str(e)}")


@router.get("/admin/applications/{application_id}/attachments/{filename}")
def download_attachment(
    application_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """첨부파일을 다운로드합니다 (슈퍼어드민 전용)."""
    
    application = db.query(CommunityApplication).filter(
        CommunityApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다.")
    
    # 파일 경로 구성
    file_dir = os.path.join(UPLOAD_DIR, str(application_id))
    
    # 업로드된 파일 중에서 찾기
    if application.attachments:
        try:
            attachments = json.loads(application.attachments)
            for attachment in attachments:
                if attachment["filename"] == filename:
                    file_path = attachment["path"]
                    if os.path.exists(file_path):
                        return FileResponse(
                            path=file_path,
                            filename=filename,
                            media_type='application/octet-stream'
                        )
        except Exception:
            pass
    
    raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")