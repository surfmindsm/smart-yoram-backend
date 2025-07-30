from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Member])
def read_members(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.church_id:
        members = (
            db.query(models.Member)
            .filter(models.Member.church_id == current_user.church_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    elif current_user.is_superuser:
        members = db.query(models.Member).offset(skip).limit(limit).all()
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return members


@router.post("/", response_model=schemas.Member)
def create_member(
    *,
    db: Session = Depends(deps.get_db),
    member_in: schemas.MemberCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if not current_user.is_superuser and current_user.church_id != member_in.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    member = models.Member(**member_in.dict())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/{member_id}", response_model=schemas.Member)
def read_member(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not current_user.is_superuser and member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return member


@router.put("/{member_id}", response_model=schemas.Member)
def update_member(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    member_in: schemas.MemberUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not current_user.is_superuser and member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = member_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)

    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}")
def delete_member(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if not current_user.is_superuser and member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(member)
    db.commit()
    return {"message": "Member deleted successfully"}
