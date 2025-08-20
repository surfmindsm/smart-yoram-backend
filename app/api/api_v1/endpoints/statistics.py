from typing import Any, List, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date

from app import models
from app.api import deps

router = APIRouter()


@router.get("/attendance/summary")
def get_attendance_summary(
    *,
    db: Session = Depends(deps.get_db),
    start_date: date = Query(None, description="Start date"),
    end_date: date = Query(None, description="End date"),
    attendance_type: str = Query("주일예배", description="Attendance type"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get attendance summary statistics.
    """
    # Default to last 3 months if no date range specified
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=90)

    # Get total members
    total_members = (
        db.query(func.count(models.Member.id))
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "active",
        )
        .scalar()
    )

    # Get attendance records
    attendance_query = (
        db.query(
            models.Attendance.service_date,
            func.count(models.Attendance.id).label("present_count"),
        )
        .filter(
            models.Attendance.church_id == current_user.church_id,
            models.Attendance.service_date >= start_date,
            models.Attendance.service_date <= end_date,
            models.Attendance.service_type == attendance_type,
            models.Attendance.present == True,
        )
        .group_by(models.Attendance.service_date)
        .all()
    )

    # Calculate statistics
    attendance_data = []
    total_attendance = 0

    for record in attendance_query:
        attendance_rate = (
            (record.present_count / total_members * 100) if total_members > 0 else 0
        )
        attendance_data.append(
            {
                "date": record.service_date.isoformat(),
                "present_count": record.present_count,
                "total_members": total_members,
                "attendance_rate": round(attendance_rate, 1),
            }
        )
        total_attendance += record.present_count

    # Calculate average attendance
    avg_attendance = total_attendance / len(attendance_data) if attendance_data else 0
    avg_attendance_rate = (
        (avg_attendance / total_members * 100) if total_members > 0 else 0
    )

    return {
        "summary": {
            "total_members": total_members,
            "average_attendance": round(avg_attendance, 1),
            "average_attendance_rate": round(avg_attendance_rate, 1),
            "period": {"start_date": start_date, "end_date": end_date},
        },
        "attendance_data": attendance_data,
    }


@router.get("/attendance/by-member")
def get_attendance_by_member(
    *,
    db: Session = Depends(deps.get_db),
    start_date: date = Query(None, description="Start date"),
    end_date: date = Query(None, description="End date"),
    attendance_type: str = Query("주일예배", description="Attendance type"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get attendance statistics by member.
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=90)

    # Get all members with their attendance counts
    attendance_stats = (
        db.query(
            models.Member.id,
            models.Member.name,
            models.Member.position,
            models.Member.district,
            func.count(models.Attendance.id).label("attendance_count"),
        )
        .outerjoin(
            models.Attendance,
            and_(
                models.Member.id == models.Attendance.member_id,
                models.Attendance.attendance_date >= start_date,
                models.Attendance.attendance_date <= end_date,
                models.Attendance.attendance_type == attendance_type,
                models.Attendance.is_present == True,
            ),
        )
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "active",
        )
        .group_by(
            models.Member.id,
            models.Member.name,
            models.Member.position,
            models.Member.district,
        )
        .all()
    )

    # Count total possible attendance days
    total_days = (
        db.query(func.count(func.distinct(models.Attendance.attendance_date)))
        .filter(
            models.Attendance.church_id == current_user.church_id,
            models.Attendance.attendance_date >= start_date,
            models.Attendance.attendance_date <= end_date,
            models.Attendance.attendance_type == attendance_type,
        )
        .scalar()
        or 1
    )

    # Format results
    member_attendance = []
    for stat in attendance_stats:
        attendance_rate = (
            (stat.attendance_count / total_days * 100) if total_days > 0 else 0
        )
        member_attendance.append(
            {
                "member_id": stat.id,
                "name": stat.name,
                "position": stat.position,
                "district": stat.district,
                "attendance_count": stat.attendance_count,
                "total_days": total_days,
                "attendance_rate": round(attendance_rate, 1),
            }
        )

    # Sort by attendance rate
    member_attendance.sort(key=lambda x: x["attendance_rate"], reverse=True)

    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
        },
        "member_attendance": member_attendance,
    }


@router.get("/members/demographics")
def get_member_demographics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get member demographics statistics.
    """
    # Gender distribution
    gender_stats = (
        db.query(models.Member.gender, func.count(models.Member.id).label("count"))
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "active",
        )
        .group_by(models.Member.gender)
        .all()
    )

    # Age distribution
    today = date.today()
    age_groups = {
        "0-9": 0,
        "10-19": 0,
        "20-29": 0,
        "30-39": 0,
        "40-49": 0,
        "50-59": 0,
        "60-69": 0,
        "70+": 0,
    }

    members_with_dob = (
        db.query(models.Member)
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "active",
            models.Member.birthdate.isnot(None),
        )
        .all()
    )

    for member in members_with_dob:
        age = today.year - member.birthdate.year
        if age < 10:
            age_groups["0-9"] += 1
        elif age < 20:
            age_groups["10-19"] += 1
        elif age < 30:
            age_groups["20-29"] += 1
        elif age < 40:
            age_groups["30-39"] += 1
        elif age < 50:
            age_groups["40-49"] += 1
        elif age < 60:
            age_groups["50-59"] += 1
        elif age < 70:
            age_groups["60-69"] += 1
        else:
            age_groups["70+"] += 1

    # Position distribution
    position_stats = (
        db.query(models.Member.position, func.count(models.Member.id).label("count"))
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "active",
            models.Member.position.isnot(None),
        )
        .group_by(models.Member.position)
        .all()
    )

    # District distribution
    district_stats = (
        db.query(models.Member.district, func.count(models.Member.id).label("count"))
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "active",
            models.Member.district.isnot(None),
        )
        .group_by(models.Member.district)
        .all()
    )

    return {
        "gender_distribution": [
            {"gender": stat.gender, "count": stat.count} for stat in gender_stats
        ],
        "age_distribution": [
            {"age_group": k, "count": v} for k, v in age_groups.items()
        ],
        "position_distribution": [
            {"position": stat.position, "count": stat.count} for stat in position_stats
        ],
        "district_distribution": [
            {"district": stat.district, "count": stat.count} for stat in district_stats
        ],
    }


