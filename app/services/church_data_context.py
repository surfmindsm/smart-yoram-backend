from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import logging

from app.models.announcement import Announcement
from app.models.user import User
from app.models.worship_schedule import WorshipService

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


def get_attendance_stats(db: Session, church_id: int) -> Dict:
    """
    Get attendance statistics for the church.
    """
    try:
        # TODO: Implement when attendance tracking is available
        # For now, return mock data
        return {
            "average_weekly_attendance": 0,
            "last_week_attendance": 0,
            "recent_attendances": [],
        }
    except Exception as e:
        logger.error(f"Error fetching attendance stats: {e}")
        return {
            "average_weekly_attendance": 0,
            "last_week_attendance": 0,
            "recent_attendances": [],
        }


def get_member_statistics(db: Session, church_id: int) -> Dict:
    """
    Get member statistics for the church (without personal information).
    """
    try:
        # Total members
        total_members = (
            db.query(User)
            .filter(User.church_id == church_id, User.is_active == True)
            .count()
        )

        # Members by role
        role_stats = (
            db.query(User.role, func.count(User.id).label("count"))
            .filter(User.church_id == church_id, User.is_active == True)
            .group_by(User.role)
            .all()
        )

        # New members this month
        start_of_month = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        new_members_this_month = (
            db.query(User)
            .filter(
                User.church_id == church_id,
                User.created_at >= start_of_month,
                User.is_active == True,
            )
            .count()
        )

        # Members by department (if available)
        department_stats = (
            db.query(User.department_id, func.count(User.id).label("count"))
            .filter(
                User.church_id == church_id,
                User.is_active == True,
                User.department_id.isnot(None),
            )
            .group_by(User.department_id)
            .all()
        )

        return {
            "total_members": total_members,
            "new_members_this_month": new_members_this_month,
            "members_by_role": {role: count for role, count in role_stats},
            "departments_count": len(department_stats),
        }
    except Exception as e:
        logger.error(f"Error fetching member statistics: {e}")
        return {
            "total_members": 0,
            "new_members_this_month": 0,
            "members_by_role": {},
            "departments_count": 0,
        }


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

    if context_data.get("attendances"):
        stats = context_data["attendances"]
        context_parts.append("\n[출석 현황]")
        context_parts.append(
            f"- 평균 주간 출석: {stats['average_weekly_attendance']}명"
        )
        context_parts.append(f"- 지난주 출석: {stats['last_week_attendance']}명")

    if context_data.get("members"):
        stats = context_data["members"]
        context_parts.append("\n[교인 현황]")
        context_parts.append(f"- 전체 교인: {stats['total_members']}명")
        context_parts.append(f"- 이번달 새신자: {stats['new_members_this_month']}명")

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
