from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.activity_log import ActionType, ResourceType


class ActivityLogCreate(BaseModel):
    """Schema for creating an activity log entry"""
    user_id: str = Field(..., max_length=50)
    session_id: str = Field(..., max_length=100)
    timestamp: Optional[datetime] = None
    action: ActionType
    resource: ResourceType
    target_id: Optional[str] = Field(None, max_length=50)
    target_name: Optional[str] = Field(None, max_length=100)
    page_path: str = Field(..., max_length=200)
    page_name: str = Field(..., max_length=100)
    details: Optional[Dict[str, Any]] = None
    sensitive_data: Optional[List[str]] = None
    # IP and User-Agent will be set by server, not client
    
    @validator('sensitive_data')
    def validate_sensitive_data(cls, v):
        if v is not None and not isinstance(v, list):
            raise ValueError('sensitive_data must be a list of field names')
        return v


class ActivityLogBatch(BaseModel):
    """Schema for batch creating activity logs"""
    logs: List[ActivityLogCreate] = Field(..., min_items=1, max_items=100)


class ActivityLogResponse(BaseModel):
    """Schema for activity log response"""
    id: int
    user_id: str
    session_id: str
    timestamp: datetime
    action: str
    resource: str
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    page_path: str
    page_name: str
    details: Optional[Dict[str, Any]] = None
    sensitive_data: Optional[List[str]] = None
    ip_address: str
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityLogSummary(BaseModel):
    """Schema for activity log summary (for admin list view)"""
    id: int
    user_id: str
    timestamp: datetime
    action: str
    resource: str
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    page_name: str
    ip_address: str
    sensitive_data_count: int = 0

    class Config:
        from_attributes = True


class ActivityLogQuery(BaseModel):
    """Schema for activity log query parameters"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=200)
    user_id: Optional[str] = None
    action: Optional[ActionType] = None
    resource: Optional[ResourceType] = None
    start_date: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')
    search: Optional[str] = None
    ip_address: Optional[str] = None


class ActivityLogStats(BaseModel):
    """Schema for activity log statistics"""
    total_logs: int = 0
    today_logs: int = 0
    week_logs: int = 0
    month_logs: int = 0
    action_breakdown: Dict[str, int] = {}
    resource_breakdown: Dict[str, int] = {}
    top_users: List[Dict[str, Union[str, int]]] = []
    sensitive_data_access_count: int = 0


class ActivityLogCreateResponse(BaseModel):
    """Schema for activity log creation response"""
    success: bool = True
    message: str = "활동 로그가 성공적으로 저장되었습니다"
    inserted_count: int
    timestamp: datetime
    
    
class ActivityLogErrorResponse(BaseModel):
    """Schema for activity log error response"""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ActivityLogListResponse(BaseModel):
    """Schema for activity log list response"""
    success: bool = True
    data: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "logs": [
                        {
                            "id": 84,
                            "user_id": "admin123",
                            "timestamp": "2025-09-06T15:30:45.123Z",
                            "action": "view",
                            "resource": "member",
                            "target_id": "12345",
                            "target_name": "홍길동",
                            "page_name": "교인 상세조회",
                            "ip_address": "192.168.1.100",
                            "sensitive_data_count": 5
                        }
                    ],
                    "pagination": {
                        "total_count": 1247,
                        "page": 1,
                        "limit": 50,
                        "total_pages": 25
                    }
                }
            }
        }


# Export activity log utility functions for consistent logging
class ActivityLogHelper:
    @staticmethod
    def create_member_view_log(user_id: str, session_id: str, member_id: str, 
                              member_name: str, accessed_fields: List[str]) -> ActivityLogCreate:
        """Helper to create a member view log"""
        return ActivityLogCreate(
            user_id=user_id,
            session_id=session_id,
            action=ActionType.VIEW,
            resource=ResourceType.MEMBER,
            target_id=member_id,
            target_name=member_name,
            page_path="/member-management",
            page_name="교인 상세조회",
            details={
                "accessed_fields": accessed_fields,
                "view_type": "detail_modal"
            },
            sensitive_data=accessed_fields
        )
    
    @staticmethod
    def create_member_update_log(user_id: str, session_id: str, member_id: str, 
                                member_name: str, updated_fields: List[str], 
                                old_values: Dict[str, Any] = None) -> ActivityLogCreate:
        """Helper to create a member update log"""
        details = {
            "updated_fields": updated_fields,
            "update_type": "form_edit"
        }
        if old_values:
            details["old_values"] = old_values
            
        return ActivityLogCreate(
            user_id=user_id,
            session_id=session_id,
            action=ActionType.UPDATE,
            resource=ResourceType.MEMBER,
            target_id=member_id,
            target_name=member_name,
            page_path="/member-management/edit",
            page_name="교인 정보 수정",
            details=details,
            sensitive_data=updated_fields
        )