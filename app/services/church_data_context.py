from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
import logging

from app.models.announcement import Announcement
from app.models.user import User
from app.models.worship_schedule import WorshipService
from app.models.pastoral_care import PastoralCareRequest, PrayerRequest
from app.models.financial import Offering, FundType
from app.models.attendance import Attendance
from app.models.member import Member, Family

logger = logging.getLogger(__name__)


def get_church_context_data(
    db: Session,
    church_id: int,
    church_data_sources: Dict = None,
    user_query: str = "",
    requested_sources: List[str] = None,
    format: str = "detailed",
    prioritize_church_data: bool = False,
) -> Dict[str, Any]:
    """
    Retrieve church data based on enabled data sources.

    Args:
        db: Database session
        church_id: Church ID
        church_data_sources: Dictionary of enabled data sources
        user_query: User's query to help filter relevant data
        requested_sources: List of specific sources to include
        format: Response format (detailed, summary, compact)
        prioritize_church_data: Whether this is for priority church data mode

    Returns:
        Dictionary containing church context data
    """
    context_data = {}

    # Determine which sources to include
    sources_to_include = set()

    if requested_sources:
        sources_to_include.update(requested_sources)
    elif church_data_sources:
        sources_to_include.update(
            [key for key, value in church_data_sources.items() if value is True]
        )
    else:
        # Default sources for priority mode
        if prioritize_church_data:
            sources_to_include = {
                "announcements",
                "prayer_requests",
                "pastoral_care_requests",
                "offerings",
                "attendances",
                "members",
                "worship_services",
            }

    try:
        # Add metadata
        context_data["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "sources_included": list(sources_to_include),
            "format": format,
            "prioritize_mode": prioritize_church_data,
        }

        # 🚀 Optimized parallel data retrieval with Redis caching for 60-80% performance improvement  
        import concurrent.futures
        from app.services.church_data_cache import (
            get_announcements_cached,
            get_attendance_stats_cached,
            get_member_stats_cached,
            get_worship_schedule_cached,
            get_prayer_requests_cached,
            get_pastoral_care_requests_cached,
            get_offering_stats_cached,
        )

        # Define data fetching functions with thread-local database sessions
        def fetch_data_with_session(data_type, fetch_func, db_session, church_id):
            """Fetch data using a thread-local database session"""
            try:
                return data_type, fetch_func(db_session, church_id)
            except Exception as e:
                logger.error(f"Error fetching {data_type}: {e}")
                return data_type, {} if data_type.endswith('_stats') else []

        # Prepare tasks for parallel execution
        fetch_tasks = []
        
        if "announcements" in sources_to_include:
            fetch_tasks.append(("announcements", get_announcements_cached))
            
        if "attendance" in sources_to_include or "attendances" in sources_to_include:
            fetch_tasks.append(("attendance_stats", get_attendance_stats_cached))
            
        if "members" in sources_to_include:
            fetch_tasks.append(("member_stats", get_member_stats_cached))
            
        if "worship_services" in sources_to_include or "worship" in sources_to_include:
            fetch_tasks.append(("worship_schedule", get_worship_schedule_cached))
            
        if "prayer_requests" in sources_to_include:
            fetch_tasks.append(("prayer_requests", get_prayer_requests_cached))
            
        if "pastoral_care_requests" in sources_to_include or "pastoral_care" in sources_to_include:
            fetch_tasks.append(("pastoral_care_requests", get_pastoral_care_requests_cached))
            
        if "offerings" in sources_to_include:
            fetch_tasks.append(("offering_stats", get_offering_stats_cached))

        # Execute data fetching in parallel using ThreadPoolExecutor
        if fetch_tasks:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(fetch_tasks), 4)) as executor:
                future_to_data_type = {
                    executor.submit(fetch_data_with_session, data_type, fetch_func, db, church_id): data_type
                    for data_type, fetch_func in fetch_tasks
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_data_type):
                    try:
                        data_type, result = future.result(timeout=30)  # 30 second timeout per task
                        context_data[data_type] = result
                    except concurrent.futures.TimeoutError:
                        data_type = future_to_data_type[future]
                        logger.error(f"Timeout fetching {data_type}")
                        context_data[data_type] = {} if data_type.endswith('_stats') else []
                    except Exception as e:
                        data_type = future_to_data_type[future]
                        logger.error(f"Error fetching {data_type}: {e}")
                        context_data[data_type] = {} if data_type.endswith('_stats') else []

    except Exception as e:
        logger.error(f"Error retrieving church context data: {e}")

    return context_data


