from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.utils.device_parser import parse_user_agent, get_client_ip
from app.utils.activity_logger import activity_logger

try:
    from app.utils.qr_code import generate_member_qr_code
except ImportError:
    # QR code generation is optional
    def generate_member_qr_code(member):
        return None


router = APIRouter()


def create_login_history(
    db: Session, 
    user_id: int, 
    request: Request, 
    status: str = "success"
) -> None:
    """Create a login history record"""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        device_info = parse_user_agent(user_agent)
        
        login_history = models.LoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device=device_info,
            location="서울, 대한민국",  # TODO: Implement GeoIP lookup
            status=status,
            session_start=datetime.utcnow() if status == "success" else None
        )
        
        db.add(login_history)
        db.commit()
        
        print(f"📝 LOGIN HISTORY CREATED: User {user_id}, IP: {ip_address}, Device: {device_info}, Status: {status}")
        
    except Exception as e:
        print(f"❌ Failed to create login history: {e}")
        # Don't fail the login if history creation fails
        db.rollback()


@router.post("/login/access-token", response_model=schemas.TokenWithUser)
def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
) -> Any:
    try:
        print(f"Auth login attempt - username: {form_data.username}")
        # Try to find user by username first
        user = (
            db.query(models.User).filter(models.User.username == form_data.username).first()
        )
        # If not found by username, try email
        if not user:
            user = (
                db.query(models.User).filter(models.User.email == form_data.username).first()
            )
        
        if not user:
            print(f"User not found by username or email: {form_data.username}")
            # Create failed login history for unknown user
            # We'll skip this since we don't have a user_id
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        
        if not security.verify_password(form_data.password, user.hashed_password):
            print(f"Password verification failed for user: {form_data.username}")
            # Create failed login history
            if request:
                create_login_history(db, user.id, request, status="failed")
                # Also create activity log for failed login
                activity_logger.log_login_failure(db, form_data.username, request, "invalid_credentials")
            raise HTTPException(status_code=400, detail="Incorrect username or password")
            
        if not user.is_active:
            print(f"Inactive user: {form_data.username}")
            if request:
                create_login_history(db, user.id, request, status="failed")
                # Also create activity log for inactive user
                activity_logger.log_login_failure(db, form_data.username, request, "inactive_user")
            raise HTTPException(status_code=400, detail="Inactive user")
        
        # Create successful login history and activity log
        if request:
            create_login_history(db, user.id, request, status="success")
            activity_logger.log_login_success(db, str(user.id), request)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "church_id": user.church_id,
            "role": user.role,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_first": user.is_first,
        },
    }


@router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    return current_user


@router.post("/change-password")
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change password for current user
    """
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    db.commit()

    return {"msg": "Password updated successfully"}


@router.post("/complete-first-time-setup", response_model=schemas.User)
def complete_first_time_setup(
    *,
    db: Session = Depends(deps.get_db),
    new_password: str = Body(
        ..., description="New password to replace temporary password"
    ),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Complete first-time setup for new users.
    This endpoint:
    1. Changes the temporary password to a new password
    2. Generates QR code for the member
    3. Sets is_first to False
    """
    if not current_user.is_first:
        raise HTTPException(
            status_code=400, detail="First-time setup already completed"
        )

    # 1. Update password
    current_user.hashed_password = get_password_hash(new_password)
    current_user.encrypted_password = None  # Clear encrypted password

    # 2. Generate QR code if member exists
    member = (
        db.query(models.Member).filter(models.Member.user_id == current_user.id).first()
    )

    if member and not member.qr_code:
        try:
            qr_code_data = generate_member_qr_code(member)
            member.qr_code = qr_code_data
            db.add(member)
        except Exception as e:
            # Log error but don't fail the whole process
            print(f"Error generating QR code: {e}")

    # 3. Mark first-time setup as complete
    current_user.is_first = False

    # Save changes
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/check-first-time")
def check_first_time_status(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Check if user needs to complete first-time setup
    """
    return {
        "is_first": current_user.is_first,
        "user_id": current_user.id,
        "email": current_user.email,
    }
