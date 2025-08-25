#!/usr/bin/env python3
"""
Create sample announcement data
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import models


def create_sample_announcements():
    db = SessionLocal()
    try:
        # Get first church and admin user
        church = db.query(models.Church).first()
        if not church:
            print("No church found. Please run create_sample_data.py first.")
            return

        admin_user = (
            db.query(models.User)
            .filter(models.User.church_id == church.id, models.User.role == "admin")
            .first()
        )

        minister_user = (
            db.query(models.User)
            .filter(models.User.church_id == church.id, models.User.role == "minister")
            .first()
        )

        if not admin_user:
            print("No admin user found.")
            return

        # Sample announcements
        announcements = [
            {
                "title": "2025년 신년 예배 안내",
                "content": """새해를 맞이하여 신년 예배를 드립니다.
                
일시: 2025년 1월 1일(수) 오전 10시
장소: 본당

모든 성도님들의 많은 참석 부탁드립니다.
새해에도 주님의 은혜가 가득하시길 기도합니다.""",
                "author_id": admin_user.id,
                "author_name": admin_user.full_name or admin_user.username,
                "is_pinned": True,
                "created_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "title": "주일학교 겨울 성경학교 등록 안내",
                "content": """2025년 겨울 성경학교 등록을 받습니다.

기간: 2025년 1월 6일(월) ~ 1월 8일(수)
대상: 유치부 ~ 고등부
등록비: 30,000원
등록 마감: 12월 29일(주일)

문의: 교육부서 각 부서장""",
                "author_id": minister_user.id if minister_user else admin_user.id,
                "author_name": (
                    minister_user.full_name if minister_user else admin_user.full_name
                ),
                "target_audience": "youth",
                "created_at": datetime.utcnow() - timedelta(days=3),
            },
            {
                "title": "2024년 성탄절 예배 및 행사 안내",
                "content": """성탄절을 맞이하여 다음과 같이 예배와 행사가 있습니다.

12월 24일(화) 성탄 전야 예배
- 저녁 7시 30분, 본당
- 성탄 칸타타 및 촛불 예배

12월 25일(수) 성탄절 예배
- 오전 10시, 본당
- 성탄 축하 예배 및 성례식

모든 성도님들과 함께 아기 예수님의 탄생을 축하하며 기뻐하는 시간이 되길 소망합니다.""",
                "author_id": admin_user.id,
                "author_name": admin_user.full_name or admin_user.username,
                "created_at": datetime.utcnow() - timedelta(days=7),
            },
            {
                "title": "교회 주차장 이용 안내",
                "content": """주일 예배시 주차장 이용에 대해 안내드립니다.

1. 교회 주차장은 선착순으로 이용 가능합니다.
2. 장애인 주차구역은 장애인 차량만 주차 가능합니다.
3. 이중 주차시 연락처를 반드시 남겨주세요.
4. 인근 공영주차장도 이용 가능합니다 (도보 5분).

서로 배려하는 마음으로 주차해 주시기 바랍니다.""",
                "author_id": admin_user.id,
                "author_name": admin_user.full_name or admin_user.username,
                "created_at": datetime.utcnow() - timedelta(days=14),
            },
            {
                "title": "구역 모임 변경 안내",
                "content": """12월 구역 모임 일정이 변경되었습니다.

변경 전: 12월 둘째 주
변경 후: 12월 셋째 주

성탄절 준비 관계로 일정이 변경되었으니 각 구역장님들은 구역원들에게 전달 부탁드립니다.""",
                "author_id": minister_user.id if minister_user else admin_user.id,
                "author_name": (
                    minister_user.full_name if minister_user else admin_user.full_name
                ),
                "created_at": datetime.utcnow() - timedelta(days=20),
            },
            {
                "title": "교회 앱 사용 안내",
                "content": """스마트 요람 앱이 출시되었습니다!

주요 기능:
- 교인 정보 조회
- 출석 체크 (QR 코드)
- 주보 확인
- 교회 일정 확인
- 헌금 내역 조회

앱스토어 또는 구글 플레이에서 '스마트요람'을 검색하여 다운로드 받으실 수 있습니다.

사용 중 문의사항은 교회 사무실로 연락주세요.""",
                "author_id": admin_user.id,
                "author_name": admin_user.full_name or admin_user.username,
                "is_pinned": True,
                "created_at": datetime.utcnow() - timedelta(days=30),
            },
            {
                "title": "2024년 추수감사절 예배",
                "content": """추수감사절을 맞이하여 한 해 동안 베풀어주신 하나님의 은혜에 감사드리는 예배를 드립니다.

일시: 11월 17일(주일) 오전 11시
장소: 본당

감사헌금 봉투는 예배실 입구에 비치되어 있습니다.""",
                "author_id": admin_user.id,
                "author_name": admin_user.full_name or admin_user.username,
                "is_active": False,  # 지난 공지
                "created_at": datetime.utcnow() - timedelta(days=45),
            },
        ]

        # Create announcements
        for announcement_data in announcements:
            announcement = models.Announcement(church_id=church.id, **announcement_data)
            db.add(announcement)

        db.commit()
        print(f"Created {len(announcements)} sample announcements for {church.name}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_announcements()
