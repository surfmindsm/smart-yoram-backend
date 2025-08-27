from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
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
    db: Session, church_id: int, church_data_sources: Dict, user_query: str = ""
) -> Dict[str, Any]:
    """
    Retrieve church data based on enabled data sources.

    Args:
        db: Database session
        church_id: Church ID
        church_data_sources: Dictionary of enabled data sources
        user_query: User's query to help filter relevant data

    Returns:
        Dictionary containing church context data
    """
    context_data = {}

    try:
        if church_data_sources.get("announcements"):
            context_data["announcements"] = get_recent_announcements(db, church_id)

        if church_data_sources.get("attendances"):
            context_data["attendances"] = get_attendance_stats(db, church_id)

        if church_data_sources.get("members"):
            context_data["members"] = get_member_statistics(db, church_id)

        if church_data_sources.get("worship_services"):
            context_data["worship_services"] = get_worship_schedule(db, church_id)
            
        if church_data_sources.get("prayer_requests"):
            context_data["prayer_requests"] = get_recent_prayer_requests(db, church_id)
            
        if church_data_sources.get("pastoral_care_requests"):
            context_data["pastoral_care_requests"] = get_recent_pastoral_care_requests(db, church_id)
            
        if church_data_sources.get("offerings"):
            context_data["offerings"] = get_recent_offerings(db, church_id)
            
        if church_data_sources.get("attendances"):
            context_data["attendances"] = get_attendance_stats(db, church_id)
            
        if church_data_sources.get("members"):
            context_data["members"] = get_enhanced_member_statistics(db, church_id)

    except Exception as e:
        logger.error(f"Error retrieving church context data: {e}")

    return context_data


