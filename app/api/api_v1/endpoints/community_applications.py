from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
    Response,
)
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
from passlib.context import CryptContext

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
    AttachmentInfo,
)
from app.models.user import User
from app.models.church import Church
from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

# 파일 업로드 설정
UPLOAD_DIR = "uploads/community_applications"
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 5

# 유효한 신청자 유형
VALID_APPLICANT_TYPES = {
    "company",
    "individual",
    "musician",
    "minister",
    "organization",
    "church_admin",
    "other",
}
VALID_STATUS_TYPES = {"pending", "approved", "rejected"}


def safe_file_save(
    files: List[UploadFile], application_id: int
) -> List[AttachmentInfo]:
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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{secrets.token_hex(4)}_{file.filename}"
            file_path = os.path.join(app_upload_dir, safe_filename)

            # 파일 저장
            with open(file_path, "wb") as f:
                f.write(file_content)

            saved_files.append(
                AttachmentInfo(
                    filename=file.filename, path=file_path, size=len(file_content)
                )
            )

        except Exception as e:
            logger.error(f"File save error: {str(e)}")
            continue

    return saved_files


@router.post(
    "/applications",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_community_application(
    applicant_type: str = Form(...),
    organization_name: str = Form(...),
    contact_person: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    description: str = Form(...),
    business_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    service_area: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    agree_terms: bool = Form(...),
    agree_privacy: bool = Form(...),
    agree_marketing: bool = Form(default=False),
    attachments: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    """커뮤니티 회원 신청서를 제출합니다."""

    try:
        # 입력 데이터 검증
        if applicant_type not in VALID_APPLICANT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid applicant_type. Must be one of: {', '.join(VALID_APPLICANT_TYPES)}",
            )

        # 비밀번호 길이 검증
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호는 최소 8자 이상이어야 합니다.",
            )

        # 필수 약관 동의 검증
        if not agree_terms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이용약관에 동의해야 합니다.",
            )

        if not agree_privacy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="개인정보처리방침에 동의해야 합니다.",
            )

        # 이메일 중복 체크
        existing_app = (
            db.query(CommunityApplication)
            .filter(CommunityApplication.email == email)
            .first()
        )

        if existing_app:
            return StandardResponse(
                success=False,
                message="이미 등록된 이메일입니다.",
                data={"error_code": "EMAIL_ALREADY_EXISTS"},
            )

        # 비밀번호 해싱
        password_hash = pwd_context.hash(password)

        # 신청서 생성
        application = CommunityApplication(
            applicant_type=applicant_type,
            organization_name=organization_name[:200],  # 길이 제한
            contact_person=contact_person[:100],
            email=email[:255],
            phone=phone[:20],
            password_hash=password_hash,
            business_number=business_number[:50] if business_number else None,
            address=address,
            description=description,
            service_area=service_area[:200] if service_area else None,
            website=website[:500] if website else None,
            agree_terms=agree_terms,
            agree_privacy=agree_privacy,
            agree_marketing=agree_marketing,
            status="pending",
        )

        db.add(application)
        db.flush()  # ID 얻기 위해 flush

        # 파일 업로드 처리 (안전하게)
        if (
            attachments
            and len([f for f in attachments if f and f.filename]) > MAX_FILES
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"최대 {MAX_FILES}개 파일만 업로드 가능합니다.",
            )

        saved_files = []
        if attachments:
            saved_files = safe_file_save(attachments, application.id)
            if saved_files:
                application.attachments = json.dumps(
                    [file.dict() for file in saved_files]
                )

        db.commit()

        logger.info(f"New community application submitted: {application.id}")

        return StandardResponse(
            success=True,
            message="신청서가 성공적으로 제출되었습니다.",
            data={
                "application_id": application.id,
                "status": application.status,
                "submitted_at": application.submitted_at.isoformat(),
            },
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Application submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="신청서 제출 중 오류가 발생했습니다.",
        )


