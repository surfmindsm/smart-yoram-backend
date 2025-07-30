from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.post("/members/upload")
async def upload_members_excel(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    file: UploadFile = File(...)
) -> Any:
    """
    Upload members from Excel file.
    Expected columns: 이름, 성별, 생년월일, 전화번호, 주소, 직분, 구역
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Read Excel file
        df = pd.read_excel(io.BytesIO(await file.read()))
        
        # Validate required columns
        required_columns = ['이름', '성별', '전화번호']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Process each row
        created_count = 0
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if member exists by phone number
                existing_member = db.query(models.Member).filter(
                    models.Member.church_id == current_user.church_id,
                    models.Member.phone_number == str(row.get('전화번호', '')).strip()
                ).first()
                
                member_data = {
                    'name': str(row.get('이름', '')).strip(),
                    'gender': str(row.get('성별', '')).strip(),
                    'phone_number': str(row.get('전화번호', '')).strip(),
                    'church_id': current_user.church_id
                }
                
                # Optional fields
                if pd.notna(row.get('생년월일')):
                    try:
                        member_data['date_of_birth'] = pd.to_datetime(row['생년월일']).date()
                    except:
                        pass
                
                if pd.notna(row.get('주소')):
                    member_data['address'] = str(row['주소']).strip()
                
                if pd.notna(row.get('직분')):
                    member_data['position'] = str(row['직분']).strip()
                
                if pd.notna(row.get('구역')):
                    member_data['district'] = str(row['구역']).strip()
                
                if existing_member:
                    # Update existing member
                    for key, value in member_data.items():
                        if key != 'church_id':
                            setattr(existing_member, key, value)
                    updated_count += 1
                else:
                    # Create new member
                    new_member = models.Member(**member_data)
                    db.add(new_member)
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "message": "Excel upload completed",
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@router.get("/members/download")
def download_members_excel(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download all members as Excel file.
    """
    # Get all members for the church
    members = db.query(models.Member).filter(
        models.Member.church_id == current_user.church_id
    ).all()
    
    # Convert to DataFrame
    data = []
    for member in members:
        data.append({
            '이름': member.name,
            '성별': member.gender,
            '생년월일': member.date_of_birth,
            '전화번호': member.phone_number,
            '주소': member.address or '',
            '직분': member.position or '',
            '구역': member.district or '',
            '등록일': member.registration_date,
            '상태': member.member_status or 'active'
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='교인명단', index=False)
    
    output.seek(0)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"members_{current_user.church_id}_{timestamp}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/members/template")
def download_member_template(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download Excel template for member upload.
    """
    # Create template DataFrame
    template_data = {
        '이름': ['홍길동', '김철수'],
        '성별': ['남', '여'],
        '생년월일': ['1990-01-01', '1985-05-15'],
        '전화번호': ['010-1234-5678', '010-9876-5432'],
        '주소': ['서울시 강남구', '서울시 서초구'],
        '직분': ['집사', '권사'],
        '구역': ['1구역', '2구역']
    }
    
    df = pd.DataFrame(template_data)
    
    # Create Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='교인명단', index=False)
        
        # Add instructions sheet
        instructions = pd.DataFrame({
            '필드명': ['이름', '성별', '생년월일', '전화번호', '주소', '직분', '구역'],
            '필수여부': ['필수', '필수', '선택', '필수', '선택', '선택', '선택'],
            '설명': [
                '교인 이름',
                '남/여',
                'YYYY-MM-DD 형식',
                '010-0000-0000 형식',
                '주소',
                '직분 (집사, 권사, 장로 등)',
                '소속 구역'
            ]
        })
        instructions.to_excel(writer, sheet_name='설명', index=False)
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": "attachment; filename=member_upload_template.xlsx"}
    )


@router.get("/attendance/download")
def download_attendance_excel(
    *,
    db: Session = Depends(deps.get_db),
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download attendance records as Excel file.
    """
    query = db.query(models.Attendance).filter(
        models.Attendance.church_id == current_user.church_id
    )
    
    if start_date:
        query = query.filter(models.Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(models.Attendance.attendance_date <= end_date)
    
    attendances = query.all()
    
    # Get member names
    member_ids = [att.member_id for att in attendances]
    members = db.query(models.Member).filter(models.Member.id.in_(member_ids)).all()
    member_dict = {m.id: m.name for m in members}
    
    # Convert to DataFrame
    data = []
    for att in attendances:
        data.append({
            '날짜': att.attendance_date,
            '이름': member_dict.get(att.member_id, ''),
            '예배구분': att.attendance_type,
            '출석여부': '출석' if att.is_present else '결석',
            '비고': att.notes or ''
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='출석기록', index=False)
    
    output.seek(0)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"attendance_{current_user.church_id}_{timestamp}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )