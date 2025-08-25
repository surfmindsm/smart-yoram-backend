"""
First Time Setup API Endpoints
초기 설정 관련 API
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app import models, schemas
from app.api import deps
from app.core.security import get_password_hash
from app.utils.encryption import encrypt_password

router = APIRouter()


class FirstTimeSetupRequest(BaseModel):
    """초기 설정 요청 스키마"""

    # Church Information
    church_name: str
    church_address: Optional[str] = None
    church_phone: Optional[str] = None
    pastor_name: Optional[str] = None

    # Admin User Information
    admin_email: EmailStr
    admin_password: str
    admin_name: str
    admin_phone: Optional[str] = None


class FirstTimeSetupResponse(BaseModel):
    """초기 설정 응답 스키마"""

    church: schemas.Church
    admin_user: schemas.User
    message: str


@router.get("/check")
async def check_first_time_setup(db: Session = Depends(deps.get_db)):
    """
    시스템 초기 설정이 필요한지 확인

    Returns:
        - needs_setup: 초기 설정 필요 여부
        - has_churches: 교회 데이터 존재 여부
        - has_superuser: 슈퍼유저 존재 여부
    """
    # 교회 데이터 확인
    church_count = db.query(models.Church).count()

    # 슈퍼유저 확인
    superuser_count = (
        db.query(models.User).filter(models.User.is_superuser == True).count()
    )

    # 어드민 유저 확인
    admin_count = db.query(models.User).filter(models.User.role == "admin").count()

    needs_setup = church_count == 0 or (superuser_count == 0 and admin_count == 0)

    return {
        "needs_setup": needs_setup,
        "has_churches": church_count > 0,
        "has_superuser": superuser_count > 0,
        "has_admin": admin_count > 0,
        "total_churches": church_count,
        "total_users": db.query(models.User).count(),
    }


@router.post("/complete", response_model=FirstTimeSetupResponse)
async def complete_first_time_setup(
    *, db: Session = Depends(deps.get_db), setup_data: FirstTimeSetupRequest
):
    """
    시스템 초기 설정 완료

    1. 첫 번째 교회 생성
    2. 시스템 관리자 계정 생성
    3. 관리자를 교회에 연결
    """
    # 이미 설정이 완료되었는지 확인
    if db.query(models.Church).count() > 0:
        # 이미 교회가 있으면 추가 설정 불가
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System has already been initialized. Churches exist.",
        )

    # 1. 교회 생성
    church = models.Church(
        name=setup_data.church_name,
        address=setup_data.church_address,
        phone=setup_data.church_phone,
        pastor_name=setup_data.pastor_name,
        district_scheme="구역",  # 기본값
        subscription_status="trial",
        subscription_plan="basic",
        member_limit=100,
        is_active=True,
    )
    db.add(church)
    db.flush()  # ID 생성을 위해 flush

    # 2. 관리자 계정 생성
    admin_user = models.User(
        email=setup_data.admin_email,
        username=setup_data.admin_email,  # 이메일을 username으로 사용
        hashed_password=get_password_hash(setup_data.admin_password),
        encrypted_password=encrypt_password(setup_data.admin_password),
        full_name=setup_data.admin_name,
        phone=setup_data.admin_phone,
        church_id=church.id,
        role="admin",
        is_active=True,
        is_superuser=True,  # 첫 번째 관리자는 슈퍼유저 권한 부여
        is_first=False,
    )
    db.add(admin_user)
    db.flush()

    # 3. 관리자 Member 프로필 생성
    admin_member = models.Member(
        church_id=church.id,
        user_id=admin_user.id,
        name=setup_data.admin_name,
        phone=setup_data.admin_phone,
        email=setup_data.admin_email,
        position="pastor",  # 관리자는 목사 직분으로 설정
        department="관리부",
        status="active",
        member_status="active",
    )
    db.add(admin_member)

    # 4. 커밋
    db.commit()
    db.refresh(church)
    db.refresh(admin_user)

    return FirstTimeSetupResponse(
        church=church,
        admin_user=admin_user,
        message="Initial setup completed successfully. You can now login with your admin account.",
    )
