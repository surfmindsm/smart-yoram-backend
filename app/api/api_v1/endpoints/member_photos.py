from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.utils.storage import upload_member_photo, delete_member_photo

router = APIRouter()


@router.post("/{member_id}/upload-photo", response_model=schemas.Member)
async def upload_member_photo_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload profile photo for a member to Supabase Storage.
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Read file content
    file_content = await file.read()
    
    # Upload to Supabase Storage
    success, photo_url, error_msg = upload_member_photo(
        file_content=file_content,
        filename=file.filename,
        church_id=member.church_id,
        member_id=member_id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Delete old photo from Supabase if exists
    if member.profile_photo_url:
        delete_success, delete_error = delete_member_photo(member.profile_photo_url)
        if not delete_success:
            # Log error but don't fail the upload
            print(f"Failed to delete old photo: {delete_error}")
    
    # Update member with new photo URL
    member.profile_photo_url = photo_url
    db.commit()
    db.refresh(member)
    
    return member


@router.delete("/{member_id}/delete-photo", response_model=schemas.Member)
def delete_member_photo_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete profile photo for a member from Supabase Storage.
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if not member.profile_photo_url:
        raise HTTPException(status_code=400, detail="Member has no profile photo")
    
    # Delete from Supabase Storage
    success, error_msg = delete_member_photo(member.profile_photo_url)
    if not success:
        raise HTTPException(status_code=500, detail=f"Could not delete file: {error_msg}")
    
    # Update member
    member.profile_photo_url = None
    db.commit()
    db.refresh(member)
    
    return member