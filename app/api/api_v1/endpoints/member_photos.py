from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime

from app import models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

UPLOAD_DIR = "static/uploads/members"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/{member_id}/upload-photo", response_model=schemas.Member)
async def upload_member_photo(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload profile photo for a member.
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{member.church_id}_{member_id}_{timestamp}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    
    # Delete old photo if exists
    if member.profile_photo_url:
        old_path = member.profile_photo_url.replace("/static/", "static/")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except:
                pass
    
    # Update member with photo URL
    photo_url = f"/static/uploads/members/{unique_filename}"
    member.profile_photo_url = photo_url
    db.commit()
    db.refresh(member)
    
    return member


@router.delete("/{member_id}/delete-photo", response_model=schemas.Member)
def delete_member_photo(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete profile photo for a member.
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if not member.profile_photo_url:
        raise HTTPException(status_code=400, detail="Member has no profile photo")
    
    # Delete file
    file_path = member.profile_photo_url.replace("/static/", "static/")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not delete file: {str(e)}")
    
    # Update member
    member.profile_photo_url = None
    db.commit()
    db.refresh(member)
    
    return member