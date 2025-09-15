import enum
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CommonStatus(str, enum.Enum):
    """커뮤니티 API 통일 상태 값"""
    ACTIVE = "active"        # 활성/모집중/진행중
    COMPLETED = "completed"  # 완료/마감  
    CANCELLED = "cancelled"  # 취소
    PAUSED = "paused"       # 일시중지 (필요시)


class ContactMethod(str, enum.Enum):
    """연락 방법 통일"""
    PHONE = "phone"
    EMAIL = "email"
    KAKAO = "kakao"
    SMS = "sms"


class CommunityBaseMixin:
    """커뮤니티 API 공통 필드 Mixin"""
    
    # 교회/작성자 정보
    church_id = Column(Integer, nullable=False, default=9998, comment="교회 ID (9998=커뮤니티)")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="작성자 ID")
    
    # 통계 정보
    view_count = Column(Integer, default=0, comment="조회수")
    likes = Column(Integer, default=0, comment="좋아요수")
    
    # 상태
    status = Column(Enum(CommonStatus), default=CommonStatus.ACTIVE, comment="상태")
    
    # 시간 정보 (표준화됨)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정일")
    
    # 관계 (동적으로 설정됨)
    @property
    def author_relationship(self):
        """작성자 관계 - 하위 클래스에서 author = relationship("User", foreign_keys=[author_id])로 설정"""
        return relationship("User", foreign_keys=[self.author_id])


class ContactFieldsMixin:
    """연락처 필드 Mixin (분리된 필드 패턴)"""
    
    contact_phone = Column(String(20), nullable=True, comment="연락처 전화번호")
    contact_email = Column(String(100), nullable=True, comment="연락처 이메일")


class CommunityResponseMixin:
    """커뮤니티 API 응답 공통 필드 (프로퍼티)"""
    
    @property 
    def author_name(self):
        """작성자 이름 (author relationship 활용)"""
        return self.author.full_name if self.author else "익명"
    
    @property
    def church_name(self):
        """교회 이름 (기본값)"""
        return f"교회 {self.church_id}" if self.church_id != 9998 else "커뮤니티"


# 공통 헬퍼 함수들
def build_community_list_response(items, page, limit, total_count):
    """커뮤니티 API 표준 목록 응답 구조 생성"""
    total_pages = (total_count + limit - 1) // limit
    
    return {
        "success": True,
        "data": items,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "per_page": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


def build_community_success_response(message, data=None):
    """커뮤니티 API 표준 성공 응답 구조 생성"""
    response = {
        "success": True,
        "message": message
    }
    if data:
        response["data"] = data
    return response


def build_community_error_response(message, data=None):
    """커뮤니티 API 표준 에러 응답 구조 생성"""
    response = {
        "success": False,
        "message": message
    }
    if data:
        response["data"] = data
    return response


def build_standard_filters_query(query_sql, params, filters):
    """표준 필터 쿼리 빌더"""
    filter_mappings = {
        'status': 'status = :status',
        'category': 'category = :category',
        'location': 'location ILIKE :location',
        'search': '(title ILIKE :search OR description ILIKE :search)'
    }
    
    for filter_key, filter_value in filters.items():
        if filter_value and filter_value != 'all':
            if filter_key in filter_mappings:
                query_sql += f" AND {filter_mappings[filter_key]}"
                if filter_key in ['location', 'search']:
                    params[filter_key] = f"%{filter_value}%"
                else:
                    params[filter_key] = filter_value
    
    return query_sql, params


def format_community_item_response(row, field_mapping, author_names=None):
    """커뮤니티 아이템 응답 데이터 포매팅 (SQL raw 결과용)"""
    import json
    
    data_item = {}
    
    # 기본 필드 매핑
    for response_key, row_index in field_mapping.items():
        value = row[row_index] if row_index < len(row) else None
        
        # JSON 필드 파싱
        if response_key in ['images', 'instruments_needed', 'preferred_location', 'available_days']:
            if value:
                try:
                    data_item[response_key] = json.loads(value) if isinstance(value, str) else value
                except:
                    data_item[response_key] = []
            else:
                data_item[response_key] = []
        # 날짜 필드 포매팅
        elif response_key in ['created_at', 'updated_at']:
            data_item[response_key] = value.isoformat() if value else None
        # 기본값 처리
        else:
            data_item[response_key] = value
    
    # 작성자 이름 추가 (author_names 딕셔너리 활용)
    if 'author_id' in data_item and author_names:
        data_item['author_name'] = author_names.get(data_item['author_id'], "익명")
    
    return data_item