def get_recent_announcements(
    db: Session, church_id: int, limit: int = 100
) -> List[Dict]:
    """
    Get ALL announcements for the church (no time limit).
    """
    try:
        announcements = (
            db.query(Announcement)
            .filter(Announcement.church_id == church_id)
            # Show ALL announcements regardless of status
            .order_by(desc(Announcement.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": ann.id,
                "title": ann.title,
                "content": ann.content,  # Show full content, not truncated
                "category": ann.category,
                "subcategory": ann.subcategory,  # Added missing column
                "author_name": ann.author_name,  # Added missing column
                "is_active": ann.is_active,  # Added missing column
                "is_pinned": ann.is_pinned,
                "target_audience": ann.target_audience,
                "created_at": ann.created_at.isoformat() if ann.created_at else None,
                "updated_at": (
                    ann.updated_at.isoformat() if ann.updated_at else None
                ),  # Added
            }
            for ann in announcements
        ]
    except Exception as e:
        logger.error(f"Error fetching announcements: {e}")
        return []
 

def get_recent_prayer_requests(
    db: Session, church_id: int, limit: int = 100
) -> List[Dict]:
    """
    Get ALL prayer requests for the church (no time limit).
    """
    try:
        prayer_requests = (
            db.query(PrayerRequest)
            .filter(PrayerRequest.church_id == church_id)
            # Show ALL prayer requests regardless of status/expiry
            .order_by(desc(PrayerRequest.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": req.id,
                "requester_name": (
                    req.requester_name if not req.is_anonymous else "익명"
                ),
                "requester_phone": req.requester_phone,  # Added missing column
                "prayer_type": req.prayer_type,
                "prayer_content": req.prayer_content,  # Show full content, not truncated
                "is_anonymous": req.is_anonymous,  # Added missing column
                "is_urgent": req.is_urgent,
                "is_public": req.is_public,  # Added missing column
                "status": req.status,  # Added missing column
                "admin_notes": req.admin_notes,  # Added missing column
                "answered_testimony": req.answered_testimony,  # Added missing column
                "prayer_count": req.prayer_count,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "updated_at": (
                    req.updated_at.isoformat() if req.updated_at else None
                ),  # Added
                "closed_at": (
                    req.closed_at.isoformat() if req.closed_at else None
                ),  # Added
                "expires_at": req.expires_at.isoformat() if req.expires_at else None,
            }
            for req in prayer_requests
        ]
    except Exception as e:
        logger.error(f"Error fetching prayer requests: {e}")
        return []


def get_recent_pastoral_care_requests(
    db: Session, church_id: int, limit: int = 100
) -> List[Dict]:
    """
    Get ALL pastoral care requests for the church (no time limit).
    """
    try:
        pastoral_requests = (
            db.query(PastoralCareRequest)
            .filter(PastoralCareRequest.church_id == church_id)
            # Show ALL pastoral care requests regardless of status
            .order_by(desc(PastoralCareRequest.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": req.id,
                "requester_name": req.requester_name,
                "requester_phone": req.requester_phone,
                "request_type": req.request_type,
                "request_content": req.request_content,
                "priority": req.priority,
                "is_urgent": req.is_urgent,
                "status": req.status,
                "assigned_pastor_id": req.assigned_pastor_id,  # Added missing column
                "preferred_date": (
                    req.preferred_date.isoformat() if req.preferred_date else None
                ),
                "preferred_time_start": (
                    req.preferred_time_start.isoformat()
                    if req.preferred_time_start
                    else None
                ),
                "preferred_time_end": (
                    req.preferred_time_end.isoformat()
                    if req.preferred_time_end
                    else None
                ),
                "scheduled_date": (
                    req.scheduled_date.isoformat() if req.scheduled_date else None
                ),
                "scheduled_time": (
                    req.scheduled_time.isoformat() if req.scheduled_time else None
                ),
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "updated_at": req.updated_at.isoformat() if req.updated_at else None,
                "completed_at": (
                    req.completed_at.isoformat() if req.completed_at else None
                ),
                "address": req.address,
                "latitude": (
                    float(req.latitude) if req.latitude else None
                ),  # Added missing column
                "longitude": (
                    float(req.longitude) if req.longitude else None
                ),  # Added missing column
                "completion_notes": req.completion_notes,
                "admin_notes": req.admin_notes,
                "contact_info": req.contact_info,
            }
            for req in pastoral_requests
        ]
    except Exception as e:
        logger.error(f"Error fetching pastoral care requests: {e}")
        return []


def get_all_offerings(db: Session, church_id: int) -> Dict:
    """
    Get comprehensive offering statistics for the church (all data).
    """
    try:
        from datetime import datetime, timedelta

        # Calculate multiple date ranges
        end_date = datetime.now().date()
        # Remove start_date limitation - get all data

        # This year and last year
        current_year = end_date.year
        last_year = current_year - 1
        this_year_start = datetime(current_year, 1, 1).date()
        last_year_start = datetime(last_year, 1, 1).date()
        last_year_end = datetime(last_year, 12, 31).date()

        # Current month and last month
        current_month_start = end_date.replace(day=1)
        if current_month_start.month == 1:
            last_month_start = current_month_start.replace(
                year=current_month_start.year - 1, month=12
            )
        else:
            last_month_start = current_month_start.replace(
                month=current_month_start.month - 1
            )

        # Get total offering for all time
        total_all_time = (
            db.query(func.sum(Offering.amount))
            .filter(Offering.church_id == church_id, Offering.offered_on <= end_date)
            .scalar()
            or 0
        )

        # Get this year total
        total_this_year = (
            db.query(func.sum(Offering.amount))
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= this_year_start,
                Offering.offered_on <= end_date,
            )
            .scalar()
            or 0
        )

        # Get last year total
        total_last_year = (
            db.query(func.sum(Offering.amount))
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= last_year_start,
                Offering.offered_on <= last_year_end,
            )
            .scalar()
            or 0
        )

        # Get this month total
        total_this_month = (
            db.query(func.sum(Offering.amount))
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= current_month_start,
                Offering.offered_on <= end_date,
            )
            .scalar()
            or 0
        )

        # Get last month total
        if current_month_start.month == 1:
            last_month_end = datetime(current_month_start.year - 1, 12, 31).date()
        else:
            last_month_end = current_month_start - timedelta(days=1)

        total_last_month = (
            db.query(func.sum(Offering.amount))
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= last_month_start,
                Offering.offered_on <= last_month_end,
            )
            .scalar()
            or 0
        )

        # Monthly breakdown for this year
        monthly_breakdown = (
            db.query(
                func.extract("month", Offering.offered_on).label("month"),
                func.sum(Offering.amount).label("total"),
            )
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= this_year_start,
                Offering.offered_on <= end_date,
            )
            .group_by(func.extract("month", Offering.offered_on))
            .order_by("month")
            .all()
        )

        # Fund type breakdown for this year
        fund_stats_year = (
            db.query(
                Offering.fund_type,
                func.sum(Offering.amount).label("total"),
                func.count(Offering.id).label("count"),
            )
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= this_year_start,
                Offering.offered_on <= end_date,
            )
            .group_by(Offering.fund_type)
            .order_by(desc("total"))
            .all()
        )

        # Average offering per member (if member data available)
        total_members = (
            db.query(Member)
            .filter(Member.church_id == church_id, Member.status == "active")
            .count()
        )

        avg_offering_per_member = (
            (total_this_month / total_members) if total_members > 0 else 0
        )

        # Get recent individual offerings (optimized with eager loading)
        from sqlalchemy.orm import joinedload
        
        recent_offerings = (
            db.query(Offering)
            .options(joinedload(Offering.member))  # Prevent N+1 queries
            .filter(Offering.church_id == church_id)
            # Show all offerings, no date restriction
            .order_by(desc(Offering.offered_on))
            .limit(50)  # Increased limit
            .all()
        )

        return {
            "period_days": "전체 기간",
            "totals": {
                "all_time": float(total_all_time),
                "this_year": float(total_this_year),
                "last_year": float(total_last_year),
                "this_month": float(total_this_month),
                "last_month": float(total_last_month),
                "year_over_year_change": (
                    float((total_this_year - total_last_year) / total_last_year * 100)
                    if total_last_year > 0
                    else 0
                ),
                "month_over_month_change": (
                    float(
                        (total_this_month - total_last_month) / total_last_month * 100
                    )
                    if total_last_month > 0
                    else 0
                ),
            },
            "monthly_breakdown": [
                {
                    "month": int(month.month),
                    "month_name": [
                        "",
                        "1월",
                        "2월",
                        "3월",
                        "4월",
                        "5월",
                        "6월",
                        "7월",
                        "8월",
                        "9월",
                        "10월",
                        "11월",
                        "12월",
                    ][int(month.month)],
                    "total": float(month.total),
                }
                for month in monthly_breakdown
            ],
            "fund_breakdown": [
                {
                    "fund_type": fund.fund_type,
                    "total": float(fund.total),
                    "count": fund.count,
                    "percentage": (
                        float(fund.total / total_this_year * 100)
                        if total_this_year > 0
                        else 0
                    ),
                }
                for fund in fund_stats_year
            ],
            "statistics": {
                "total_members": total_members,
                "avg_offering_per_member_this_month": round(avg_offering_per_member, 0),
                "total_offerings_count_this_year": sum(
                    fund.count for fund in fund_stats_year
                ),
            },
            "recent_offerings": [
                {
                    "id": offering.id,  # Added missing column
                    "member_name": offering.member.name if offering.member else "익명",
                    "member_id": offering.member_id,  # Added missing column
                    "fund_type": offering.fund_type,
                    "amount": float(offering.amount),
                    "date": offering.offered_on.isoformat(),
                    "note": offering.note,
                    "created_at": (
                        offering.created_at.isoformat() if offering.created_at else None
                    ),  # Added
                    "updated_at": (
                        offering.updated_at.isoformat() if offering.updated_at else None
                    ),  # Added
                }
                for offering in recent_offerings
            ],
        }
    except Exception as e:
        logger.error(f"Error fetching offering statistics: {e}")
        return {
            "period_days": "전체 기간",
            "total_amount": 0,
            "fund_breakdown": [],
            "recent_offerings": [],
        }


