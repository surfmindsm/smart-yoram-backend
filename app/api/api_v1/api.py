from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    auth_member,
    users,
    members,
    churches,
    attendances,
    bulletins,
    member_photos,
    sms,
    qr_codes,
    calendar,
    excel,
    statistics,
    family,
    member_card,
    announcements,
    daily_verses,
    worship_schedule,
    push_notifications,
    health,
    ai_agents,
    chat,
    church,
    analytics,
    debug,
    pastoral_care,
    prayer_requests,
    financial,
    member_enhanced,
    geocoding,
    system_logs,
    setup,
)


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    auth_member.router, prefix="/auth/member", tags=["auth_member"]
)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(
    member_photos.router, prefix="/members", tags=["member_photos"]
)
api_router.include_router(churches.router, prefix="/churches", tags=["churches"])
api_router.include_router(
    attendances.router, prefix="/attendances", tags=["attendances"]
)
api_router.include_router(bulletins.router, prefix="/bulletins", tags=["bulletins"])
api_router.include_router(sms.router, prefix="/sms", tags=["sms"])
api_router.include_router(qr_codes.router, prefix="/qr-codes", tags=["qr_codes"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(excel.router, prefix="/excel", tags=["excel"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(family.router, prefix="/family", tags=["family"])
api_router.include_router(
    member_card.router, prefix="/member-card", tags=["member_card"]
)
api_router.include_router(
    announcements.router, prefix="/announcements", tags=["announcements"]
)
api_router.include_router(
    daily_verses.router, prefix="/daily-verses", tags=["daily_verses"]
)
api_router.include_router(
    worship_schedule.router, prefix="/worship", tags=["worship_schedule"]
)
api_router.include_router(
    push_notifications.router, prefix="/notifications", tags=["push_notifications"]
)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ai_agents.router, prefix="/agents", tags=["ai_agents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(church.router, prefix="/church", tags=["church"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(debug.router, prefix="/debug", tags=["debug"])
api_router.include_router(
    pastoral_care.router, prefix="/pastoral-care", tags=["pastoral_care"]
)
api_router.include_router(
    prayer_requests.router, prefix="/prayer-requests", tags=["prayer_requests"]
)
api_router.include_router(financial.router, prefix="/financial", tags=["financial"])
api_router.include_router(
    member_enhanced.router, prefix="/members", tags=["member_enhanced"]
)
api_router.include_router(geocoding.router, prefix="/geocoding", tags=["geocoding"])
api_router.include_router(
    system_logs.router, prefix="/system-logs", tags=["system_logs"]
)
api_router.include_router(setup.router, prefix="/setup", tags=["setup"])