@router.get("/admin/applications/debug", response_model=dict)
def debug_community_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """디버깅용 Mock 데이터 엔드포인트"""
    try:
        # 테이블 존재 확인
        table_count = db.execute(
            text("SELECT COUNT(*) FROM community_applications")
        ).scalar()

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
                        "reviewed_at": None,
                    }
                ],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 1,
                    "total_count": 1,
                    "per_page": 20,
                    "has_next": False,
                    "has_prev": False,
                },
                "statistics": {"pending": 1, "approved": 0, "rejected": 0, "total": 1},
            },
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "table_exists": False}


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
    current_user: User = Depends(get_current_active_superuser),
):
    """신청서 목록을 조회합니다 (슈퍼어드민 전용)."""

    try:
        # 기본 쿼리
        query = db.query(CommunityApplication)

        # 필터링
        if (
            status_filter
            and status_filter != "all"
            and status_filter in VALID_STATUS_TYPES
        ):
            query = query.filter(CommunityApplication.status == status_filter)

        if (
            applicant_type
            and applicant_type != "all"
            and applicant_type in VALID_APPLICANT_TYPES
        ):
            query = query.filter(CommunityApplication.applicant_type == applicant_type)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (CommunityApplication.organization_name.ilike(search_term))
                | (CommunityApplication.contact_person.ilike(search_term))
                | (CommunityApplication.email.ilike(search_term))
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
            "pending": stats_query.filter(
                CommunityApplication.status == "pending"
            ).count(),
            "approved": stats_query.filter(
                CommunityApplication.status == "approved"
            ).count(),
            "rejected": stats_query.filter(
                CommunityApplication.status == "rejected"
            ).count(),
            "total": stats_query.count(),
        }

        return CommunityApplicationsListResponse(
            applications=applications,
            pagination={
                "current_page": page,
                "total_pages": (total_count + limit - 1) // limit,
                "total_count": total_count,
                "per_page": limit,
                "has_next": page < (total_count + limit - 1) // limit,
                "has_prev": page > 1,
            },
            statistics=statistics,
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        logger.error(f"Application list error: {str(e)}")
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"신청서 목록 조회 중 오류가 발생했습니다: {str(e)}",
        )


@router.get(
    "/admin/applications/{application_id}", response_model=CommunityApplicationResponse
)
def get_community_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """신청서 상세 정보를 조회합니다 (슈퍼어드민 전용)."""

    application = (
        db.query(CommunityApplication)
        .filter(CommunityApplication.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="신청서를 찾을 수 없습니다."
        )

    # 첨부파일 정보 파싱
    if application.attachments:
        try:
            attachments_data = json.loads(application.attachments)
            application.attachments = attachments_data
        except:
            application.attachments = None

    return application


@router.put(
    "/admin/applications/{application_id}/approve", response_model=StandardResponse
)
def approve_community_application(
    application_id: int,
    request: ApplicationApproval,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """신청서를 승인합니다 (슈퍼어드민 전용)."""

    # 수동으로 CORS 헤더 추가 (500 에러 시에도 CORS 헤더 보장)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"

    try:
        application = (
            db.query(CommunityApplication)
            .filter(CommunityApplication.id == application_id)
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="신청서를 찾을 수 없습니다.",
            )

        if application.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 처리된 신청서입니다.",
            )

        # 데이터 검증
        logger.info(f"Validating application {application_id} data")

        # password_hash가 없는 경우 임시 비밀번호 생성
        if not hasattr(application, 'password_hash') or not application.password_hash:
            logger.warning(f"Application {application_id} missing password_hash, generating temporary password")
            temp_password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
            )
            password_hash = pwd_context.hash(temp_password)
            logger.info(f"Generated temporary password for {application.email}: {temp_password}")
        else:
            password_hash = application.password_hash
            temp_password = None

        if not application.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="신청서에 이메일이 없습니다.",
            )

        # 이메일 중복 확인 (승인 전에 미리 확인)
        existing_user = db.query(User).filter(User.email == application.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 등록된 이메일 주소입니다: {application.email}",
            )

        logger.info(f"Application {application_id} validation passed")

        # 승인 처리
        application.status = "approved"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        application.notes = request.notes

        # 사용자 계정 생성
        user_role = (
            "church_admin"
            if application.applicant_type == "church_admin"
            else "community_user"
        )
        church_id = 9998  # 기본값: 커뮤니티 전용 테넌트

        # 커뮤니티 전용 교회가 없는 경우 생성
        community_church = db.query(Church).filter(Church.id == 9998).first()
        if not community_church:
            logger.info("Creating community church with ID 9998")
            community_church = Church(
                id=9998,
                name="스마트요람 커뮤니티",
                subscription_plan="community",  # 커뮤니티 전용 플랜
                is_active=True,
            )
            db.add(community_church)
            db.flush()
            logger.info("Community church created successfully")

        # 교회 관리자인 경우 교회 생성 또는 연결
        if application.applicant_type == "church_admin":
            # 기존 교회가 있는지 확인
            existing_church = (
                db.query(Church)
                .filter(Church.name.ilike(f"%{application.organization_name}%"))
                .first()
            )

            if existing_church:
                church_id = existing_church.id
                logger.info(
                    f"Using existing church: {existing_church.name} (ID: {church_id})"
                )
            else:
                # 새 교회 생성
                new_church = Church(
                    name=application.organization_name,
                    address=application.address,
                    phone=application.phone,
                    is_active=True,
                )
                db.add(new_church)
                db.flush()
                church_id = new_church.id
                logger.info(f"Created new church: {new_church.name} (ID: {church_id})")

        # 사용자 계정 생성 (신청 시 입력한 비밀번호 해시 사용)
        logger.info(f"Creating user account for {application.email}")
        new_user = User(
            email=application.email,
            username=application.email,  # 이메일을 username으로 사용
            hashed_password=password_hash,  # 위에서 처리된 password_hash 사용
            full_name=application.contact_person,
            phone=application.phone,
            church_id=church_id,
            role=user_role,
            is_active=True,
            is_superuser=False,
            is_first=True,
        )
        db.add(new_user)

        db.commit()

        logger.info(f"Application approved: {application_id} by user {current_user.id}")
        logger.info(f"User account created: {new_user.email} with role {user_role}")

        # 교회 정보 가져오기
        created_church = db.query(Church).filter(Church.id == church_id).first()
        
        # 응답 데이터 구성
        response_data = {
            "application_id": application.id,
            "status": application.status,
            "reviewed_at": application.reviewed_at.isoformat(),
            "user_account": {
                "email": application.email,
                "password_set": True,
                "user_role": user_role,
                "church_id": church_id,
                "login_url": "https://admin.smartyoram.com/login",
            },
            "church": {
                "id": created_church.id,
                "name": created_church.name,
                "subscription_plan": created_church.subscription_plan,
                "is_community": created_church.subscription_plan == "community",
            },
        }
        
        # 임시 비밀번호가 생성된 경우 추가
        if temp_password:
            response_data["user_account"]["temporary_password"] = temp_password
            response_data["user_account"]["password_note"] = "기존 신청서에 비밀번호가 없어 임시 비밀번호를 생성했습니다."

        return StandardResponse(
            success=True,
            message="신청서가 승인되었습니다. 사용자 계정이 생성되었습니다.",
            data=response_data,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        import traceback

        error_details = traceback.format_exc()
        logger.error(f"Application approval error: {str(e)}")
        logger.error(f"Full traceback: {error_details}")

        # 개발 환경에서는 더 구체적인 에러 정보 제공
        detail_message = f"승인 처리 에러: {str(e)} | 유형: {type(e).__name__}"

        # 500 에러 시에도 CORS 헤더 추가
        error_response = HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail_message,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
            },
        )
        raise error_response