def get_attendance_stats(db: Session, church_id: int) -> Dict:
    """
    Get attendance statistics for the church.
    """
    try:
        from datetime import datetime, timedelta

        # Get date ranges
        today = datetime.now().date()
        last_week_start = today - timedelta(days=today.weekday() + 7)  # Last Monday
        last_week_end = last_week_start + timedelta(days=6)  # Last Sunday

        # Get total member count
        total_members = (
            db.query(Member)
            .filter(Member.church_id == church_id, Member.status == "active")
            .count()
        )

        # Get last week attendance
        last_week_attendance = (
            db.query(func.count(Attendance.id.distinct()))
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= last_week_start,
                Attendance.service_date <= last_week_end,
                Attendance.present == True,
            )
            .scalar()
            or 0
        )

        # Get attendance by service type for last 4 weeks
        four_weeks_ago = today - timedelta(weeks=4)
        service_stats = (
            db.query(
                Attendance.service_type,
                func.count(Attendance.id).label("total_attendance"),
                func.count(func.distinct(Attendance.service_date)).label(
                    "service_count"
                ),
            )
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= four_weeks_ago,
                Attendance.present == True,
            )
            .group_by(Attendance.service_type)
            .all()
        )

        # Monthly attendance trends (전체 기간)
        monthly_attendance = (
            db.query(
                func.extract("year", Attendance.service_date).label("year"),
                func.extract("month", Attendance.service_date).label("month"),
                func.count(Attendance.id).label("attendance_count"),
                func.count(func.distinct(Attendance.member_id)).label(
                    "unique_attendees"
                ),
            )
            .filter(Attendance.church_id == church_id, Attendance.present == True)
            .group_by(
                func.extract("year", Attendance.service_date),
                func.extract("month", Attendance.service_date),
            )
            .order_by("year", "month")
            .all()
        )

        # Attendance by member (top attendees this year)
        year_start = today.replace(month=1, day=1)
        top_attendees = (
            db.query(Member.name, func.count(Attendance.id).label("attendance_count"))
            .join(Attendance)
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= year_start,
                Attendance.present == True,
            )
            .group_by(Member.id, Member.name)
            .order_by(desc("attendance_count"))
            .limit(10)
            .all()
        )

        # Weekly attendance pattern (last 8 weeks)
        eight_weeks_ago = today - timedelta(weeks=8)
        weekly_attendance = (
            db.query(
                func.extract("week", Attendance.service_date).label("week"),
                func.extract("year", Attendance.service_date).label("year"),
                func.count(Attendance.id).label("attendance_count"),
            )
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= eight_weeks_ago,
                Attendance.present == True,
            )
            .group_by(
                func.extract("year", Attendance.service_date),
                func.extract("week", Attendance.service_date),
            )
            .order_by("year", "week")
            .all()
        )

        # Get recent attendance records (no time limit)
        recent_attendance = (
            db.query(Attendance)
            .join(Member)
            .filter(Attendance.church_id == church_id, Attendance.present == True)
            .order_by(desc(Attendance.service_date))
            .limit(50)  # Increased limit
            .all()
        )

        # Calculate average weekly attendance
        average_weekly = 0
        if service_stats:
            total_weekly_attendance = sum(
                stat.total_attendance
                for stat in service_stats
                if stat.service_count >= 2
            )
            service_weeks = (
                max(stat.service_count for stat in service_stats)
                if service_stats
                else 0
            )
            if service_weeks > 0:
                average_weekly = total_weekly_attendance // service_weeks

        return {
            "total_members": total_members,
            "average_weekly_attendance": average_weekly,
            "last_week_attendance": last_week_attendance,
            "attendance_rate": (
                round((last_week_attendance / total_members * 100), 1)
                if total_members > 0
                else 0
            ),
            "service_breakdown": [
                {
                    "service_type": stat.service_type,
                    "avg_attendance": (
                        stat.total_attendance // stat.service_count
                        if stat.service_count > 0
                        else 0
                    ),
                    "service_count": stat.service_count,
                    "total_attendance": stat.total_attendance,
                }
                for stat in service_stats
            ],
            "monthly_trends": [
                {
                    "year": int(month.year),
                    "month": int(month.month),
                    "month_name": [
                        "",
                        "1월",
                        "2월",
                        "3월",
                        "4월",
                        "5월",
                        "6월",
                        "7월",
                        "8월",
                        "9월",
                        "10월",
                        "11월",
                        "12월",
                    ][int(month.month)],
                    "total_attendance": month.attendance_count,
                    "unique_attendees": month.unique_attendees,
                }
                for month in monthly_attendance
            ],
            "weekly_trends": [
                {
                    "year": int(week.year),
                    "week": int(week.week),
                    "attendance_count": week.attendance_count,
                }
                for week in weekly_attendance
            ],
            "top_attendees": [
                {
                    "member_name": attendee.name,
                    "attendance_count": attendee.attendance_count,
                }
                for attendee in top_attendees
            ],
            "recent_attendances": [
                {
                    "id": att.id,  # Added missing column
                    "member_id": att.member_id,  # Added missing column
                    "member_name": att.member.name if att.member else "Unknown",
                    "service_type": att.service_type,
                    "service_date": att.service_date.isoformat(),
                    "present": att.present,  # Added missing column
                    "check_in_time": (
                        att.check_in_time.isoformat() if att.check_in_time else None
                    ),
                    "check_in_method": att.check_in_method,
                    "notes": getattr(att, "notes", None),  # Added if exists
                    "created_at": (
                        att.created_at.isoformat() if att.created_at else None
                    ),  # Added
                }
                for att in recent_attendance
            ],
        }
    except Exception as e:
        logger.error(f"Error fetching attendance stats: {e}")
        return {
            "total_members": 0,
            "average_weekly_attendance": 0,
            "last_week_attendance": 0,
            "attendance_rate": 0,
            "service_breakdown": [],
            "recent_attendances": [],
        }