@router.get("/members/growth")
def get_member_growth(
    *,
    db: Session = Depends(deps.get_db),
    months: int = Query(12, description="Number of months to show"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get member growth statistics over time.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=30 * months)

    # Get new member registrations by month
    new_members = (
        db.query(
            func.date_trunc("month", models.Member.registration_date).label("month"),
            func.count(models.Member.id).label("new_members"),
        )
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.registration_date >= start_date,
        )
        .group_by("month")
        .all()
    )

    # Get transfers out by month
    transfers_out = (
        db.query(
            func.date_trunc("month", models.Member.updated_at).label("month"),
            func.count(models.Member.id).label("transfers"),
        )
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "transferred",
            models.Member.updated_at >= start_date,
        )
        .group_by("month")
        .all()
    )

    # Combine data
    growth_data = {}

    for record in new_members:
        month_key = record.month.strftime("%Y-%m")
        growth_data[month_key] = {
            "month": month_key,
            "new_members": record.new_members,
            "transfers_out": 0,
        }

    for record in transfers_out:
        month_key = record.month.strftime("%Y-%m")
        if month_key in growth_data:
            growth_data[month_key]["transfers_out"] = record.transfers
        else:
            growth_data[month_key] = {
                "month": month_key,
                "new_members": 0,
                "transfers_out": record.transfers,
            }

    # Calculate net growth and total members
    total_members = (
        db.query(func.count(models.Member.id))
        .filter(
            models.Member.church_id == current_user.church_id,
            models.Member.member_status == "active",
            models.Member.registration_date < start_date,
        )
        .scalar()
        or 0
    )

    growth_list = []
    for month_key in sorted(growth_data.keys()):
        data = growth_data[month_key]
        net_growth = data["new_members"] - data["transfers_out"]
        total_members += net_growth

        growth_list.append(
            {
                "month": data["month"],
                "new_members": data["new_members"],
                "transfers_out": data["transfers_out"],
                "net_growth": net_growth,
                "total_members": total_members,
            }
        )

    return {
        "period": {"start_date": start_date, "end_date": end_date, "months": months},
        "growth_data": growth_list,
        "summary": {
            "total_new_members": sum(d["new_members"] for d in growth_list),
            "total_transfers_out": sum(d["transfers_out"] for d in growth_list),
            "net_growth": sum(d["net_growth"] for d in growth_list),
            "current_total_members": total_members,
        },
    }