@router.put(
    "/admin/applications/{application_id}/reject", response_model=StandardResponse
)
def reject_community_application(
    application_id: int,
    request: ApplicationRejection,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """신청서를 반려합니다 (슈퍼어드민 전용)."""

    try:
        application = (
            db.query(CommunityApplication)
            .filter(CommunityApplication.id == application_id)
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="신청서를 찾을 수 없습니다.",
            )

        if application.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 처리된 신청서입니다.",
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
                "reviewed_at": application.reviewed_at.isoformat(),
            },
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Application rejection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="반려 처리 중 오류가 발생했습니다.",
        )


@router.get("/admin/applications/{application_id}/attachments/{filename}")
def download_attachment(
    application_id: int,
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """첨부파일을 다운로드합니다 (슈퍼어드민 전용)."""

    try:
        # 신청서 존재 확인
        application = (
            db.query(CommunityApplication)
            .filter(CommunityApplication.id == application_id)
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="신청서를 찾을 수 없습니다.",
            )

        # 첨부파일 정보 확인
        if not application.attachments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="첨부파일이 없습니다."
            )

        try:
            attachments_data = json.loads(application.attachments)
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="첨부파일 정보를 읽을 수 없습니다.",
            )

        # 요청된 파일 찾기
        target_file = None
        for attachment in attachments_data:
            if attachment.get("filename") == filename:
                target_file = attachment
                break

        if not target_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="요청한 파일을 찾을 수 없습니다.",
            )

        file_path = target_file.get("path")

        # 파일 존재 확인
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="파일이 서버에 존재하지 않습니다.",
            )

        # 보안 검증 - 파일이 업로드 디렉토리 내에 있는지 확인
        upload_dir_abs = os.path.abspath(UPLOAD_DIR)
        file_path_abs = os.path.abspath(file_path)

        if not file_path_abs.startswith(upload_dir_abs):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="파일 접근이 허용되지 않습니다.",
            )

        logger.info(f"File download: {filename} by user {current_user.id}")

        return FileResponse(
            path=file_path, filename=filename, media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="파일 다운로드 중 오류가 발생했습니다.",
        )