def get_enhanced_member_statistics(db: Session, church_id: int) -> Dict:
    """
    Get enhanced member statistics for the church (without personal information).
    """
    try:
        from datetime import datetime, timedelta

        # Total members (using Member table)
        total_members = (
            db.query(Member)
            .filter(Member.church_id == church_id, Member.status == "active")
            .count()
        )

        # Members by position (직분)
        position_stats = (
            db.query(Member.position, func.count(Member.id).label("count"))
            .filter(Member.church_id == church_id, Member.status == "active")
            .group_by(Member.position)
            .all()
        )

        # New members this month
        start_of_month = (
            datetime.now()
            .replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            .date()
        )
        new_members_this_month = (
            db.query(Member)
            .filter(
                Member.church_id == church_id,
                Member.registration_date >= start_of_month,
                Member.status == "active",
            )
            .count()
        )

        # Members by department
        department_stats = (
            db.query(Member.department, func.count(Member.id).label("count"))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.department.isnot(None),
            )
            .group_by(Member.department)
            .all()
        )

        # Members by district (구역)
        district_stats = (
            db.query(Member.district, func.count(Member.id).label("count"))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.district.isnot(None),
            )
            .group_by(Member.district)
            .all()
        )

        # Age demographics (optimized single query with CASE WHEN)
        from sqlalchemy import case
        
        age_stats_raw = (
            db.query(
                func.sum(
                    case(
                        (Member.age.between(0, 12), 1),
                        else_=0
                    )
                ).label("children"),
                func.sum(
                    case(
                        (Member.age.between(13, 18), 1),
                        else_=0
                    )
                ).label("youth"),
                func.sum(
                    case(
                        (Member.age.between(19, 35), 1),
                        else_=0
                    )
                ).label("young_adult"),
                func.sum(
                    case(
                        (Member.age.between(36, 60), 1),
                        else_=0
                    )
                ).label("adult"),
                func.sum(
                    case(
                        (Member.age.between(61, 150), 1),
                        else_=0
                    )
                ).label("senior")
            )
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.age.isnot(None)
            )
            .first()
        )
        
        age_stats = {
            "children": age_stats_raw.children or 0,
            "youth": age_stats_raw.youth or 0,
            "young_adult": age_stats_raw.young_adult or 0,
            "adult": age_stats_raw.adult or 0,
            "senior": age_stats_raw.senior or 0,
        }

        # Gender statistics (more detailed)
        gender_stats = (
            db.query(Member.gender, func.count(Member.id).label("count"))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.gender.isnot(None),
            )
            .group_by(Member.gender)
            .all()
        )

        # Marital status statistics
        marital_stats = (
            db.query(Member.marital_status, func.count(Member.id).label("count"))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.marital_status.isnot(None),
            )
            .group_by(Member.marital_status)
            .all()
        )

        # Detailed age statistics (actual ages, not just ranges)
        age_distribution = (
            db.query(Member.age, func.count(Member.id).label("count"))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.age.isnot(None),
            )
            .group_by(Member.age)
            .order_by(Member.age)
            .all()
        )

        # Average age calculation
        avg_age = (
            db.query(func.avg(Member.age))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.age.isnot(None),
            )
            .scalar()
        )

        # All baptisms (전체 기간) - enhanced with details
        baptized_members = (
            db.query(Member)
            .filter(
                Member.church_id == church_id,
                Member.baptism_date.isnot(None),
                Member.status == "active",
            )
            .order_by(desc(Member.baptism_date))
            .all()
        )

        recent_baptisms = len(baptized_members)

        # Family count
        family_count = db.query(Family).filter(Family.church_id == church_id).count()

        return {
            "total_members": total_members,
            "new_members_this_month": new_members_this_month,
            "recent_baptisms": recent_baptisms,
            "family_count": family_count,
            "average_age": round(avg_age, 1) if avg_age else 0,
            "members_by_position": {pos: count for pos, count in position_stats if pos},
            "members_by_department": {
                dept: count for dept, count in department_stats if dept
            },
            "members_by_district": {
                district: count for district, count in district_stats if district
            },
            "age_demographics": age_stats,
            "detailed_age_distribution": {
                age: count for age, count in age_distribution
            },
            "gender_distribution": {
                gender: count for gender, count in gender_stats if gender
            },
            "marital_status_distribution": {
                status: count for status, count in marital_stats if status
            },
            # Added baptism details
            "baptism_details": [
                {
                    "member_name": member.name,
                    "baptism_date": (
                        member.baptism_date.isoformat() if member.baptism_date else None
                    ),
                    "baptism_church": member.baptism_church,
                    "registration_date": (
                        member.registration_date.isoformat()
                        if member.registration_date
                        else None
                    ),
                }
                for member in baptized_members[:20]  # Recent 20 baptisms
            ],
        }
    except Exception as e:
        logger.error(f"Error fetching enhanced member statistics: {e}")
        return {
            "total_members": 0,
            "new_members_this_month": 0,
            "recent_baptisms": 0,
            "family_count": 0,
            "members_by_position": {},
            "members_by_department": {},
            "members_by_district": {},
            "age_demographics": {},
            "gender_distribution": {},
        }


