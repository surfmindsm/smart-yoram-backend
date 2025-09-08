"""
커뮤니티 회원 신청 API 엔드포인트
외부 업체/개인의 회원가입 신청 처리
"""

from typing import Any, List, Optional
from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, and_

from app import models, schemas
from app.api import deps
from app.utils.file_upload import get_uploader
from app.core.security import get_password_hash, generate_password

router = APIRouter()


@router.post("/applications", response_model=schemas.CommunityApplicationSubmitResponse)
def submit_community_application(
    request: Request,
    # 폼 데이터 (multipart/form-data)
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
    # 파일 업로드 (선택사항)
    files: List[UploadFile] = File(default=[]),
    # 데이터베이스 세션
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    커뮤니티 회원 신청서 제출
    - 인증 불필요 (공개 API)
    - 파일 업로드 지원
    - 이메일 중복 체크
    """
    try:
        # 요청 데이터 검증
        if applicant_type not in ['company', 'individual', 'musician', 'minister', 'organization', 'other']:
            raise HTTPException(status_code=400, detail="잘못된 신청자 유형입니다")
        
        if not all([organization_name.strip(), contact_person.strip(), email.strip(), phone.strip(), description.strip()]):
            raise HTTPException(status_code=400, detail="필수 입력 항목이 누락되었습니다")
        
        # 이메일 중복 체크 (승인된 신청서만)
        existing_application = db.query(models.CommunityApplication).filter(
            models.CommunityApplication.email == email.lower().strip(),
            models.CommunityApplication.status == "approved"
        ).first()
        
        if existing_application:
            return schemas.CommunityApplicationSubmitResponse(
                success=False,
                message="이미 등록된 이메일입니다.",
                data={"error_code": "EMAIL_ALREADY_EXISTS"}
            )
        
        # 신청서 생성
        application = models.CommunityApplication(
            applicant_type=applicant_type,
            organization_name=organization_name.strip(),
            contact_person=contact_person.strip(),
            email=email.lower().strip(),
            phone=phone.strip(),
            business_number=business_number.strip() if business_number else None,
            address=address.strip() if address else None,
            description=description.strip(),
            service_area=service_area.strip() if service_area else None,
            website=website.strip() if website else None,
            status="pending"
        )
        
        db.add(application)
        db.flush()  # ID 생성을 위해 flush
        
        # 파일 업로드 처리
        uploaded_files = []
        if files and any(f.filename for f in files if f.filename):  # 실제 파일이 있는 경우만
            uploader = get_uploader()
            upload_result = uploader.upload_files(files, application.id)
            
            if upload_result["success"] and upload_result["files"]:
                uploaded_files = upload_result["files"]
                # 첨부파일 정보를 JSON으로 저장
                attachments_json = json.dumps(uploaded_files, ensure_ascii=False)
                application.attachments = attachments_json
        
        db.commit()
        db.refresh(application)
        
        # 응답 데이터 구성
        response_data = {
            "application_id": application.id,
            "status": application.status,
            "submitted_at": application.submitted_at.isoformat(),
            "uploaded_files": len(uploaded_files)
        }
        
        print(f"✅ 커뮤니티 신청서 제출 완료: {application.id} - {application.organization_name}")
        
        return schemas.CommunityApplicationSubmitResponse(
            success=True,
            message="신청서가 성공적으로 제출되었습니다. 검토 후 이메일로 결과를 알려드립니다.",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 신청서 제출 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"신청서 제출 실패: {str(e)}")


@router.get("/applications/{application_id}", response_model=schemas.CommunityApplicationResponse)
def get_community_application(
    application_id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    신청서 상세 조회 (공개 - 신청자가 확인용)
    보안상 민감한 정보는 제외하고 반환
    """
    try:
        application = db.query(models.CommunityApplication).filter(
            models.CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다")
        
        # 공개 정보만 포함
        response_data = schemas.CommunityApplicationResponse.from_orm(application)
        response_data.applicant_type_display = application.applicant_type_display
        response_data.status_display = application.status_display
        
        # 민감한 정보 제거
        response_data.reviewed_by = None
        response_data.notes = None
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 신청서 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="신청서 조회 실패")


@router.get("/applications/{application_id}/status")
def get_application_status(
    application_id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    신청서 상태 간단 조회 (공개)
    신청자가 상태만 확인할 때 사용
    """
    try:
        application = db.query(models.CommunityApplication).filter(
            models.CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다")
        
        return {
            "success": True,
            "data": {
                "application_id": application.id,
                "status": application.status,
                "status_display": application.status_display,
                "submitted_at": application.submitted_at.isoformat(),
                "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="상태 조회 실패")


# 유틸리티 함수들
def _build_search_filter(search_term: str):
    """검색 필터 생성"""
    if not search_term:
        return None
    
    search_pattern = f"%{search_term.strip()}%"
    return or_(
        models.CommunityApplication.organization_name.ilike(search_pattern),
        models.CommunityApplication.contact_person.ilike(search_pattern),
        models.CommunityApplication.email.ilike(search_pattern)
    )


def _build_sort_expression(sort_by: str, sort_order: str):
    """정렬 표현식 생성"""
    sort_field = getattr(models.CommunityApplication, sort_by, models.CommunityApplication.submitted_at)
    return desc(sort_field) if sort_order == "desc" else asc(sort_field)


def _calculate_statistics(db: Session) -> dict:
    """신청서 통계 계산"""
    try:
        total = db.query(models.CommunityApplication).count()
        pending = db.query(models.CommunityApplication).filter(models.CommunityApplication.status == "pending").count()
        approved = db.query(models.CommunityApplication).filter(models.CommunityApplication.status == "approved").count()
        rejected = db.query(models.CommunityApplication).filter(models.CommunityApplication.status == "rejected").count()
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected
        }
    except Exception as e:
        print(f"⚠️ 통계 계산 실패: {e}")
        return {"total": 0, "pending": 0, "approved": 0, "rejected": 0}


def generate_username(organization_name: str, applicant_type: str) -> str:
    """사용자명 자동 생성"""
    # 영문자와 숫자만 남기기
    clean_name = "".join(c for c in organization_name if c.isalnum())[:10]
    if not clean_name:
        clean_name = applicant_type
    
    # 타임스탬프 추가로 유니크하게
    import time
    timestamp = str(int(time.time()))[-6:]  # 마지막 6자리
    
    return f"{clean_name}_{applicant_type}_{timestamp}".lower()