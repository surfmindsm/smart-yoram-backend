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
)


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(auth_member.router, prefix="/auth/member", tags=["auth_member"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(member_photos.router, prefix="/members", tags=["member_photos"])
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
api_router.include_router(member_card.router, prefix="/member-card", tags=["member_card"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["announcements"])
