"""
Announcement category definitions
"""

ANNOUNCEMENT_CATEGORIES = {
    "worship": {
        "label": "예배/모임",
        "description": "예배, 각종 모임, 주요 일정",
        "subcategories": {
            "sunday_worship": "주일예배",
            "wednesday_worship": "수요예배",
            "dawn_prayer": "새벽기도",
            "special_worship": "특별예배",
            "group_meeting": "구역/속회 모임",
            "committee_meeting": "위원회 모임",
            "schedule": "주요 일정",
        },
    },
    "member_news": {
        "label": "교우 소식",
        "description": "부고, 결혼, 출산, 이사, 입원 등",
        "subcategories": {
            "obituary": "부고",
            "wedding": "결혼",
            "birth": "출산",
            "relocation": "이사",
            "hospitalization": "입원",
            "celebration": "축하",
            "other": "기타",
        },
    },
    "event": {
        "label": "행사/공지",
        "description": "행사, 봉사, 알림, 일반 공지",
        "subcategories": {
            "church_event": "교회 행사",
            "volunteer": "봉사 활동",
            "education": "교육/세미나",
            "registration": "등록/신청",
            "facility": "시설 관련",
            "notice": "일반 공지",
            "emergency": "긴급 공지",
        },
    },
}


def get_categories():
    """Get all announcement categories"""
    return ANNOUNCEMENT_CATEGORIES


def get_category_choices():
    """Get category choices for validation"""
    return list(ANNOUNCEMENT_CATEGORIES.keys())


def get_subcategory_choices(category: str):
    """Get subcategory choices for a specific category"""
    if category in ANNOUNCEMENT_CATEGORIES:
        return list(ANNOUNCEMENT_CATEGORIES[category]["subcategories"].keys())
    return []


def validate_category(category: str, subcategory: str = None) -> bool:
    """Validate category and subcategory combination"""
    if category not in ANNOUNCEMENT_CATEGORIES:
        return False

    if subcategory:
        return subcategory in ANNOUNCEMENT_CATEGORIES[category]["subcategories"]

    return True
