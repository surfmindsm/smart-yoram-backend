from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import qrcode
import io
import base64
from datetime import datetime

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/{member_id}/card")
def get_member_card_data(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get member card data for mobile display.
    """
    member = (
        db.query(models.Member)
        .filter(
            models.Member.id == member_id,
            models.Member.church_id == current_user.church_id,
        )
        .first()
    )

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Get church info
    church = (
        db.query(models.Church)
        .filter(models.Church.id == current_user.church_id)
        .first()
    )

    # Get or create QR code
    qr_code = (
        db.query(models.QRCode)
        .filter(
            models.QRCode.member_id == member_id,
            models.QRCode.is_active == True,
            models.QRCode.qr_type == "member_card",
        )
        .first()
    )

    if not qr_code:
        # Create new QR code for member card
        import uuid

        unique_code = f"card:{member.church_id}:{member_id}:{uuid.uuid4().hex[:8]}"

        qr_code = models.QRCode(
            church_id=member.church_id,
            member_id=member_id,
            code=unique_code,
            qr_type="member_card",
            is_active=True,
        )
        db.add(qr_code)
        db.commit()
        db.refresh(qr_code)

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(qr_code.code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    qr_code_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()

    # Calculate age if birth date exists
    age = None
    if member.birthdate:
        today = datetime.now().date()
        age = today.year - member.birthdate.year
        if today < member.birthdate.replace(year=today.year):
            age -= 1

    # Get recent attendance count (last 30 days)
    from datetime import timedelta

    thirty_days_ago = datetime.now().date() - timedelta(days=30)

    recent_attendance_count = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.member_id == member_id,
            models.Attendance.service_date >= thirty_days_ago,
            models.Attendance.present == True,
        )
        .count()
    )

    return {
        "member": {
            "id": member.id,
            "name": member.name,
            "profile_photo_url": member.profile_photo_url,
            "phone_number": member.phone,
            "position": member.position,
            "district": member.district,
            "registration_date": member.registration_date,
            "age": age,
            "member_status": member.member_status,
        },
        "church": {
            "name": church.name if church else "교회",
            "address": church.address if church else "",
            "phone": church.phone if church else "",
        },
        "qr_code": {"code": qr_code.code, "image_base64": qr_code_base64},
        "statistics": {
            "recent_attendance_count": recent_attendance_count,
            "member_since": member.registration_date.strftime("%Y년 %m월")
            if member.registration_date
            else "",
        },
    }


@router.get("/{member_id}/card/html", response_class=HTMLResponse)
def get_member_card_html(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get member card as HTML for mobile display.
    """
    card_data = get_member_card_data(
        db=db, member_id=member_id, current_user=current_user
    )

    member = card_data["member"]
    church = card_data["church"]
    qr_code = card_data["qr_code"]
    stats = card_data["statistics"]

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{member['name']} - 교인증</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Malgun Gothic', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            
            .member-card {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
                width: 100%;
                max-width: 400px;
                position: relative;
            }}
            
            .card-header {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 25px 20px;
                text-align: center;
                position: relative;
            }}
            
            .card-header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                opacity: 0.3;
            }}
            
            .church-name {{
                font-size: 16px;
                font-weight: 300;
                margin-bottom: 5px;
                position: relative;
                z-index: 1;
            }}
            
            .card-title {{
                font-size: 22px;
                font-weight: bold;
                position: relative;
                z-index: 1;
            }}
            
            .card-body {{
                padding: 30px 20px;
            }}
            
            .profile-section {{
                text-align: center;
                margin-bottom: 25px;
            }}
            
            .profile-photo {{
                width: 100px;
                height: 100px;
                border-radius: 50%;
                border: 4px solid #f0f0f0;
                margin: 0 auto 15px;
                object-fit: cover;
                background: #f8f9fa;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 40px;
                color: #6c757d;
            }}
            
            .member-name {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            
            .member-position {{
                color: #7f8c8d;
                font-size: 14px;
                margin-bottom: 10px;
            }}
            
            .member-info {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 25px;
            }}
            
            .info-item {{
                text-align: center;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
            }}
            
            .info-label {{
                font-size: 12px;
                color: #6c757d;
                margin-bottom: 5px;
            }}
            
            .info-value {{
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }}
            
            .qr-section {{
                text-align: center;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                margin-top: 20px;
            }}
            
            .qr-code {{
                width: 120px;
                height: 120px;
                margin: 0 auto 10px;
                border-radius: 10px;
                overflow: hidden;
                background: white;
                padding: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .qr-code img {{
                width: 100%;
                height: 100%;
            }}
            
            .qr-label {{
                font-size: 12px;
                color: #6c757d;
            }}
            
            .card-footer {{
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                color: #6c757d;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="member-card">
            <div class="card-header">
                <div class="church-name">{church['name']}</div>
                <div class="card-title">교인증</div>
            </div>
            
            <div class="card-body">
                <div class="profile-section">
                    <div class="profile-photo">
                        {'<img src="' + member.get('profile_photo_url', '') + '" alt="프로필 사진">' if member.get('profile_photo_url') else '👤'}
                    </div>
                    <div class="member-name">{member['name']}</div>
                    <div class="member-position">{member.get('position', '') or ''} {member.get('district', '') or ''}</div>
                </div>
                
                <div class="member-info">
                    <div class="info-item">
                        <div class="info-label">연령</div>
                        <div class="info-value">{member.get('age', '미상') if member.get('age') else '미상'}세</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">등록일</div>
                        <div class="info-value">{stats.get('member_since', '미상')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">최근 출석</div>
                        <div class="info-value">{stats.get('recent_attendance_count', 0)}회</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">상태</div>
                        <div class="info-value">{'활동' if member.get('member_status') == 'active' else '비활동'}</div>
                    </div>
                </div>
                
                <div class="qr-section">
                    <div class="qr-code">
                        <img src="data:image/png;base64,{qr_code['image_base64']}" alt="QR 코드">
                    </div>
                    <div class="qr-label">출석체크용 QR 코드</div>
                </div>
            </div>
            
            <div class="card-footer">
                발급일: {datetime.now().strftime('%Y년 %m월 %d일')}
            </div>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@router.post("/{member_id}/card/regenerate-qr")
def regenerate_member_card_qr(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Regenerate QR code for member card.
    """
    member = (
        db.query(models.Member)
        .filter(
            models.Member.id == member_id,
            models.Member.church_id == current_user.church_id,
        )
        .first()
    )

    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Deactivate existing QR codes
    existing_codes = (
        db.query(models.QRCode)
        .filter(
            models.QRCode.member_id == member_id,
            models.QRCode.qr_type == "member_card",
            models.QRCode.is_active == True,
        )
        .all()
    )

    for code in existing_codes:
        code.is_active = False

    # Create new QR code
    import uuid

    unique_code = f"card:{member.church_id}:{member_id}:{uuid.uuid4().hex[:8]}"

    new_qr_code = models.QRCode(
        church_id=member.church_id,
        member_id=member_id,
        code=unique_code,
        qr_type="member_card",
        is_active=True,
    )
    db.add(new_qr_code)
    db.commit()
    db.refresh(new_qr_code)

    return {
        "message": "QR code regenerated successfully",
        "qr_code": {"id": new_qr_code.id, "code": new_qr_code.code},
    }
