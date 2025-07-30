from typing import Any, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Attendance])
def read_attendances(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    service_date: date = Query(None),
    service_type: str = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    query = db.query(models.Attendance)

    if current_user.church_id:
        query = query.filter(models.Attendance.church_id == current_user.church_id)
    elif not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if service_date:
        query = query.filter(models.Attendance.service_date == service_date)
    if service_type:
        query = query.filter(models.Attendance.service_type == service_type)

    attendances = query.offset(skip).limit(limit).all()
    return attendances


@router.post("/", response_model=schemas.Attendance)
def create_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendance_in: schemas.AttendanceCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if (
        not current_user.is_superuser
        and current_user.church_id != attendance_in.church_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if member belongs to the church
    member = (
        db.query(models.Member)
        .filter(
            models.Member.id == attendance_in.member_id,
            models.Member.church_id == attendance_in.church_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in this church")

    # Check for duplicate attendance
    existing = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.member_id == attendance_in.member_id,
            models.Attendance.service_date == attendance_in.service_date,
            models.Attendance.service_type == attendance_in.service_type,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded")

    attendance = models.Attendance(**attendance_in.dict(), created_by=current_user.id)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.post("/bulk", response_model=List[schemas.Attendance])
def create_bulk_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendances_in: List[schemas.AttendanceCreate],
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    created_attendances = []

    for attendance_in in attendances_in:
        if (
            not current_user.is_superuser
            and current_user.church_id != attendance_in.church_id
        ):
            continue

        # Check if member belongs to the church
        member = (
            db.query(models.Member)
            .filter(
                models.Member.id == attendance_in.member_id,
                models.Member.church_id == attendance_in.church_id,
            )
            .first()
        )
        if not member:
            continue

        # Skip if already exists
        existing = (
            db.query(models.Attendance)
            .filter(
                models.Attendance.member_id == attendance_in.member_id,
                models.Attendance.service_date == attendance_in.service_date,
                models.Attendance.service_type == attendance_in.service_type,
            )
            .first()
        )
        if existing:
            continue

        attendance = models.Attendance(
            **attendance_in.dict(), created_by=current_user.id
        )
        db.add(attendance)
        created_attendances.append(attendance)

    db.commit()
    for attendance in created_attendances:
        db.refresh(attendance)

    return created_attendances


@router.get("/{attendance_id}", response_model=schemas.Attendance)
def read_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendance_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    attendance = (
        db.query(models.Attendance)
        .filter(models.Attendance.id == attendance_id)
        .first()
    )
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    if not current_user.is_superuser and attendance.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return attendance


@router.put("/{attendance_id}", response_model=schemas.Attendance)
def update_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendance_id: int,
    attendance_in: schemas.AttendanceUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    attendance = (
        db.query(models.Attendance)
        .filter(models.Attendance.id == attendance_id)
        .first()
    )
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    if not current_user.is_superuser and attendance.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = attendance_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.delete("/{attendance_id}")
def delete_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendance_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    attendance = (
        db.query(models.Attendance)
        .filter(models.Attendance.id == attendance_id)
        .first()
    )
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")

    if not current_user.is_superuser and attendance.church_id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(attendance)
    db.commit()
    return {"message": "Attendance deleted successfully"}