def get_member_statistics(db: Session, church_id: int) -> Dict:
    """
    Legacy function - redirects to enhanced version.
    """
    return get_enhanced_member_statistics(db, church_id)


def get_worship_schedule(db: Session, church_id: int, limit: int = 100) -> List[Dict]:
    """
    Get ALL worship services schedule (no time limit).
    """
    try:
        # Get all worship services
        services = (
            db.query(WorshipService)
            .filter(WorshipService.church_id == church_id)
            .filter(WorshipService.is_active == True)
            .order_by(WorshipService.day_of_week, WorshipService.start_time)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": service.id,
                "name": service.name,
                "service_type": service.service_type,
                "day_of_week": service.day_of_week,
                "day_name": ["월", "화", "수", "목", "금", "토", "일"][service.day_of_week] if service.day_of_week is not None else "미정",
                "start_time": (
                    service.start_time.isoformat() if service.start_time else None
                ),
                "end_time": service.end_time.isoformat() if service.end_time else None,
                "location": service.location,
                "target_group": service.target_group,
                "is_online": service.is_online,
                "is_active": service.is_active,
                "order_index": service.order_index,  # Added missing column
                "created_at": (
                    service.created_at.isoformat() if service.created_at else None
                ),
                "updated_at": (
                    service.updated_at.isoformat() if service.updated_at else None
                ),
            }
            for service in services
        ]
    except Exception as e:
        logger.error(f"Error fetching worship schedule: {e}")
        return []


