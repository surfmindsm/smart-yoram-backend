from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.utils.storage import upload_bulletin

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
    
    # Validate that date is not set to None if it's provided
    # The database requires date to be non-null
    if "date" in update_data and update_data["date"] is None:
        raise HTTPException(
            status_code=422, 
            detail="Date field cannot be set to null. Date is required for bulletins."
        )
    
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


@router.post("/{bulletin_id}/upload-file", response_model=schemas.Bulletin)
async def upload_bulletin_file(
    *,
    db: Session = Depends(deps.get_db),
    bulletin_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload bulletin file to Supabase Storage.
    """
    bulletin = (
        db.query(models.Bulletin).filter(models.Bulletin.id == bulletin_id).first()
    )
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin not found")
    
    if bulletin.church_id != current_user.church_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate that bulletin has a date (required for file storage path)
    if bulletin.date is None:
        raise HTTPException(
            status_code=422, 
            detail="Cannot upload file to bulletin without a date. Please update the bulletin with a valid date first."
        )
    
    # Read file content
    file_content = await file.read()
    
    # Upload to Supabase Storage
    success, file_url, error_msg = upload_bulletin(
        file_content=file_content,
        filename=file.filename,
        church_id=bulletin.church_id,
        bulletin_date=str(bulletin.date)
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Update bulletin with file URL
    bulletin.file_url = file_url
    db.commit()
    db.refresh(bulletin)
    
    return bulletin