def get_recent_announcements(
    db: Session, church_id: int, limit: int = 10
) -> List[Dict]:
    """
    Get recent announcements for the church.
    """
    try:
        announcements = (
            db.query(Announcement)
            .filter(Announcement.church_id == church_id, Announcement.is_active == True)
            .order_by(desc(Announcement.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": ann.id,
                "title": ann.title,
                "content": (
                    ann.content[:200] + "..." if len(ann.content) > 200 else ann.content
                ),
                "category": ann.category,
                "created_at": ann.created_at.isoformat() if ann.created_at else None,
                "is_pinned": getattr(ann, 'is_pinned', False),
                "target_audience": getattr(ann, 'target_audience', 'all'),
            }
            for ann in announcements
        ]
    except Exception as e:
        logger.error(f"Error fetching announcements: {e}")
        return []


def get_recent_prayer_requests(
    db: Session, church_id: int, limit: int = 10
) -> List[Dict]:
    """
    Get recent prayer requests for the church.
    """
    try:
        prayer_requests = (
            db.query(PrayerRequest)
            .filter(
                PrayerRequest.church_id == church_id,
                PrayerRequest.status == "active",
                PrayerRequest.is_public == True
            )
            .order_by(desc(PrayerRequest.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": req.id,
                "requester_name": req.requester_name if not req.is_anonymous else "익명",
                "prayer_type": req.prayer_type,
                "prayer_content": (
                    req.prayer_content[:150] + "..." if len(req.prayer_content) > 150 else req.prayer_content
                ),
                "is_urgent": req.is_urgent,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "prayer_count": req.prayer_count,
                "expires_at": req.expires_at.isoformat() if req.expires_at else None,
            }
            for req in prayer_requests
        ]
    except Exception as e:
        logger.error(f"Error fetching prayer requests: {e}")
        return []


def get_recent_pastoral_care_requests(
    db: Session, church_id: int, limit: int = 10
) -> List[Dict]:
    """
    Get recent pastoral care requests for the church.
    """
    try:
        pastoral_requests = (
            db.query(PastoralCareRequest)
            .filter(
                PastoralCareRequest.church_id == church_id,
                PastoralCareRequest.status.in_(["pending", "approved", "scheduled"])
            )
            .order_by(desc(PastoralCareRequest.created_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": req.id,
                "requester_name": req.requester_name,
                "request_type": req.request_type,
                "request_content": (
                    req.request_content[:150] + "..." if len(req.request_content) > 150 else req.request_content
                ),
                "priority": req.priority,
                "is_urgent": req.is_urgent,
                "status": req.status,
                "preferred_date": req.preferred_date.isoformat() if req.preferred_date else None,
                "scheduled_date": req.scheduled_date.isoformat() if req.scheduled_date else None,
                "scheduled_time": req.scheduled_time.isoformat() if req.scheduled_time else None,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "address": req.address,
            }
            for req in pastoral_requests
        ]
    except Exception as e:
        logger.error(f"Error fetching pastoral care requests: {e}")
        return []


def get_recent_offerings(
    db: Session, church_id: int, days: int = 30
) -> Dict:
    """
    Get comprehensive offering statistics for the church.
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate multiple date ranges
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # This year and last year
        current_year = end_date.year
        last_year = current_year - 1
        this_year_start = datetime(current_year, 1, 1).date()
        last_year_start = datetime(last_year, 1, 1).date()
        last_year_end = datetime(last_year, 12, 31).date()
        
        # Current month and last month
        current_month_start = end_date.replace(day=1)
        if current_month_start.month == 1:
            last_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            last_month_start = current_month_start.replace(month=current_month_start.month - 1)
        
        # Get total offering for recent period
        total_recent = db.query(func.sum(Offering.amount)).filter(
            Offering.church_id == church_id,
            Offering.offered_on >= start_date,
            Offering.offered_on <= end_date
        ).scalar() or 0
        
        # Get this year total
        total_this_year = db.query(func.sum(Offering.amount)).filter(
            Offering.church_id == church_id,
            Offering.offered_on >= this_year_start,
            Offering.offered_on <= end_date
        ).scalar() or 0
        
        # Get last year total
        total_last_year = db.query(func.sum(Offering.amount)).filter(
            Offering.church_id == church_id,
            Offering.offered_on >= last_year_start,
            Offering.offered_on <= last_year_end
        ).scalar() or 0
        
        # Get this month total
        total_this_month = db.query(func.sum(Offering.amount)).filter(
            Offering.church_id == church_id,
            Offering.offered_on >= current_month_start,
            Offering.offered_on <= end_date
        ).scalar() or 0
        
        # Get last month total
        if current_month_start.month == 1:
            last_month_end = datetime(current_month_start.year - 1, 12, 31).date()
        else:
            last_month_end = current_month_start - timedelta(days=1)
            
        total_last_month = db.query(func.sum(Offering.amount)).filter(
            Offering.church_id == church_id,
            Offering.offered_on >= last_month_start,
            Offering.offered_on <= last_month_end
        ).scalar() or 0
        
        # Monthly breakdown for this year
        monthly_breakdown = (
            db.query(
                func.extract('month', Offering.offered_on).label('month'),
                func.sum(Offering.amount).label('total')
            )
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= this_year_start,
                Offering.offered_on <= end_date
            )
            .group_by(func.extract('month', Offering.offered_on))
            .order_by('month')
            .all()
        )
        
        # Fund type breakdown for this year
        fund_stats_year = (
            db.query(
                Offering.fund_type,
                func.sum(Offering.amount).label('total'),
                func.count(Offering.id).label('count')
            )
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= this_year_start,
                Offering.offered_on <= end_date
            )
            .group_by(Offering.fund_type)
            .order_by(desc('total'))
            .all()
        )
        
        # Average offering per member (if member data available)
        total_members = (
            db.query(Member)
            .filter(Member.church_id == church_id, Member.status == "active")
            .count()
        )
        
        avg_offering_per_member = (total_this_month / total_members) if total_members > 0 else 0
        
        # Get recent individual offerings (more details)
        recent_offerings = (
            db.query(Offering)
            .join(Member, isouter=True)
            .filter(
                Offering.church_id == church_id,
                Offering.offered_on >= start_date
            )
            .order_by(desc(Offering.offered_on))
            .limit(10)
            .all()
        )
        
        return {
            "period_days": days,
            "totals": {
                "recent_period": float(total_recent),
                "this_year": float(total_this_year),
                "last_year": float(total_last_year),
                "this_month": float(total_this_month),
                "last_month": float(total_last_month),
                "year_over_year_change": float((total_this_year - total_last_year) / total_last_year * 100) if total_last_year > 0 else 0,
                "month_over_month_change": float((total_this_month - total_last_month) / total_last_month * 100) if total_last_month > 0 else 0,
            },
            "monthly_breakdown": [
                {
                    "month": int(month.month),
                    "month_name": ["", "1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"][int(month.month)],
                    "total": float(month.total)
                } for month in monthly_breakdown
            ],
            "fund_breakdown": [
                {
                    "fund_type": fund.fund_type,
                    "total": float(fund.total),
                    "count": fund.count,
                    "percentage": float(fund.total / total_this_year * 100) if total_this_year > 0 else 0
                } for fund in fund_stats_year
            ],
            "statistics": {
                "total_members": total_members,
                "avg_offering_per_member_this_month": round(avg_offering_per_member, 0),
                "total_offerings_count_this_year": sum(fund.count for fund in fund_stats_year),
            },
            "recent_offerings": [
                {
                    "member_name": offering.member.name if offering.member else "익명",
                    "fund_type": offering.fund_type,
                    "amount": float(offering.amount),
                    "date": offering.offered_on.isoformat(),
                    "note": offering.note
                } for offering in recent_offerings
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching offering statistics: {e}")
        return {
            "period_days": days,
            "total_amount": 0,
            "fund_breakdown": [],
            "recent_offerings": []
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
                Attendance.present == True
            )
            .scalar() or 0
        )
        
        # Get attendance by service type for last 4 weeks
        four_weeks_ago = today - timedelta(weeks=4)
        service_stats = (
            db.query(
                Attendance.service_type,
                func.count(Attendance.id).label('total_attendance'),
                func.count(func.distinct(Attendance.service_date)).label('service_count')
            )
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= four_weeks_ago,
                Attendance.present == True
            )
            .group_by(Attendance.service_type)
            .all()
        )
        
        # Monthly attendance trends (last 12 months)
        twelve_months_ago = today - timedelta(days=365)
        monthly_attendance = (
            db.query(
                func.extract('year', Attendance.service_date).label('year'),
                func.extract('month', Attendance.service_date).label('month'),
                func.count(Attendance.id).label('attendance_count'),
                func.count(func.distinct(Attendance.member_id)).label('unique_attendees')
            )
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= twelve_months_ago,
                Attendance.present == True
            )
            .group_by(
                func.extract('year', Attendance.service_date),
                func.extract('month', Attendance.service_date)
            )
            .order_by('year', 'month')
            .all()
        )
        
        # Attendance by member (top attendees this year)
        year_start = today.replace(month=1, day=1)
        top_attendees = (
            db.query(
                Member.name,
                func.count(Attendance.id).label('attendance_count')
            )
            .join(Attendance)
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= year_start,
                Attendance.present == True
            )
            .group_by(Member.id, Member.name)
            .order_by(desc('attendance_count'))
            .limit(10)
            .all()
        )
        
        # Weekly attendance pattern (last 8 weeks)
        eight_weeks_ago = today - timedelta(weeks=8)
        weekly_attendance = (
            db.query(
                func.extract('week', Attendance.service_date).label('week'),
                func.extract('year', Attendance.service_date).label('year'),
                func.count(Attendance.id).label('attendance_count')
            )
            .filter(
                Attendance.church_id == church_id,
                Attendance.service_date >= eight_weeks_ago,
                Attendance.present == True
            )
            .group_by(
                func.extract('year', Attendance.service_date),
                func.extract('week', Attendance.service_date)
            )
            .order_by('year', 'week')
            .all()
        )
        
        # Get recent attendance records
        recent_attendance = (
            db.query(Attendance)
            .join(Member)
            .filter(
                Attendance.church_id == church_id,
                Attendance.present == True
            )
            .order_by(desc(Attendance.service_date))
            .limit(10)
            .all()
        )
        
        # Calculate average weekly attendance
        average_weekly = 0
        if service_stats:
            total_weekly_attendance = sum(stat.total_attendance for stat in service_stats if stat.service_count >= 2)
            service_weeks = max(stat.service_count for stat in service_stats) if service_stats else 0
            if service_weeks > 0:
                average_weekly = total_weekly_attendance // service_weeks
        
        return {
            "total_members": total_members,
            "average_weekly_attendance": average_weekly,
            "last_week_attendance": last_week_attendance,
            "attendance_rate": round((last_week_attendance / total_members * 100), 1) if total_members > 0 else 0,
            "service_breakdown": [
                {
                    "service_type": stat.service_type,
                    "avg_attendance": stat.total_attendance // stat.service_count if stat.service_count > 0 else 0,
                    "service_count": stat.service_count,
                    "total_attendance": stat.total_attendance
                } for stat in service_stats
            ],
            "monthly_trends": [
                {
                    "year": int(month.year),
                    "month": int(month.month),
                    "month_name": ["", "1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"][int(month.month)],
                    "total_attendance": month.attendance_count,
                    "unique_attendees": month.unique_attendees
                } for month in monthly_attendance
            ],
            "weekly_trends": [
                {
                    "year": int(week.year),
                    "week": int(week.week),
                    "attendance_count": week.attendance_count
                } for week in weekly_attendance
            ],
            "top_attendees": [
                {
                    "member_name": attendee.name,
                    "attendance_count": attendee.attendance_count
                } for attendee in top_attendees
            ],
            "recent_attendances": [
                {
                    "member_name": att.member.name if att.member else "Unknown",
                    "service_type": att.service_type,
                    "service_date": att.service_date.isoformat(),
                    "check_in_time": att.check_in_time.isoformat() if att.check_in_time else None,
                    "check_in_method": att.check_in_method
                } for att in recent_attendance
            ]
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
        start_of_month = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        ).date()
        new_members_this_month = (
            db.query(Member)
            .filter(
                Member.church_id == church_id,
                Member.registration_date >= start_of_month,
                Member.status == "active"
            )
            .count()
        )

        # Members by department
        department_stats = (
            db.query(Member.department, func.count(Member.id).label("count"))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.department.isnot(None)
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
                Member.district.isnot(None)
            )
            .group_by(Member.district)
            .all()
        )

        # Age demographics
        age_ranges = {
            "children": (0, 12),
            "youth": (13, 18),
            "young_adult": (19, 35),
            "adult": (36, 60),
            "senior": (61, 150)
        }
        
        age_stats = {}
        for range_name, (min_age, max_age) in age_ranges.items():
            count = (
                db.query(Member)
                .filter(
                    Member.church_id == church_id,
                    Member.status == "active",
                    Member.age >= min_age,
                    Member.age <= max_age
                )
                .count()
            )
            age_stats[range_name] = count

        # Gender statistics (more detailed)
        gender_stats = (
            db.query(Member.gender, func.count(Member.id).label("count"))
            .filter(
                Member.church_id == church_id,
                Member.status == "active",
                Member.gender.isnot(None)
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
                Member.marital_status.isnot(None)
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
                Member.age.isnot(None)
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
                Member.age.isnot(None)
            )
            .scalar()
        )

        # Recent baptisms (last 6 months)
        six_months_ago = datetime.now().date() - timedelta(days=180)
        recent_baptisms = (
            db.query(Member)
            .filter(
                Member.church_id == church_id,
                Member.baptism_date >= six_months_ago,
                Member.status == "active"
            )
            .count()
        )

        # Family count
        family_count = (
            db.query(Family)
            .filter(Family.church_id == church_id)
            .count()
        )

        return {
            "total_members": total_members,
            "new_members_this_month": new_members_this_month,
            "recent_baptisms": recent_baptisms,
            "family_count": family_count,
            "average_age": round(avg_age, 1) if avg_age else 0,
            "members_by_position": {pos: count for pos, count in position_stats if pos},
            "members_by_department": {dept: count for dept, count in department_stats if dept},
            "members_by_district": {district: count for district, count in district_stats if district},
            "age_demographics": age_stats,
            "detailed_age_distribution": {age: count for age, count in age_distribution},
            "gender_distribution": {gender: count for gender, count in gender_stats if gender},
            "marital_status_distribution": {status: count for status, count in marital_stats if status},
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


def get_worship_schedule(db: Session, church_id: int) -> List[Dict]:
    """
    Get upcoming worship services schedule.
    """
    try:
        # Get next 2 weeks of worship services
        two_weeks_later = datetime.now() + timedelta(weeks=2)

        services = (
            db.query(WorshipService)
            .filter(
                WorshipService.church_id == church_id,
                WorshipService.worship_date >= datetime.now(),
                WorshipService.worship_date <= two_weeks_later,
                WorshipService.is_active == True,
            )
            .order_by(WorshipService.worship_date)
            .all()
        )

        return [
            {
                "id": service.id,
                "worship_type": service.worship_type,
                "worship_date": (
                    service.worship_date.isoformat() if service.worship_date else None
                ),
                "start_time": (
                    service.start_time.isoformat() if service.start_time else None
                ),
                "end_time": service.end_time.isoformat() if service.end_time else None,
                "location": service.location,
                "preacher": service.preacher,
                "sermon_title": service.sermon_title,
                "bible_text": service.bible_text,
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
            for req in prayer_requests[:5]:  # Limit to 5 most recent
                urgency = " (긴급)" if req['is_urgent'] else ""
                context_parts.append(
                    f"- {req['requester_name']}: {req['prayer_content']}{urgency} "
                    f"[{req['prayer_type']}, 기도수: {req['prayer_count']}]"
                )

    if context_data.get("pastoral_care_requests"):
        pastoral_requests = context_data["pastoral_care_requests"]
        if pastoral_requests:
            context_parts.append("\n[심방 요청]")
            for req in pastoral_requests[:5]:  # Limit to 5 most recent
                urgency = " (긴급)" if req['is_urgent'] else ""
                status_text = {"pending": "대기중", "approved": "승인됨", "scheduled": "예약됨"}.get(req['status'], req['status'])
                date_info = f", 희망일: {req['preferred_date']}" if req['preferred_date'] else ""
                scheduled_info = f", 예약일시: {req['scheduled_date']} {req['scheduled_time']}" if req['scheduled_date'] else ""
                context_parts.append(
                    f"- {req['requester_name']}: {req['request_content']}{urgency} "
                    f"[{req['request_type']}, {status_text}{date_info}{scheduled_info}]"
                )

    if context_data.get("offerings"):
        offering_data = context_data["offerings"]
        if offering_data.get("totals", {}).get("this_year", 0) > 0:
            totals = offering_data["totals"]
            context_parts.append("\n[헌금 현황]")
            context_parts.append(f"- 올해 총 헌금: {totals['this_year']:,.0f}원")
            context_parts.append(f"- 작년 대비: {totals['year_over_year_change']:+.1f}% ({totals['last_year']:,.0f}원)")
            context_parts.append(f"- 이번달: {totals['this_month']:,.0f}원 (전월 대비 {totals['month_over_month_change']:+.1f}%)")
            
            stats = offering_data.get("statistics", {})
            if stats.get("total_members", 0) > 0:
                context_parts.append(f"- 교인 1인당 월평균: {stats['avg_offering_per_member_this_month']:,.0f}원")
            
            if offering_data.get("fund_breakdown"):
                context_parts.append("- 헌금 종류별:")
                for fund in offering_data["fund_breakdown"][:3]:  # Top 3
                    context_parts.append(f"  • {fund['fund_type']}: {fund['total']:,.0f}원 ({fund['percentage']:.1f}%)")
            
            if offering_data.get("monthly_breakdown"):
                context_parts.append("- 월별 추이 (최근):")
                for month in offering_data["monthly_breakdown"][-3:]:  # Last 3 months
                    context_parts.append(f"  • {month['month_name']}: {month['total']:,.0f}원")

    if context_data.get("attendances"):
        stats = context_data["attendances"]
        if stats["total_members"] > 0:
            context_parts.append("\n[출석 현황]")
            context_parts.append(f"- 등록 교인: {stats['total_members']}명")
            context_parts.append(f"- 지난주 출석: {stats['last_week_attendance']}명 ({stats['attendance_rate']}%)")
            context_parts.append(f"- 평균 주간 출석: {stats['average_weekly_attendance']}명")
            
            if stats.get("service_breakdown"):
                context_parts.append("- 예배별 출석:")
                service_names = {"sunday_morning": "주일 오전", "sunday_evening": "주일 오후", "wednesday": "수요예배", "friday": "금요예배"}
                for service in stats["service_breakdown"]:
                    service_name = service_names.get(service["service_type"], service["service_type"])
                    context_parts.append(f"  • {service_name}: 평균 {service['avg_attendance']}명 (총 {service['total_attendance']}회)")
            
            if stats.get("monthly_trends"):
                context_parts.append("- 월별 출석 추이 (최근):")
                for trend in stats["monthly_trends"][-3:]:  # Last 3 months
                    context_parts.append(f"  • {trend['month_name']}: {trend['total_attendance']}회 (고유 출석자 {trend['unique_attendees']}명)")
            
            if stats.get("top_attendees"):
                context_parts.append("- 올해 최다 출석자:")
                for attendee in stats["top_attendees"][:3]:  # Top 3
                    context_parts.append(f"  • {attendee['member_name']}: {attendee['attendance_count']}회")

    if context_data.get("members"):
        stats = context_data["members"]
        if stats["total_members"] > 0:
            context_parts.append("\n[교인 현황]")
            context_parts.append(f"- 전체 등록 교인: {stats['total_members']}명 (평균연령: {stats.get('average_age', 0)}세)")
            context_parts.append(f"- 이번달 새신자: {stats['new_members_this_month']}명")
            context_parts.append(f"- 최근 6개월 세례자: {stats['recent_baptisms']}명")
            context_parts.append(f"- 등록 가정수: {stats['family_count']}가정")
            
            # Gender distribution
            if stats.get("gender_distribution"):
                gender_stats = stats["gender_distribution"]
                # 모든 가능한 성별 값들을 체크
                male_keys = ["M", "m", "male", "남성", "남", "Male", "MALE"]
                female_keys = ["F", "f", "female", "여성", "여", "Female", "FEMALE"]
                
                male_count = sum(gender_stats.get(key, 0) for key in male_keys)
                female_count = sum(gender_stats.get(key, 0) for key in female_keys)
                
                # 실제 데이터베이스의 모든 gender 값들도 표시 (디버깅용)
                all_genders = {k: v for k, v in gender_stats.items() if v > 0}
                
                if male_count > 0 or female_count > 0:
                    context_parts.append(f"- 성별 분포: 남성 {male_count}명, 여성 {female_count}명")
                    if len(all_genders) > 0:
                        context_parts.append(f"  (데이터베이스 원본값: {all_genders})")
            
            # Marital status
            if stats.get("marital_status_distribution"):
                marital_names = {"single": "미혼", "married": "기혼", "divorced": "이혼", "widowed": "사별"}
                marital_stats = []
                for status, count in stats["marital_status_distribution"].items():
                    if count > 0:
                        status_name = marital_names.get(status, status)
                        marital_stats.append(f"{status_name} {count}명")
                if marital_stats:
                    context_parts.append(f"- 혼인상태: {', '.join(marital_stats)}")
            
            if stats.get("members_by_position"):
                context_parts.append("- 직분별 분포:")
                position_names = {"pastor": "목사", "elder": "장로", "deacon": "집사", "member": "성도", "youth": "청년", "child": "아동"}
                for pos, count in stats["members_by_position"].items():
                    pos_name = position_names.get(pos, pos)
                    context_parts.append(f"  • {pos_name}: {count}명")
                    
            if stats.get("members_by_department"):
                context_parts.append("- 부서별 분포:")
                for dept, count in list(stats["members_by_department"].items())[:5]:  # Top 5 departments
                    context_parts.append(f"  • {dept}: {count}명")
                    
            if stats.get("age_demographics"):
                context_parts.append("- 연령대별 분포:")
                age_names = {"children": "아동(0-12세)", "youth": "청소년(13-18세)", "young_adult": "청년(19-35세)", "adult": "장년(36-60세)", "senior": "노년(61세+)"}
                for age_range, count in stats["age_demographics"].items():
                    if count > 0:
                        age_name = age_names.get(age_range, age_range)
                        context_parts.append(f"  • {age_name}: {count}명")

    if context_data.get("worship_services"):
        services = context_data["worship_services"]
        if services:
            context_parts.append("\n[예배 일정]")
            for service in services[:3]:  # Limit to next 3 services
                date_str = (
                    service["worship_date"].split("T")[0]
                    if service["worship_date"]
                    else "미정"
                )
                context_parts.append(
                    f"- {date_str} {service['worship_type']}: "
                    f"{service['sermon_title'] or '미정'} ({service['preacher'] or '미정'})"
                )

    return "\n".join(context_parts) if context_parts else ""