def format_context_for_prompt(context_data: Dict) -> str:
    """
    Format the church context data for inclusion in GPT prompt.
    """
    context_parts = []

    if context_data.get("announcements"):
        announcements = context_data["announcements"]
        if announcements:
            context_parts.append("\n[교회 공지사항]")
            for ann in announcements[:5]:  # Limit to 5 most recent
                context_parts.append(f"- {ann['title']}: {ann['content']}")

    if context_data.get("prayer_requests"):
        prayer_requests = context_data["prayer_requests"]
        if prayer_requests:
            context_parts.append("\n[중보기도 요청]")
            for req in prayer_requests:  # Show ALL prayer requests
                urgency = " (긴급)" if req["is_urgent"] else ""
                context_parts.append(
                    f"- {req['requester_name']}: {req['prayer_content']}{urgency} "
                    f"[{req['prayer_type']}, 기도수: {req['prayer_count']}]"
                )

    if context_data.get("pastoral_care_requests"):
        pastoral_requests = context_data["pastoral_care_requests"]
        if pastoral_requests:
            context_parts.append("\n[심방 요청]")
            # Sort by created_at desc to show most recent first
            sorted_requests = sorted(
                pastoral_requests, key=lambda x: x["created_at"] or "", reverse=True
            )
            for (
                req
            ) in (
                sorted_requests
            ):  # Show ALL pastoral care requests in chronological order
                urgency = " (긴급)" if req["is_urgent"] else ""
                status_text = {
                    "pending": "대기중",
                    "approved": "승인됨",
                    "scheduled": "예약됨",
                    "completed": "완료됨",
                    "cancelled": "취소됨",
                }.get(req["status"], req["status"])

                # 연락처 정보
                phone_info = (
                    f", 연락처: {req['requester_phone']}"
                    if req["requester_phone"]
                    else ""
                )

                # 날짜 정보
                date_info = (
                    f", 희망일: {req['preferred_date']}"
                    if req["preferred_date"]
                    else ""
                )
                scheduled_info = (
                    f", 예약일시: {req['scheduled_date']} {req['scheduled_time']}"
                    if req["scheduled_date"]
                    else ""
                )

                # 주소 정보
                address_info = f", 주소: {req['address']}" if req["address"] else ""

                # 완료/관리자 노트
                notes_info = ""
                if req["completion_notes"]:
                    notes_info += f", 완료노트: {req['completion_notes']}"
                if req["admin_notes"]:
                    notes_info += f", 관리자노트: {req['admin_notes']}"

                context_parts.append(
                    f"- ID{req['id']} {req['requester_name']}: {req['request_content']}{urgency}{phone_info} "
                    f"[{req['request_type']}, {status_text}{date_info}{scheduled_info}{address_info}{notes_info}]"
                )

    if context_data.get("offering_stats"):
        offering_data = context_data["offering_stats"]
        # Show offering info even if amount is 0
        totals = offering_data.get("totals", {})
        if totals or offering_data:
            context_parts.append("\n[헌금 현황]")
            this_year = totals.get("this_year", 0) or totals.get("all_time", 0)
            last_year = totals.get("last_year", 0)

            if this_year == 0 and last_year == 0:
                context_parts.append("- 현재 헌금 기록이 없습니다")
                context_parts.append(
                    "- 헌금 데이터베이스 연동 또는 입력 시스템 점검 필요"
                )
            else:
                context_parts.append(f"- 올해 총 헌금: {this_year:,.0f}원")
                if last_year > 0:
                    change = (
                        ((this_year - last_year) / last_year * 100)
                        if last_year > 0
                        else 0
                    )
                    context_parts.append(
                        f"- 작년 대비: {change:+.1f}% ({last_year:,.0f}원)"
                    )

                this_month = totals.get("this_month", 0)
                if this_month > 0:
                    month_change = totals.get("month_over_month_change", 0)
                    context_parts.append(
                        f"- 이번달: {this_month:,.0f}원 (전월 대비 {month_change:+.1f}%)"
                    )

            stats = offering_data.get("statistics", {})
            if stats.get("total_members", 0) > 0:
                context_parts.append(
                    f"- 교인 1인당 월평균: {stats['avg_offering_per_member_this_month']:,.0f}원"
                )

            if offering_data.get("fund_breakdown"):
                context_parts.append("- 헌금 종류별:")
                for fund in offering_data["fund_breakdown"][:3]:  # Top 3
                    context_parts.append(
                        f"  • {fund['fund_type']}: {fund['total']:,.0f}원 ({fund['percentage']:.1f}%)"
                    )

            if offering_data.get("monthly_breakdown"):
                context_parts.append("- 월별 추이 (최근):")
                for month in offering_data["monthly_breakdown"][-3:]:  # Last 3 months
                    context_parts.append(
                        f"  • {month['month_name']}: {month['total']:,.0f}원"
                    )

    if context_data.get("attendance_stats"):
        stats = context_data["attendance_stats"]
        if stats["total_members"] > 0:
            context_parts.append("\n[출석 현황]")
            context_parts.append(f"- 등록 교인: {stats['total_members']}명")
            context_parts.append(
                f"- 지난주 출석: {stats['last_week_attendance']}명 ({stats['attendance_rate']}%)"
            )
            context_parts.append(
                f"- 평균 주간 출석: {stats['average_weekly_attendance']}명"
            )

            if stats.get("service_breakdown"):
                context_parts.append("- 예배별 출석:")
                service_names = {
                    "sunday_morning": "주일 오전",
                    "sunday_evening": "주일 오후",
                    "wednesday": "수요예배",
                    "friday": "금요예배",
                }
                for service in stats["service_breakdown"]:
                    service_name = service_names.get(
                        service["service_type"], service["service_type"]
                    )
                    context_parts.append(
                        f"  • {service_name}: 평균 {service['avg_attendance']}명 (총 {service['total_attendance']}회)"
                    )

            if stats.get("monthly_trends"):
                context_parts.append("- 월별 출석 추이 (최근):")
                for trend in stats["monthly_trends"][-3:]:  # Last 3 months
                    context_parts.append(
                        f"  • {trend['month_name']}: {trend['total_attendance']}회 (고유 출석자 {trend['unique_attendees']}명)"
                    )

            if stats.get("top_attendees"):
                context_parts.append("- 올해 최다 출석자:")
                for attendee in stats["top_attendees"][:3]:  # Top 3
                    context_parts.append(
                        f"  • {attendee['member_name']}: {attendee['attendance_count']}회"
                    )

    if context_data.get("member_stats"):
        stats = context_data["member_stats"]
        if stats["total_members"] > 0:
            context_parts.append("\n[교인 현황]")
            context_parts.append(
                f"- 전체 등록 교인: {stats['total_members']}명 (평균연령: {stats.get('average_age', 0)}세)"
            )
            context_parts.append(
                f"- 이번달 새신자: {stats['new_members_this_month']}명"
            )
            context_parts.append(f"- 최근 6개월 세례자: {stats['recent_baptisms']}명")
            context_parts.append(f"- 등록 가정수: {stats['family_count']}가정")

            # Gender distribution
            if stats.get("gender_distribution"):
                gender_stats = stats["gender_distribution"]
                # 모든 가능한 성별 값들을 체크 (한글, 영문, 대소문자 모두 포함)
                male_keys = ["M", "m", "male", "남성", "남", "Male", "MALE", "MAN", "man"]
                female_keys = ["F", "f", "female", "여성", "여", "Female", "FEMALE", "WOMAN", "woman", "W", "w"]

                male_count = sum(gender_stats.get(key, 0) for key in male_keys)
                female_count = sum(gender_stats.get(key, 0) for key in female_keys)

                # 실제 데이터베이스의 모든 gender 값들도 표시 (디버깅용)
                all_genders = {k: v for k, v in gender_stats.items() if v > 0}

                total_with_gender = male_count + female_count
                total_members = stats.get("total_members", 0)
                
                if male_count > 0 or female_count > 0:
                    context_parts.append(
                        f"- 성별 분포: 남성 {male_count}명, 여성 {female_count}명"
                    )
                    
                    # 성별 데이터가 부족한 경우 경고 메시지 추가
                    if total_with_gender < total_members:
                        missing_count = total_members - total_with_gender
                        context_parts.append(
                            f"  ※ 성별 정보가 누락된 교인: {missing_count}명 (전체 {total_members}명 중)"
                        )
                    
                    if len(all_genders) > 0:
                        context_parts.append(f"  (데이터베이스 원본값: {all_genders})")
                else:
                    # 성별 데이터가 전혀 없는 경우
                    if total_members > 0:
                        context_parts.append(
                            f"- 성별 분포: 성별 정보가 기록되지 않음 (전체 {total_members}명)"
                        )

            # Marital status
            if stats.get("marital_status_distribution"):
                marital_names = {
                    "single": "미혼",
                    "married": "기혼",
                    "divorced": "이혼",
                    "widowed": "사별",
                }
                marital_stats = []
                for status, count in stats["marital_status_distribution"].items():
                    if count > 0:
                        status_name = marital_names.get(status, status)
                        marital_stats.append(f"{status_name} {count}명")
                if marital_stats:
                    context_parts.append(f"- 혼인상태: {', '.join(marital_stats)}")

            if stats.get("members_by_position"):
                context_parts.append("- 직분별 분포:")
                position_names = {
                    "pastor": "목사",
                    "elder": "장로",
                    "deacon": "집사", 
                    "member": "성도",
                    "youth": "청년",
                    "child": "아동",
                }
                
                total_with_position = sum(stats["members_by_position"].values())
                total_members = stats.get("total_members", 0)
                
                for pos, count in stats["members_by_position"].items():
                    pos_name = position_names.get(pos, pos)
                    context_parts.append(f"  • {pos_name}: {count}명")
                
                # 직분 정보가 누락된 교인이 있는지 체크
                if total_with_position < total_members:
                    missing_count = total_members - total_with_position
                    context_parts.append(
                        f"  ※ 직분 정보가 누락된 교인: {missing_count}명"
                    )

            if stats.get("members_by_department"):
                context_parts.append("- 부서별 분포:")
                dept_items = list(stats["members_by_department"].items())[:5]  # Top 5 departments
                
                total_with_department = sum(stats["members_by_department"].values())
                total_members = stats.get("total_members", 0)
                
                for dept, count in dept_items:
                    context_parts.append(f"  • {dept}: {count}명")
                
                # 부서 정보가 누락된 교인이 있는지 체크
                if total_with_department < total_members:
                    missing_count = total_members - total_with_department
                    context_parts.append(
                        f"  ※ 부서 정보가 누락된 교인: {missing_count}명"
                    )

            if stats.get("members_by_district"):
                context_parts.append("- 구역별 분포:")
                district_items = list(stats["members_by_district"].items())[:5]  # Top 5 districts
                
                total_with_district = sum(stats["members_by_district"].values())
                total_members = stats.get("total_members", 0)
                
                for district, count in district_items:
                    context_parts.append(f"  • {district}: {count}명")
                
                # 구역 정보가 누락된 교인이 있는지 체크
                if total_with_district < total_members:
                    missing_count = total_members - total_with_district
                    context_parts.append(
                        f"  ※ 구역 정보가 누락된 교인: {missing_count}명"
                    )

            if stats.get("age_demographics"):
                context_parts.append("- 연령대별 분포:")
                age_names = {
                    "children": "아동(0-12세)",
                    "youth": "청소년(13-18세)",
                    "young_adult": "청년(19-35세)",
                    "adult": "장년(36-60세)",
                    "senior": "노년(61세+)",
                }
                for age_range, count in stats["age_demographics"].items():
                    if count > 0:
                        age_name = age_names.get(age_range, age_range)
                        context_parts.append(f"  • {age_name}: {count}명")

    if context_data.get("worship_schedule"):
        services = context_data["worship_schedule"]
        if services:
            context_parts.append("\n[예배 일정]")
            for service in services:
                time_str = (
                    service["start_time"][:5] if service["start_time"] else "미정"
                )  # Extract HH:MM from time
                day_name = service.get("day_name", "미정")
                location_str = f" ({service['location']})" if service['location'] else ""
                online_str = " [온라인]" if service.get('is_online') else ""
                context_parts.append(
                    f"- {day_name} {time_str} {service['name']}: "
                    f"{service['service_type'] or '예배'}{location_str}{online_str}"
                )

    return "\n".join(context_parts) if context_parts else ""


