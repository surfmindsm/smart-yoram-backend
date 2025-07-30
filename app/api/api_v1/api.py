from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth,
    users,
    members,
    churches,
    attendances,
    bulletins,
)


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(churches.router, prefix="/churches", tags=["churches"])
api_router.include_router(
    attendances.router, prefix="/attendances", tags=["attendances"]
)
api_router.include_router(bulletins.router, prefix="/bulletins", tags=["bulletins"])
