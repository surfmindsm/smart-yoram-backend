from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core.security import get_password_hash, verify_password


router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = (
        db.query(models.User).filter(models.User.username == user_in.username).first()
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        church_id=user_in.church_id,
        role=user_in.role,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # Update password if provided
    if user_in.password is not None:
        current_user.hashed_password = get_password_hash(user_in.password)
        # Clear first login flag when password is changed
        if current_user.is_first:
            current_user.is_first = False

    # Update other fields
    update_data = user_in.dict(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/update-first-login", response_model=dict)
def update_first_login_status(
    *,
    db: Session = Depends(deps.get_db),
    is_first: bool = Body(..., embed=True),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update first login status. Special endpoint for mobile app.
    """
    current_user.is_first = is_first
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "success": True,
        "message": f"is_first updated to {is_first}",
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "is_first": current_user.is_first,
        },
    }


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user