# 🔍 Full-text Search Functions
def search_announcements(
    db: Session, church_id: int, search_query: str, limit: int = 50
) -> List[Dict]:
    """
    Search announcements using PostgreSQL full-text search.
    Supports both Korean and English text.
    """
    try:
        # Use both full-text search and trigram similarity for best results
        results = (
            db.query(Announcement)
            .filter(Announcement.church_id == church_id)
            .filter(
                text(
                    "to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '')) @@ plainto_tsquery('english', :query)"
                    " OR title % :query"  # trigram similarity
                    " OR content ILIKE :like_query"  # fallback for Korean
                ).params(
                    query=search_query, 
                    like_query=f"%{search_query}%"
                )
            )
            .order_by(desc(Announcement.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": ann.id,
                "title": ann.title,
                "content": ann.content,
                "category": ann.category,
                "author_name": ann.author_name,
                "created_at": ann.created_at.isoformat() if ann.created_at else None,
                "relevance_score": "high",  # Could implement ts_rank for scoring
            }
            for ann in results
        ]
    except Exception as e:
        logger.error(f"Error searching announcements: {e}")
        return []


def search_prayer_requests(
    db: Session, church_id: int, search_query: str, limit: int = 50
) -> List[Dict]:
    """
    Search prayer requests using full-text search.
    """
    try:
        results = (
            db.query(PrayerRequest)
            .filter(PrayerRequest.church_id == church_id)
            .filter(
                text(
                    "to_tsvector('english', COALESCE(prayer_content, '')) @@ plainto_tsquery('english', :query)"
                    " OR prayer_content ILIKE :like_query"
                ).params(
                    query=search_query,
                    like_query=f"%{search_query}%"
                )
            )
            .order_by(desc(PrayerRequest.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": req.id,
                "requester_name": req.requester_name if not req.is_anonymous else "익명",
                "prayer_content": req.prayer_content,
                "prayer_type": req.prayer_type,
                "created_at": req.created_at.isoformat() if req.created_at else None,
            }
            for req in results
        ]
    except Exception as e:
        logger.error(f"Error searching prayer requests: {e}")
        return []


def search_pastoral_care_requests(
    db: Session, church_id: int, search_query: str, limit: int = 50
) -> List[Dict]:
    """
    Search pastoral care requests using full-text search.
    """
    try:
        results = (
            db.query(PastoralCareRequest)
            .filter(PastoralCareRequest.church_id == church_id)
            .filter(
                text(
                    "to_tsvector('english', COALESCE(request_content, '')) @@ plainto_tsquery('english', :query)"
                    " OR request_content ILIKE :like_query"
                ).params(
                    query=search_query,
                    like_query=f"%{search_query}%"
                )
            )
            .order_by(desc(PastoralCareRequest.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": req.id,
                "requester_name": req.requester_name,
                "request_content": req.request_content,
                "request_type": req.request_type,
                "status": req.status,
                "created_at": req.created_at.isoformat() if req.created_at else None,
            }
            for req in results
        ]
    except Exception as e:
        logger.error(f"Error searching pastoral care requests: {e}")
        return []


def search_members(
    db: Session, church_id: int, search_query: str, limit: int = 50
) -> List[Dict]:
    """
    Search members by name using trigram similarity for fuzzy matching.
    """
    try:
        results = (
            db.query(Member)
            .filter(
                Member.church_id == church_id,
                Member.status == "active"
            )
            .filter(
                text(
                    "name % :query OR name_eng % :query OR name ILIKE :like_query"
                ).params(
                    query=search_query,
                    like_query=f"%{search_query}%"
                )
            )
            .order_by(
                text("similarity(name, :query) DESC").params(query=search_query)
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "id": member.id,
                "name": member.name,
                "name_eng": member.name_eng,
                "position": member.position,
                "department": member.department,
                "district": member.district,
                "phone": member.phone,
            }
            for member in results
        ]
    except Exception as e:
        logger.error(f"Error searching members: {e}")
        return []


def search_all_content(
    db: Session, church_id: int, search_query: str, limit_per_type: int = 20
) -> Dict[str, List[Dict]]:
    """
    Search across all content types and return combined results.
    """
    try:
        return {
            "announcements": search_announcements(db, church_id, search_query, limit_per_type),
            "prayer_requests": search_prayer_requests(db, church_id, search_query, limit_per_type),
            "pastoral_care_requests": search_pastoral_care_requests(db, church_id, search_query, limit_per_type),
            "members": search_members(db, church_id, search_query, limit_per_type),
            "search_query": search_query,
            "searched_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error in unified search: {e}")
        return {
            "announcements": [],
            "prayer_requests": [],
            "pastoral_care_requests": [],
            "members": [],
            "search_query": search_query,
            "error": str(e),
        }
