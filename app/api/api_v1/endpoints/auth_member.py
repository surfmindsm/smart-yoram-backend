from datetime import timedelta
from typing import Any, Union
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
def login_member(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login for members.
    Members can log in with email or phone number as username.
    """
    # Try to find user by email first
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # If not found by email, try phone number
    if not user:
        user = db.query(models.User).filter(models.User.phone == form_data.username).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Check if user has member profile
    member = db.query(models.Member).filter(models.Member.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=403, detail="User is not a member")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/access-token", response_model=schemas.TokenWithUser)
def login_member_access_token(
    db: Session = Depends(deps.get_db),
    username: str = Body(...),
    password: str = Body(...),
) -> Any:
    """
    Login endpoint for members with user information.
    Returns token and user details.
    """
    # Try to find user by email first
    user = db.query(models.User).filter(models.User.email == username).first()
    
    # If not found by email, try phone number
    if not user:
        user = db.query(models.User).filter(models.User.phone == username).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Check if user has member profile
    member = db.query(models.Member).filter(models.Member.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=403, detail="User is not a member")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user,
        "member": member
    }


@router.post("/password-reset-request")
def request_password_reset(
    *,
    db: Session = Depends(deps.get_db),
    email: str = Body(..., embed=True),
) -> Any:
    """
    Request password reset for member.
    Sends new temporary password to email.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Check if user has member profile
    member = db.query(models.Member).filter(models.Member.user_id == user.id).first()
    if not member:
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate new temporary password
    from app.utils.password import generate_temporary_password
    from app.utils.encryption import encrypt_password
    from app.utils.email import send_temporary_password_email
    
    temp_password = generate_temporary_password()
    
    # Update user password
    user.hashed_password = security.get_password_hash(temp_password)
    user.encrypted_password = encrypt_password(temp_password)
    
    # Get church name
    church = db.query(models.Church).filter(models.Church.id == member.church_id).first()
    
    # Send email
    send_temporary_password_email(
        to_email=user.email,
        member_name=member.name,
        church_name=church.name if church else "교회",
        temp_password=temp_password
    )
    
    db.commit()
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/change-password")
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Change password for current member.
    """
    if not security.verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Check if user has member profile
    member = db.query(models.Member).filter(models.Member.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=403, detail="User is not a member")
    
    from app.utils.encryption import encrypt_password
    
    # Update password
    current_user.hashed_password = security.get_password_hash(new_password)
    current_user.encrypted_password = encrypt_password(new_password)
    
    db.commit()
    
    return {"message": "Password changed successfully"}