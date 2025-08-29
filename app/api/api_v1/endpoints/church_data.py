from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import models
from app.services.church_data_context import get_church_context_data
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/context", response_model=Dict[str, Any])
def get_church_data_context(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    data_sources: Optional[str] = None,  # Comma-separated list of data sources
    format: str = "detailed",  # detailed, summary, compact
) -> Any:
    """
    Get comprehensive church data context for AI agents.

    Args:
        data_sources: Comma-separated list of data sources to include
                     (announcements,prayer_requests,pastoral_care,offerings,attendance,members,worship)
        format: Response format (detailed, summary, compact)
    """
    try:
        church_id = current_user.church_id
        if not church_id:
            raise HTTPException(
                status_code=400, detail="User not associated with any church"
            )

        # Parse data sources
        requested_sources = []
        if data_sources:
            requested_sources = [source.strip() for source in data_sources.split(",")]

        # Get comprehensive church context
        context_data = get_church_context_data(
            db=db,
            church_id=church_id,
            requested_sources=requested_sources,
            format=format,
        )

        return {
            "success": True,
            "data": {
                "church_id": church_id,
                "data_sources": context_data,
                "generated_at": context_data.get("metadata", {}).get("generated_at"),
                "format": format,
                "requested_sources": requested_sources or ["all"],
            },
        }

    except Exception as e:
        logger.error(f"Error fetching church data context: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch church context: {str(e)}"
        )


@router.get("/context/formatted", response_model=Dict[str, Any])
def get_formatted_church_context(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    data_sources: Optional[str] = None,
    format_type: str = "gpt_context",  # gpt_context, json, summary
) -> Any:
    """
    Get church data formatted specifically for GPT context.
    This endpoint formats the data optimally for AI agent consumption.
    """
    try:
        church_id = current_user.church_id
        if not church_id:
            raise HTTPException(
                status_code=400, detail="User not associated with any church"
            )

        # Parse data sources
        requested_sources = []
        if data_sources:
            requested_sources = [source.strip() for source in data_sources.split(",")]

        # Get church context data
        context_data = get_church_context_data(
            db=db,
            church_id=church_id,
            requested_sources=requested_sources,
            format="detailed",
        )

        # Format for GPT context
        if format_type == "gpt_context":
            formatted_context = format_for_gpt_context(context_data, church_id, db)

            return {
                "success": True,
                "data": {
                    "church_id": church_id,
                    "gpt_context": formatted_context,
                    "context_length": len(formatted_context),
                    "data_sources_included": list(context_data.keys()),
                    "generated_at": context_data.get("metadata", {}).get(
                        "generated_at"
                    ),
                },
            }

        elif format_type == "summary":
            summary_context = create_summary_context(context_data)

            return {
                "success": True,
                "data": {
                    "church_id": church_id,
                    "summary_context": summary_context,
                    "generated_at": context_data.get("metadata", {}).get(
                        "generated_at"
                    ),
                },
            }

        else:  # json format
            return {
                "success": True,
                "data": {
                    "church_id": church_id,
                    "json_context": context_data,
                    "generated_at": context_data.get("metadata", {}).get(
                        "generated_at"
                    ),
                },
            }

    except Exception as e:
        logger.error(f"Error fetching formatted church context: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to format church context: {str(e)}"
        )


