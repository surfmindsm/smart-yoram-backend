"""
커뮤니티 관련 공통 Enum 정의
"""
import enum


class CommunityStatus(str, enum.Enum):
    """통일된 커뮤니티 상태값"""
    ACTIVE = "active"        # 활성/모집중/진행중/진행 중
    COMPLETED = "completed"  # 완료/마감/성사/끝남
    CANCELLED = "cancelled"  # 취소/중단
    PAUSED = "paused"       # 일시중지/보류


class ContactMethod(str, enum.Enum):
    """연락 방법"""
    PHONE = "phone"
    EMAIL = "email"
    BOTH = "both"
    OTHER = "other"


class UrgencyLevel(str, enum.Enum):
    """긴급도"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CommunityCategory(str, enum.Enum):
    """공통 카테고리"""
    ELECTRONICS = "가전제품"
    FURNITURE = "가구"
    CLOTHING = "의류"
    BOOKS = "도서"
    FOOD = "식품"
    SPORTS = "스포츠용품"
    TOYS = "장난감"
    BEAUTY = "화장품"
    OTHER = "기타"


# 상태값 매핑 헬퍼 함수들
def map_sharing_status(old_status: str) -> str:
    """무료 나눔 상태값을 통일된 상태값으로 매핑"""
    mapping = {
        "available": CommunityStatus.ACTIVE,
        "reserved": CommunityStatus.ACTIVE,  # 예약됨도 활성으로 간주
        "completed": CommunityStatus.COMPLETED
    }
    return mapping.get(old_status, CommunityStatus.ACTIVE)


def map_request_status(old_status: str) -> str:
    """물품 요청 상태값을 통일된 상태값으로 매핑"""
    mapping = {
        "active": CommunityStatus.ACTIVE,
        "fulfilled": CommunityStatus.COMPLETED,
        "cancelled": CommunityStatus.CANCELLED
    }
    return mapping.get(old_status, CommunityStatus.ACTIVE)


def map_job_status(old_status: str) -> str:
    """구인/구직 상태값을 통일된 상태값으로 매핑"""
    mapping = {
        "open": CommunityStatus.ACTIVE,
        "active": CommunityStatus.ACTIVE,
        "closed": CommunityStatus.COMPLETED,
        "filled": CommunityStatus.COMPLETED
    }
    return mapping.get(old_status, CommunityStatus.ACTIVE)


def map_event_status(old_status: str) -> str:
    """교회 행사 상태값을 통일된 상태값으로 매핑"""
    mapping = {
        "upcoming": CommunityStatus.ACTIVE,
        "ongoing": CommunityStatus.ACTIVE,
        "completed": CommunityStatus.COMPLETED,
        "cancelled": CommunityStatus.CANCELLED
    }
    return mapping.get(old_status, CommunityStatus.ACTIVE)


def get_status_label(status: str) -> str:
    """상태값에 대한 한국어 라벨 반환"""
    labels = {
        CommunityStatus.ACTIVE: "활성",
        CommunityStatus.COMPLETED: "완료",
        CommunityStatus.CANCELLED: "취소",
        CommunityStatus.PAUSED: "일시중지"
    }
    return labels.get(status, "알 수 없음")