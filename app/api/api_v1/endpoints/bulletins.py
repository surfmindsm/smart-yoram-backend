from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Bulletin])
def read_bulletins(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.church_id:
        bulletins = (
            db.query(models.Bulletin)
            .filter(models.Bulletin.church_id == current_user.church_id)
            .order_by(models.Bulletin.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    elif current_user.is_superuser:
        bulletins = (
            db.query(models.Bulletin)
            .order_by(models.Bulletin.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return bulletins


@router.post("/", response_model=schemas.Bulletin)
def create_bulletin(
    *,
    db: Session = Depends(deps.get_db),
    bulletin_in: schemas.BulletinCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if (
        not current_user.is_superuser
        and current_user.church_id != bulletin_in.church_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    bulletin = models.Bulletin(**bulletin_in.dict(), created_by=current_user.id)
    db.add(bulletin)
    db.commit()
    db.refresh(bulletin)
    return bulletin


@router.get("/{bulletin_id}", response_model=schemas.Bulletin)
def read_bulletin(
    *,
    db: Session = Depends(deps.get_db),
    bulletin_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    bulletin = (
        db.query(models.Bulletin).filter(models.Bulletin.id == bulletin_id).first()
    )
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin not found")

    if not current_user.is_superuser and bulletin.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return bulletin


@router.put("/{bulletin_id}", response_model=schemas.Bulletin)
def update_bulletin(
    *,
    db: Session = Depends(deps.get_db),
    bulletin_id: int,
    bulletin_in: schemas.BulletinUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    bulletin = (
        db.query(models.Bulletin).filter(models.Bulletin.id == bulletin_id).first()
    )
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin not found")

    if not current_user.is_superuser and bulletin.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = bulletin_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bulletin, field, value)

    db.add(bulletin)
    db.commit()
    db.refresh(bulletin)
    return bulletin


@router.delete("/{bulletin_id}")
def delete_bulletin(
    *,
    db: Session = Depends(deps.get_db),
    bulletin_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    bulletin = (
        db.query(models.Bulletin).filter(models.Bulletin.id == bulletin_id).first()
    )
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin not found")

    if not current_user.is_superuser and bulletin.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(bulletin)
    db.commit()
    return {"message": "Bulletin deleted successfully"}
