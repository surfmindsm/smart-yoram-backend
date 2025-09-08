"""
커뮤니티 회원 신청 관리자 API 엔드포인트
슈퍼어드민 전용 - 신청서 승인/반려 관리
"""

from typing import Any, List, Optional
from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, and_

from app import models, schemas
from app.api import deps
from app.utils.file_upload import get_uploader
from app.core.security import get_password_hash, generate_password

router = APIRouter()


@router.get("/applications", response_model=schemas.CommunityApplicationList)
def list_community_applications(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    status: Optional[str] = Query("all", description="상태 필터"),
    applicant_type: Optional[str] = Query("all", description="신청자 유형 필터"),
    search: Optional[str] = Query(None, description="검색어"),
    sort_by: Optional[str] = Query("submitted_at", description="정렬 기준"),
    sort_order: Optional[str] = Query("desc", description="정렬 순서")
) -> Any:
    """
    커뮤니티 회원 신청서 목록 조회 (슈퍼어드민 전용)
    """
    try:
        # 기본 쿼리
        query = db.query(models.CommunityApplication)
        
        # 상태 필터
        if status and status != "all":
            if status in ["pending", "approved", "rejected"]:
                query = query.filter(models.CommunityApplication.status == status)
        
        # 신청자 유형 필터
        if applicant_type and applicant_type != "all":
            if applicant_type in ["company", "individual", "musician", "minister", "organization", "other"]:
                query = query.filter(models.CommunityApplication.applicant_type == applicant_type)
        
        # 검색 필터
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    models.CommunityApplication.organization_name.ilike(search_pattern),
                    models.CommunityApplication.contact_person.ilike(search_pattern),
                    models.CommunityApplication.email.ilike(search_pattern)
                )
            )
        
        # 정렬
        sort_field = getattr(models.CommunityApplication, sort_by, models.CommunityApplication.submitted_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))
        
        # 총 개수
        total_count = query.count()
        total_pages = (total_count + limit - 1) // limit
        
        # 페이지네이션
        offset = (page - 1) * limit
        applications = query.offset(offset).limit(limit).all()
        
        # 응답 데이터 구성
        application_responses = []
        for app in applications:
            app_data = schemas.CommunityApplicationResponse.from_orm(app)
            app_data.applicant_type_display = app.applicant_type_display
            app_data.status_display = app.status_display
            
            # 검토자 정보 추가
            if app.reviewer:
                app_data.reviewer_info = {
                    "id": app.reviewer.id,
                    "name": app.reviewer.full_name or app.reviewer.username,
                    "email": app.reviewer.email
                }
            
            application_responses.append(app_data)
        
        # 통계 계산
        statistics = _calculate_statistics(db)
        
        # 페이지네이션 정보
        pagination = {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "per_page": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        
        return schemas.CommunityApplicationList(
            applications=application_responses,
            pagination=pagination,
            statistics=statistics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 신청서 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="신청서 목록 조회 실패")


@router.get("/applications/{application_id}", response_model=schemas.CommunityApplicationResponse)
def get_community_application_detail(
    application_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    커뮤니티 회원 신청서 상세 조회 (슈퍼어드민 전용)
    """
    try:
        application = db.query(models.CommunityApplication).filter(
            models.CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다")
        
        # 상세 응답 구성
        app_data = schemas.CommunityApplicationResponse.from_orm(application)
        app_data.applicant_type_display = application.applicant_type_display
        app_data.status_display = application.status_display
        
        # 검토자 정보 추가
        if application.reviewer:
            app_data.reviewer_info = {
                "id": application.reviewer.id,
                "name": application.reviewer.full_name or application.reviewer.username,
                "email": application.reviewer.email
            }
        
        return app_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 신청서 상세 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="신청서 상세 조회 실패")


@router.put("/applications/{application_id}/approve", response_model=schemas.ApplicationApprovalResponse)
def approve_community_application(
    application_id: int,
    approval_data: schemas.ApplicationApproval,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    커뮤니티 회원 신청서 승인 (슈퍼어드민 전용)
    - 승인 시 자동으로 사용자 계정 생성
    - 승인 완료 이메일 발송
    """
    try:
        # 신청서 조회
        application = db.query(models.CommunityApplication).filter(
            models.CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다")
        
        if application.status != "pending":
            raise HTTPException(status_code=400, detail=f"대기 중인 신청서만 승인할 수 있습니다. (현재 상태: {application.status_display})")
        
        # 이메일 중복 체크 (사용자 테이블)
        existing_user = db.query(models.User).filter(models.User.email == application.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")
        
        # 사용자 계정 생성
        username = _generate_username(application.organization_name, application.applicant_type)
        temporary_password = generate_password(12)  # 12자리 임시 비밀번호
        hashed_password = get_password_hash(temporary_password)
        
        # 중복되지 않는 사용자명 생성
        base_username = username
        counter = 1
        while db.query(models.User).filter(models.User.username == username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # 새 사용자 생성
        new_user = models.User(
            email=application.email,
            username=username,
            hashed_password=hashed_password,
            full_name=application.contact_person,
            phone=application.phone,
            church_id=None,  # 커뮤니티 사용자는 교회 소속 없음
            role="community_user",
            is_active=True,
            is_superuser=False,
            is_first=True  # 최초 로그인 시 비밀번호 변경 필요
        )
        
        db.add(new_user)
        db.flush()  # 사용자 ID 생성
        
        # 신청서 승인 처리
        application.status = "approved"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        application.notes = approval_data.notes
        
        db.commit()
        
        # 응답 데이터 구성
        response_data = {
            "application_id": application.id,
            "status": application.status,
            "reviewed_at": application.reviewed_at.isoformat(),
            "user_account": {
                "username": username,
                "temporary_password": temporary_password,
                "login_url": "https://admin.smartyoram.com/login"
            }
        }
        
        print(f"✅ 커뮤니티 신청서 승인 완료: {application.id} - {application.organization_name}")
        print(f"   생성된 계정: {username}")
        
        # TODO: 이메일 발송 (향후 구현)
        # send_approval_email(application, username, temporary_password)
        
        return schemas.ApplicationApprovalResponse(
            success=True,
            message="신청서가 승인되었습니다. 계정 정보를 신청자에게 이메일로 발송했습니다.",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 신청서 승인 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"신청서 승인 실패: {str(e)}")


@router.put("/applications/{application_id}/reject", response_model=schemas.ApplicationRejectionResponse)
def reject_community_application(
    application_id: int,
    rejection_data: schemas.ApplicationRejection,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    커뮤니티 회원 신청서 반려 (슈퍼어드민 전용)
    """
    try:
        # 신청서 조회
        application = db.query(models.CommunityApplication).filter(
            models.CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다")
        
        if application.status != "pending":
            raise HTTPException(status_code=400, detail=f"대기 중인 신청서만 반려할 수 있습니다. (현재 상태: {application.status_display})")
        
        # 신청서 반려 처리
        application.status = "rejected"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = current_user.id
        application.rejection_reason = rejection_data.rejection_reason
        application.notes = rejection_data.notes
        
        db.commit()
        
        # 응답 데이터 구성
        response_data = {
            "application_id": application.id,
            "status": application.status,
            "reviewed_at": application.reviewed_at.isoformat()
        }
        
        print(f"✅ 커뮤니티 신청서 반려 완료: {application.id} - {application.organization_name}")
        print(f"   반려 사유: {rejection_data.rejection_reason}")
        
        # TODO: 이메일 발송 (향후 구현)
        # send_rejection_email(application, rejection_data.rejection_reason)
        
        return schemas.ApplicationRejectionResponse(
            success=True,
            message="신청서가 반려되었습니다. 반려 사유를 신청자에게 이메일로 발송했습니다.",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ 신청서 반려 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"신청서 반려 실패: {str(e)}")


@router.get("/applications/{application_id}/attachments/{filename}")
def download_attachment(
    application_id: int,
    filename: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    첨부파일 다운로드 (슈퍼어드민 전용)
    """
    try:
        # 신청서 존재 확인
        application = db.query(models.CommunityApplication).filter(
            models.CommunityApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="신청서를 찾을 수 없습니다")
        
        # 파일 경로 찾기
        uploader = get_uploader()
        file_path = uploader.get_file_path(application_id, filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # 파일 다운로드 응답
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 파일 다운로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="파일 다운로드 실패")


@router.get("/statistics")
def get_community_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    커뮤니티 신청 통계 조회 (슈퍼어드민 전용)
    """
    try:
        statistics = _calculate_statistics(db)
        
        # 추가 통계 정보
        from sqlalchemy import func
        
        # 월별 신청 통계 (최근 6개월)
        monthly_stats = db.query(
            func.date_format(models.CommunityApplication.submitted_at, '%Y-%m').label('month'),
            func.count(models.CommunityApplication.id).label('count')
        ).group_by(
            func.date_format(models.CommunityApplication.submitted_at, '%Y-%m')
        ).order_by('month DESC').limit(6).all()
        
        # 신청자 유형별 통계
        type_stats = db.query(
            models.CommunityApplication.applicant_type,
            func.count(models.CommunityApplication.id).label('count')
        ).group_by(models.CommunityApplication.applicant_type).all()
        
        statistics.update({
            "monthly_applications": [{"month": m[0], "count": m[1]} for m in monthly_stats],
            "applications_by_type": [{"type": t[0], "count": t[1]} for t in type_stats]
        })
        
        return {"success": True, "data": statistics}
        
    except Exception as e:
        print(f"❌ 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="통계 조회 실패")


# 유틸리티 함수들
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


def _generate_username(organization_name: str, applicant_type: str) -> str:
    """사용자명 자동 생성"""
    # 영문자와 숫자만 남기기
    clean_name = "".join(c for c in organization_name if c.isalnum())[:10]
    if not clean_name:
        clean_name = applicant_type
    
    # 타임스탬프 추가로 유니크하게
    import time
    timestamp = str(int(time.time()))[-6:]  # 마지막 6자리
    
    return f"{clean_name}_{applicant_type}_{timestamp}".lower()