from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    auth_member,
    users,
    members,
    member_codes,
    member_numbers,
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
    system_announcements,
    daily_verses,
    worship_schedule,
    push_notifications,
    health,
    ai_agents,
    chat,
    church,
    church_data,
    analytics,
    debug,
    pastoral_care,
    prayer_requests,
    financial,
    member_enhanced,
    geocoding,
    system_logs,
    setup,
    sermon_materials,
    smart_assistant,
    community_applications,
    community_home,
    community_sharing,
    community_request,
    job_posts,
    music_requests,
)

# 안전한 로그인 히스토리 import
try:
    from app.api.api_v1.endpoints import simple_login_history
    SIMPLE_LOGIN_HISTORY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Simple login history not available: {e}")
    SIMPLE_LOGIN_HISTORY_AVAILABLE = False


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
api_router.include_router(member_codes.router, prefix="/codes", tags=["member_codes"])
api_router.include_router(member_numbers.router, prefix="/members", tags=["member_numbers"])
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
    system_announcements.router, prefix="/system-announcements", tags=["system_announcements"]
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
api_router.include_router(church_data.router, prefix="/church-data", tags=["church_data"])
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
api_router.include_router(
    sermon_materials.router, prefix="/sermon-materials", tags=["sermon_materials"]
)
api_router.include_router(
    smart_assistant.router, prefix="/smart-assistant", tags=["smart_assistant"]
)

# 커뮤니티 신청 라우터
api_router.include_router(
    community_applications.router, prefix="/community", tags=["community_applications"]
)

# 커뮤니티 홈 라우터
api_router.include_router(
    community_home.router, prefix="/community", tags=["community_home"]
)

# 커뮤니티 나눔 라우터
api_router.include_router(
    community_sharing.router, prefix="/community", tags=["community_sharing"]
)

# 커뮤니티 요청 라우터
api_router.include_router(
    community_request.router, prefix="/community", tags=["community_request"]
)

# 구인/구직 라우터
api_router.include_router(
    job_posts.router, prefix="/community", tags=["job_posts"]
)

# 음악팀 모집 라우터
api_router.include_router(
    music_requests.router, prefix="/community", tags=["music_requests"]
)

# 안전한 로그인 히스토리 라우터 등록
if SIMPLE_LOGIN_HISTORY_AVAILABLE:
    api_router.include_router(
        simple_login_history.router, prefix="/auth/login-history", tags=["login_history"]
    )
    print("✅ Simple login history routes registered")
else:
    print("⚠️ Simple login history routes skipped")
