from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, validator


class SermonMaterialBase(BaseModel):
    """설교 자료 기본 스키마"""

    title: str
    author: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    scripture_reference: Optional[str] = None
    date_preached: Optional[date] = None
    tags: List[str] = []
    is_public: bool = False
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class SermonMaterialCreate(SermonMaterialBase):
    """설교 자료 생성 스키마"""

    pass


class SermonMaterialUpdate(BaseModel):
    """설교 자료 수정 스키마"""

    title: Optional[str] = None
    author: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    scripture_reference: Optional[str] = None
    date_preached: Optional[date] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class SermonMaterialResponse(SermonMaterialBase):
    """설교 자료 응답 스키마"""

    id: int
    church_id: int
    user_id: int
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    view_count: int = 0
    download_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SermonMaterialListResponse(BaseModel):
    """설교 자료 목록 응답 스키마"""

    items: List[SermonMaterialResponse]
    total: int
    page: int
    size: int
    pages: int


class FileUploadResponse(BaseModel):
    """파일 업로드 응답 스키마"""

    success: bool
    file_url: str
    file_type: str
    file_size: int
    filename: str


class SermonCategoryBase(BaseModel):
    """설교 카테고리 기본 스키마"""

    name: str
    description: Optional[str] = None
    color: str = "#3B82F6"
    order_index: int = 0


class SermonCategoryCreate(SermonCategoryBase):
    """설교 카테고리 생성 스키마"""

    pass


class SermonCategoryUpdate(BaseModel):
    """설교 카테고리 수정 스키마"""

    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class SermonCategoryResponse(SermonCategoryBase):
    """설교 카테고리 응답 스키마"""

    id: int
    church_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SermonSearchRequest(BaseModel):
    """설교 자료 검색 요청 스키마"""

    q: Optional[str] = None  # 검색어
    category: Optional[str] = None  # 카테고리 필터
    author: Optional[str] = None  # 설교자 필터
    date_from: Optional[date] = None  # 설교 날짜 시작
    date_to: Optional[date] = None  # 설교 날짜 끝
    tags: Optional[List[str]] = None  # 태그 필터
    is_public: Optional[bool] = None  # 공개/비공개 필터
    file_type: Optional[str] = None  # 파일 타입 필터


class SermonStatsResponse(BaseModel):
    """설교 자료 통계 응답 스키마"""

    total_materials: int
    public_materials: int
    private_materials: int
    total_downloads: int
    total_views: int
    categories_count: int
    most_downloaded: Optional[SermonMaterialResponse] = None
    most_viewed: Optional[SermonMaterialResponse] = None
    recent_materials: List[SermonMaterialResponse] = []
