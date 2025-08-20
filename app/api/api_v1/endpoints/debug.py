from typing import Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import logging

from app import models
from app.api import deps

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/test-auth")
def test_authentication(
    request: Request,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Test authentication - returns current user info if authenticated.
    """
    logger.info(f"Test auth endpoint called by user {current_user.id}")

    # Log headers for debugging
    auth_header = request.headers.get("Authorization")
    logger.debug(
        f"Authorization header: {auth_header[:50] if auth_header else 'None'}..."
    )

    return {
        "success": True,
        "message": "Authentication successful",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "church_id": current_user.church_id,
            "role": current_user.role,
            "is_active": current_user.is_active,
        },
    }


@router.post("/test-request-body")
def test_request_body(
    data: dict,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Test request body parsing - echoes back the received data.
    """
    logger.info(f"Test request body endpoint called by user {current_user.id}")
    logger.debug(f"Received data: {data}")

    return {
        "success": True,
        "message": "Request body received",
        "received_data": data,
        "data_type": {key: type(value).__name__ for key, value in data.items()},
    }


@router.get("/test-no-auth")
def test_no_auth() -> Any:
    """
    Test endpoint without authentication - should always work.
    """
    logger.info("Test no-auth endpoint called")

    return {
        "success": True,
        "message": "This endpoint works without authentication",
        "info": "If you can see this but not authenticated endpoints, the issue is with JWT",
    }
