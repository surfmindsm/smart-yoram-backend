from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
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
    request: Request,
    current_user: models.User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...),
) -> Any:
    """
    Upload profile photo for a member to Supabase Storage.
    """
    # DEBUG: Log request details
    try:
        print(f"=== PHOTO UPLOAD DEBUG - Member ID: {member_id} ===")
        print(f"Content-Type: {request.headers.get('content-type')}")
        print(f"User-Agent: {request.headers.get('user-agent')}")
        print(f"Authorization present: {'authorization' in request.headers}")
        
        # Get form data
        form_data = await request.form()
        print(f"Form data keys: {list(form_data.keys())}")
        print(f"Form data items: {[(key, type(value).__name__) for key, value in form_data.items()]}")
        
        # Check if file is received
        print(f"File parameter received: {file is not None}")
        if file:
            print(f"File filename: {file.filename}")
            print(f"File content_type: {file.content_type}")
            print(f"File size: {file.size if hasattr(file, 'size') else 'unknown'}")
        else:
            print("File parameter is None!")
            
        print("=== END DEBUG ===")
        
    except Exception as debug_error:
        print(f"DEBUG ERROR: {debug_error}")
    
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # DEBUG: 권한 체크 상세 로그
    print(f"🚨 PERMISSION CHECK - Member ID: {member_id}")
    print(f"🚨 Member church_id: {member.church_id}")
    print(f"🚨 Current user church_id: {current_user.church_id}")
    print(f"🚨 Current user: {current_user.email} (ID: {current_user.id})")
    print(f"🚨 Is superuser: {current_user.is_superuser}")
    print(f"🚨 User role: {current_user.role}")
    
    # 수정된 권한 체크 (superuser는 모든 교회 접근 가능)
    if not current_user.is_superuser and member.church_id != current_user.church_id:
        print(f"🚨 ACCESS DENIED - Different churches!")
        raise HTTPException(status_code=403, detail=f"Not enough permissions. Member church: {member.church_id}, User church: {current_user.church_id}")
    
    print(f"🚨 ACCESS GRANTED - Permission check passed!")

    # Read file content
    file_content = await file.read()

    # Upload to Supabase Storage
    success, photo_url, error_msg = upload_member_photo(
        file_content=file_content,
        filename=file.filename,
        church_id=member.church_id,
        member_id=member_id,
    )

    if not success:
        raise HTTPException(status_code=400, detail=error_msg)

    print(f"📸 PHOTO UPLOAD SUCCESS - Photo URL: {photo_url}")

    # Delete old photo from Supabase if exists
    old_photo_url = member.profile_photo_url
    if old_photo_url:
        print(f"🗑️ DELETING OLD PHOTO: {old_photo_url}")
        delete_success, delete_error = delete_member_photo(old_photo_url)
        if not delete_success:
            # Log error but don't fail the upload
            print(f"❌ Failed to delete old photo: {delete_error}")
        else:
            print(f"✅ Old photo deleted successfully")

    # Update member with new photo URL
    print(f"💾 UPDATING DATABASE - Member ID: {member_id}")
    print(f"💾 Old profile_photo_url: {member.profile_photo_url}")
    print(f"💾 New profile_photo_url: {photo_url}")
    
    try:
        # Method 1: SQLAlchemy ORM update
        member.profile_photo_url = photo_url
        db.commit()
        print(f"✅ DATABASE COMMIT SUCCESS")
        
        # Force refresh from database
        db.refresh(member)
        print(f"✅ DATABASE REFRESH SUCCESS")
        print(f"💾 Final profile_photo_url in DB: {member.profile_photo_url}")
        
        # Method 2: Direct SQL verification (추가 검증)
        from sqlalchemy import text
        result = db.execute(
            text("SELECT profile_photo_url FROM members WHERE id = :member_id"),
            {"member_id": member_id}
        ).fetchone()
        
        if result:
            actual_url = result[0]
            print(f"🔍 VERIFICATION - Direct SQL query result: {actual_url}")
            
            if actual_url != photo_url:
                print(f"🚨 CRITICAL ERROR: DB value mismatch!")
                print(f"🚨 Expected: {photo_url}")
                print(f"🚨 Actual: {actual_url}")
                
                # Force update with direct SQL
                print(f"🔧 ATTEMPTING DIRECT SQL UPDATE...")
                db.execute(
                    text("UPDATE members SET profile_photo_url = :photo_url, updated_at = CURRENT_TIMESTAMP WHERE id = :member_id"),
                    {"photo_url": photo_url, "member_id": member_id}
                )
                db.commit()
                print(f"🔧 DIRECT SQL UPDATE COMPLETED")
                
                # Re-verify
                verify_result = db.execute(
                    text("SELECT profile_photo_url FROM members WHERE id = :member_id"),
                    {"member_id": member_id}
                ).fetchone()
                print(f"🔍 FINAL VERIFICATION: {verify_result[0] if verify_result else 'NO RESULT'}")
            else:
                print(f"✅ VERIFICATION PASSED - URLs match")
        else:
            print(f"❌ VERIFICATION FAILED - No member found with ID {member_id}")
        
    except Exception as db_error:
        print(f"❌ DATABASE UPDATE ERROR: {db_error}")
        print(f"❌ Error type: {type(db_error).__name__}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(db_error)}")

    # Final refresh to ensure we return the updated data
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
        raise HTTPException(
            status_code=500, detail=f"Could not delete file: {error_msg}"
        )

    # Update member
    member.profile_photo_url = None
    db.commit()
    db.refresh(member)

    return member
