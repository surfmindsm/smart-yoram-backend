from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode
import io
import uuid
from datetime import datetime, timedelta

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.post("/generate/{member_id}", response_model=schemas.QRCode)
def generate_qr_code(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    qr_in: schemas.QRCodeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Generate QR code for a member.
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Deactivate existing QR codes for this member
    existing_codes = db.query(models.QRCode).filter(
        models.QRCode.member_id == member_id,
        models.QRCode.is_active == True
    ).all()
    
    for code in existing_codes:
        code.is_active = False
    
    # Generate unique code
    unique_code = f"{member.church_id}:{member_id}:{uuid.uuid4().hex}"
    
    # Set expiration (default 1 year)
    expires_at = qr_in.expires_at or datetime.utcnow() + timedelta(days=365)
    
    # Create QR code record
    qr_code = models.QRCode(
        church_id=member.church_id,
        member_id=member_id,
        code=unique_code,
        qr_type=qr_in.qr_type,
        is_active=True,
        expires_at=expires_at
    )
    db.add(qr_code)
    db.commit()
    db.refresh(qr_code)
    
    return qr_code


@router.get("/{code}/image")
def get_qr_code_image(
    *,
    db: Session = Depends(deps.get_db),
    code: str,
) -> Any:
    """
    Get QR code image.
    """
    qr_code = db.query(models.QRCode).filter(
        models.QRCode.code == code,
        models.QRCode.is_active == True
    ).first()
    
    if not qr_code:
        raise HTTPException(status_code=404, detail="QR code not found")
    
    # Check expiration
    if qr_code.expires_at and qr_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="QR code has expired")
    
    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/png")


@router.post("/verify/{code}")
def verify_qr_code(
    *,
    db: Session = Depends(deps.get_db),
    code: str,
    attendance_type: Optional[str] = "주일예배",
) -> Any:
    """
    Verify QR code and mark attendance.
    """
    qr_code = db.query(models.QRCode).filter(
        models.QRCode.code == code,
        models.QRCode.is_active == True
    ).first()
    
    if not qr_code:
        raise HTTPException(status_code=404, detail="Invalid QR code")
    
    # Check expiration
    if qr_code.expires_at and qr_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="QR code has expired")
    
    # Check if already marked attendance today
    today = datetime.utcnow().date()
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.member_id == qr_code.member_id,
        models.Attendance.attendance_date == today,
        models.Attendance.attendance_type == attendance_type
    ).first()
    
    if existing_attendance:
        return {
            "status": "already_marked",
            "message": "Attendance already marked for today",
            "member_id": qr_code.member_id,
            "attendance": existing_attendance
        }
    
    # Create attendance record
    attendance = models.Attendance(
        church_id=qr_code.church_id,
        member_id=qr_code.member_id,
        attendance_date=today,
        attendance_type=attendance_type,
        is_present=True
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    # Get member info
    member = crud.member.get(db=db, id=qr_code.member_id)
    
    return {
        "status": "success",
        "message": "Attendance marked successfully",
        "member": {
            "id": member.id,
            "name": member.name,
            "profile_photo_url": member.profile_photo_url
        },
        "attendance": attendance
    }


@router.get("/member/{member_id}", response_model=Optional[schemas.QRCode])
def get_member_qr_code(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get active QR code for a member.
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if member.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    qr_code = db.query(models.QRCode).filter(
        models.QRCode.member_id == member_id,
        models.QRCode.is_active == True
    ).first()
    
    return qr_code