from pydantic import BaseModel
from datetime import time, datetime
from typing import Optional, List


class WorshipServiceBase(BaseModel):
    name: str
    location: Optional[str] = None
    day_of_week: Optional[int] = None
    start_time: time
    end_time: Optional[time] = None
    service_type: Optional[str] = None
    target_group: Optional[str] = None
    is_online: bool = False
    is_active: bool = True
    order_index: int = 0


class WorshipServiceCreate(WorshipServiceBase):
    pass


class WorshipServiceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    day_of_week: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    service_type: Optional[str] = None
    target_group: Optional[str] = None
    is_online: Optional[bool] = None
    is_active: Optional[bool] = None
    order_index: Optional[int] = None


class WorshipService(WorshipServiceBase):
    id: int
    church_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorshipServiceCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    order_index: int = 0


class WorshipServiceCategoryCreate(WorshipServiceCategoryBase):
    pass


class WorshipServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


class WorshipServiceCategory(WorshipServiceCategoryBase):
    id: int
    church_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorshipScheduleResponse(BaseModel):
    """교회 전체 예배 스케줄 응답"""

    categories: List[WorshipServiceCategory]
    services: List[WorshipService]

    class Config:
        from_attributes = True
