from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import logging

from app.models.announcement import Announcement
from app.models.user import User
from app.models.worship_schedule import WorshipService
from app.models.pastoral_care import PastoralCareRequest, PrayerRequest

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
