from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class LoginHistoryCreate(BaseModel):
    """로그인 기록 생성용 스키마 - 매우 단순함"""
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = "success"  # success, failed
    device_type: Optional[str] = None
    location: Optional[str] = None


class LoginHistoryResponse(BaseModel):
    """로그인 기록 응답용 스키마"""
    id: int
    user_id: int
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    device_type: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LoginHistoryRecent(BaseModel):
    """최근 로그인 정보 (헤더용)"""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None
    location: Optional[str] = "위치 정보 없음"

    class Config:
        from_attributes = True


class LoginHistoryList(BaseModel):
    """로그인 기록 목록 응답"""
    records: List[LoginHistoryResponse]
    pagination: dict

    class Config:
        schema_extra = {
            "example": {
                "records": [
                    {
                        "id": 123,
                        "user_id": 1,
                        "timestamp": "2025-09-07T10:30:00Z",
                        "ip_address": "192.168.1.100",
                        "user_agent": "Mozilla/5.0...",
                        "status": "success",
                        "device_type": "desktop"
                    }
                ],
                "pagination": {
                    "total": 150,
                    "page": 1,
                    "limit": 20,
                    "total_pages": 8
                }
            }
        }