def format_for_gpt_context(context_data: Dict, church_id: int, db: Session) -> str:
    """
    Format church data optimally for GPT context consumption.
    """
    try:
        # Get church name
        church = db.query(models.Church).filter(models.Church.id == church_id).first()
        church_name = church.name if church else f"Church {church_id}"

        formatted_sections = []

        # Header
        formatted_sections.append(f"=== {church_name} 교회 데이터베이스 정보 ===\n")

        # Announcements
        if "announcements" in context_data and context_data["announcements"]:
            formatted_sections.append("📢 **최근 공지사항:**")
            announcements = context_data["announcements"][:10]  # Latest 10
            for ann in announcements:
                formatted_sections.append(
                    f"- [{ann.get('category', 'general')}] {ann.get('title', '')}"
                )
                if ann.get("content"):
                    content = (
                        ann["content"][:200] + "..."
                        if len(ann["content"]) > 200
                        else ann["content"]
                    )
                    formatted_sections.append(f"  내용: {content}")
                formatted_sections.append(f"  작성일: {ann.get('created_at', '')}")
            formatted_sections.append("")

        # Prayer Requests
        if "prayer_requests" in context_data and context_data["prayer_requests"]:
            formatted_sections.append("🙏 **기도 요청사항:**")
            prayers = context_data["prayer_requests"][:10]
            for prayer in prayers:
                formatted_sections.append(
                    f"- 요청자: {prayer.get('requester_name', 'Unknown')}"
                )
                formatted_sections.append(
                    f"  유형: {prayer.get('prayer_type', 'general')}"
                )
                content = prayer.get("prayer_content", "")
                if content:
                    content = content[:150] + "..." if len(content) > 150 else content
                    formatted_sections.append(f"  내용: {content}")
                if prayer.get("is_urgent"):
                    formatted_sections.append("  ⚠️ 긴급 요청")
                formatted_sections.append(f"  요청일: {prayer.get('created_at', '')}")
            formatted_sections.append("")

        # Pastoral Care Requests
        if (
            "pastoral_care_requests" in context_data
            and context_data["pastoral_care_requests"]
        ):
            formatted_sections.append("👥 **심방 요청사항:**")
            pastoral = context_data["pastoral_care_requests"][:10]
            for req in pastoral:
                formatted_sections.append(
                    f"- 요청자: {req.get('requester_name', 'Unknown')}"
                )
                formatted_sections.append(
                    f"  유형: {req.get('request_type', 'general')}"
                )
                formatted_sections.append(f"  상태: {req.get('status', 'pending')}")
                if req.get("scheduled_date"):
                    formatted_sections.append(f"  예정일: {req.get('scheduled_date')}")
                formatted_sections.append(f"  요청일: {req.get('created_at', '')}")
            formatted_sections.append("")

        # Offerings Summary
        if "offering_stats" in context_data and context_data["offering_stats"]:
            formatted_sections.append("💰 **헌금 현황:**")
            offering = context_data["offering_stats"]
            if offering.get("totals"):
                totals = offering["totals"]
                formatted_sections.append(
                    f"- 이번 달 총 헌금: {totals.get('total_this_month', 0):,}원"
                )
                formatted_sections.append(
                    f"- 올해 총 헌금: {totals.get('total_this_year', 0):,}원"
                )
                formatted_sections.append(
                    f"- 전체 헌금 교인 수: {totals.get('total_members', 0)}명"
                )

            if offering.get("fund_stats_month"):
                formatted_sections.append("  이번 달 헌금 종류별:")
                for fund in offering["fund_stats_month"][:5]:
                    formatted_sections.append(
                        f"    • {fund.get('fund_type', 'Unknown')}: {fund.get('total', 0):,}원 ({fund.get('count', 0)}건)"
                    )
            formatted_sections.append("")

        # Attendance Stats
        if "attendance_stats" in context_data and context_data["attendance_stats"]:
            formatted_sections.append("📊 **출석 현황:**")
            attendance = context_data["attendance_stats"]
            if attendance.get("average_weekly_attendance"):
                formatted_sections.append(
                    f"- 주간 평균 출석: {attendance['average_weekly_attendance']}명"
                )

            if attendance.get("service_stats"):
                formatted_sections.append("  예배별 출석 현황:")
                for service in attendance["service_stats"][:5]:
                    formatted_sections.append(
                        f"    • {service.get('service_type', 'Unknown')}: {service.get('total_attendance', 0)}명"
                    )
            formatted_sections.append("")

        # Member Statistics
        if "member_stats" in context_data and context_data["member_stats"]:
            formatted_sections.append("👨‍👩‍👧‍👦 **교인 현황:**")
            members = context_data["member_stats"]
            formatted_sections.append(
                f"- 총 교인 수: {members.get('total_members', 0)}명"
            )
            formatted_sections.append(
                f"- 이번 달 신규 등록: {members.get('new_members_this_month', 0)}명"
            )
            formatted_sections.append(
                f"- 세례 교인: {members.get('recent_baptisms', 0)}명"
            )
            formatted_sections.append(
                f"- 가족 수: {members.get('family_count', 0)}가정"
            )

            if members.get("gender_distribution"):
                gender = members["gender_distribution"]
                formatted_sections.append(
                    f"- 성별 분포: 남성 {gender.get('M', 0)}명, 여성 {gender.get('F', 0)}명"
                )

            if members.get("members_by_position"):
                formatted_sections.append("  직분별 분포:")
                for position, count in list(members["members_by_position"].items())[:5]:
                    formatted_sections.append(f"    • {position}: {count}명")
            formatted_sections.append("")

        # Worship Schedule
        if "worship_schedule" in context_data and context_data["worship_schedule"]:
            formatted_sections.append("⛪ **예배 일정:**")
            worship = context_data["worship_schedule"][:10]
            for service in worship:
                formatted_sections.append(f"- {service.get('worship_type', 'Unknown')}")
                formatted_sections.append(
                    f"  일시: {service.get('worship_date', '')} {service.get('start_time', '')}"
                )
                if service.get("location"):
                    formatted_sections.append(f"  장소: {service.get('location')}")
                if service.get("preacher"):
                    formatted_sections.append(f"  설교자: {service.get('preacher')}")
                if service.get("sermon_title"):
                    formatted_sections.append(
                        f"  설교 제목: {service.get('sermon_title')}"
                    )
            formatted_sections.append("")

        # Footer
        formatted_sections.append("=" * 50)

        return "\n".join(formatted_sections)

    except Exception as e:
        logger.error(f"Error formatting GPT context: {e}")
        return f"교회 데이터 포맷팅 중 오류가 발생했습니다: {str(e)}"


def create_summary_context(context_data: Dict) -> str:
    """
    Create a concise summary of church context data.
    """
    summary_parts = []

    # Count data points
    announcements_count = len(context_data.get("announcements", []))
    prayers_count = len(context_data.get("prayer_requests", []))
    pastoral_count = len(context_data.get("pastoral_care_requests", []))

    if announcements_count > 0:
        summary_parts.append(f"공지사항 {announcements_count}건")

    if prayers_count > 0:
        summary_parts.append(f"기도요청 {prayers_count}건")

    if pastoral_count > 0:
        summary_parts.append(f"심방요청 {pastoral_count}건")

    # Member stats
    if "member_stats" in context_data:
        member_stats = context_data["member_stats"]
        total_members = member_stats.get("total_members", 0)
        summary_parts.append(f"총 교인 {total_members}명")

    # Offering stats
    if "offering_stats" in context_data:
        offering_stats = context_data["offering_stats"]
        if offering_stats.get("totals", {}).get("total_this_month"):
            total_month = offering_stats["totals"]["total_this_month"]
            summary_parts.append(f"이번 달 헌금 {total_month:,}원")

    return (
        "교회 현황: " + ", ".join(summary_parts)
        if summary_parts
        else "교회 데이터 없음"
    )
