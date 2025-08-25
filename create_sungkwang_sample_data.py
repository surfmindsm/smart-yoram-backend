#!/usr/bin/env python3
"""
성광교회 샘플 데이터 생성 스크립트
"""

import os
import sys
from datetime import datetime, timedelta, date
import random
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.church import Church
from app.models.user import User
from app.models.member import Member
from app.models.attendance import Attendance
from app.models.bulletin import Bulletin
from app.core.security import get_password_hash
from app.db.base import Base


def create_sample_data():
    """성광교회 샘플 데이터 생성"""

    # 데이터베이스 세션
    db = SessionLocal()

    try:
        # 1. 기존 데이터 삭제 (개발 환경에서만)
        print("기존 데이터 삭제 중...")
        db.query(Attendance).delete()
        db.query(Bulletin).delete()
        db.query(Member).delete()
        db.query(User).delete()
        db.query(Church).delete()
        db.commit()

        # 2. 교회 생성
        print("성광교회 생성 중...")
        church = Church(
            name="성광교회",
            address="경기도 구리시 검배로 136번길 32 (토평동)",
            phone="031-563-5210",
            email="helpsk21church@gmail.com",
            pastor_name="담임목사",
        )
        db.add(church)
        db.commit()
        db.refresh(church)

        # 3. 관리자 계정 생성
        print("관리자 계정 생성 중...")
        admin_user = User(
            username="admin",
            email="admin@sungkwang21.org",
            full_name="관리자",
            hashed_password=get_password_hash("sungkwang2025"),
            is_active=True,
            is_superuser=True,
            church_id=church.id,
        )
        db.add(admin_user)

        # 교역자 계정
        pastor_user = User(
            username="pastor",
            email="pastor@sungkwang21.org",
            full_name="담임목사",
            hashed_password=get_password_hash("sungkwang2025"),
            is_active=True,
            is_superuser=False,
            church_id=church.id,
        )
        db.add(pastor_user)

        # 일반 사용자
        user1 = User(
            username="teacher1",
            email="teacher1@sungkwang21.org",
            full_name="김선생",
            hashed_password=get_password_hash("sungkwang2025"),
            is_active=True,
            is_superuser=False,
            church_id=church.id,
        )
        db.add(user1)

        db.commit()

        # 4. 교인 정보 생성
        print("교인 정보 생성 중...")

        # 성인부
        adult_members = [
            {
                "name": "김성도",
                "phone": "010-1234-5678",
                "birth_date": "1970-03-15",
                "gender": "M",
                "position": "성도",
            },
            {
                "name": "이은혜",
                "phone": "010-2345-6789",
                "birth_date": "1975-07-22",
                "gender": "F",
                "position": "성도",
            },
            {
                "name": "박믿음",
                "phone": "010-3456-7890",
                "birth_date": "1980-11-08",
                "gender": "M",
                "position": "집사",
            },
            {
                "name": "최사랑",
                "phone": "010-4567-8901",
                "birth_date": "1978-05-30",
                "gender": "F",
                "position": "집사",
            },
            {
                "name": "정평강",
                "phone": "010-5678-9012",
                "birth_date": "1965-09-12",
                "gender": "M",
                "position": "장로",
            },
            {
                "name": "강소망",
                "phone": "010-6789-0123",
                "birth_date": "1972-12-25",
                "gender": "F",
                "position": "권사",
            },
            {
                "name": "윤기쁨",
                "phone": "010-7890-1234",
                "birth_date": "1985-04-18",
                "gender": "M",
                "position": "성도",
            },
            {
                "name": "임온유",
                "phone": "010-8901-2345",
                "birth_date": "1988-08-07",
                "gender": "F",
                "position": "성도",
            },
            {
                "name": "한충성",
                "phone": "010-9012-3456",
                "birth_date": "1960-02-28",
                "gender": "M",
                "position": "장로",
            },
            {
                "name": "오인내",
                "phone": "010-0123-4567",
                "birth_date": "1968-06-14",
                "gender": "F",
                "position": "권사",
            },
        ]

        # 청년부
        youth_members = [
            {
                "name": "김청년",
                "phone": "010-1111-2222",
                "birth_date": "1995-03-20",
                "gender": "M",
                "position": "청년",
            },
            {
                "name": "이소망",
                "phone": "010-2222-3333",
                "birth_date": "1998-07-15",
                "gender": "F",
                "position": "청년",
            },
            {
                "name": "박은혜",
                "phone": "010-3333-4444",
                "birth_date": "1997-11-30",
                "gender": "F",
                "position": "청년",
            },
            {
                "name": "최믿음",
                "phone": "010-4444-5555",
                "birth_date": "1996-05-25",
                "gender": "M",
                "position": "청년",
            },
            {
                "name": "정사랑",
                "phone": "010-5555-6666",
                "birth_date": "1999-09-10",
                "gender": "F",
                "position": "청년",
            },
        ]

        # 중고등부
        student_members = [
            {
                "name": "김학생",
                "phone": "010-6666-7777",
                "birth_date": "2007-03-15",
                "gender": "M",
                "position": "학생",
            },
            {
                "name": "이중등",
                "phone": "010-7777-8888",
                "birth_date": "2008-07-22",
                "gender": "F",
                "position": "학생",
            },
            {
                "name": "박고등",
                "phone": "010-8888-9999",
                "birth_date": "2006-11-08",
                "gender": "M",
                "position": "학생",
            },
            {
                "name": "최학생",
                "phone": "010-9999-0000",
                "birth_date": "2009-05-30",
                "gender": "F",
                "position": "학생",
            },
        ]

        # 교인 데이터베이스에 추가
        all_members = []

        for member_data in adult_members:
            member = Member(
                church_id=church.id,
                name=member_data["name"],
                phone=member_data["phone"],
                birthdate=datetime.strptime(
                    member_data["birth_date"], "%Y-%m-%d"
                ).date(),
                gender=member_data["gender"],
                position=member_data["position"],
                address=f"구리시 토평동 {random.randint(100, 999)}번지",
                email=f"{member_data['name']}@example.com",
                baptism_date=(
                    datetime.strptime(member_data["birth_date"], "%Y-%m-%d").date()
                    + timedelta(days=365 * 20)
                    if random.random() > 0.3
                    else None
                ),
                status="active",
            )
            db.add(member)
            all_members.append(member)

        for member_data in youth_members:
            member = Member(
                church_id=church.id,
                name=member_data["name"],
                phone=member_data["phone"],
                birthdate=datetime.strptime(
                    member_data["birth_date"], "%Y-%m-%d"
                ).date(),
                gender=member_data["gender"],
                position=member_data["position"],
                address=f"구리시 토평동 {random.randint(100, 999)}번지",
                email=f"{member_data['name']}@example.com",
                baptism_date=(
                    datetime.strptime(member_data["birth_date"], "%Y-%m-%d").date()
                    + timedelta(days=365 * 5)
                    if random.random() > 0.5
                    else None
                ),
                status="active",
            )
            db.add(member)
            all_members.append(member)

        for member_data in student_members:
            member = Member(
                church_id=church.id,
                name=member_data["name"],
                phone=member_data["phone"],
                birthdate=datetime.strptime(
                    member_data["birth_date"], "%Y-%m-%d"
                ).date(),
                gender=member_data["gender"],
                position=member_data["position"],
                address=f"구리시 토평동 {random.randint(100, 999)}번지",
                email=f"{member_data['name']}@example.com",
                status="active",
            )
            db.add(member)
            all_members.append(member)

        db.commit()

        # 5. 출석 기록 생성 (최근 4주)
        print("출석 기록 생성 중...")
        today = date.today()

        for weeks_ago in range(4):
            service_date = today - timedelta(weeks=weeks_ago)

            # 주일예배
            for member in all_members:
                if random.random() > 0.15:  # 85% 출석률
                    attendance = Attendance(
                        church_id=church.id,
                        member_id=member.id,
                        service_date=service_date,
                        service_type="주일예배",
                        present=True,
                        notes="정상 출석" if random.random() > 0.1 else "지각",
                    )
                    db.add(attendance)

            # 수요예배 (성인만)
            if service_date.weekday() == 2:  # 수요일
                for member in all_members[:10]:  # 성인부만
                    if random.random() > 0.4:  # 60% 출석률
                        attendance = Attendance(
                            church_id=church.id,
                            member_id=member.id,
                            service_date=service_date,
                            service_type="수요예배",
                            present=True,
                        )
                        db.add(attendance)

        db.commit()

        # 6. 주보 생성
        print("주보 생성 중...")
        bulletins = [
            {
                "title": "2025년 1월 첫째 주 주보",
                "content": """
# 주일 예배 순서
1. 묵도
2. 찬송 - 8장 (거룩 거룩 거룩 전능하신 주님)
3. 대표기도 - 김성도 집사
4. 성경봉독 - 요한복음 3:16
5. 찬양대
6. 설교 - "하나님의 사랑" (담임목사)
7. 찬송 - 304장 (그 크신 하나님의 사랑)
8. 봉헌 및 봉헌기도
9. 광고
10. 축도

## 교회 소식
- 신년 특별 새벽기도회가 진행 중입니다
- 다음 주 성찬식이 있습니다
- 구역 모임 일정을 확인해 주세요
""",
                "date": today - timedelta(weeks=3),
            },
            {
                "title": "2025년 1월 둘째 주 주보",
                "content": """
# 주일 예배 순서
1. 묵도
2. 찬송 - 9장 (하늘에 가득 찬 영광의 하나님)
3. 대표기도 - 박믿음 집사
4. 성경봉독 - 마태복음 5:1-12
5. 찬양대
6. 설교 - "팔복의 삶" (담임목사)
7. 찬송 - 490장 (주여 지난 밤 내 꿈에)
8. 성찬식
9. 봉헌 및 봉헌기도
10. 광고
11. 축도

## 교회 소식
- 오늘 성찬식이 있습니다
- 다음 주 전교인 신년 윷놀이 대회
- 주일학교 겨울 성경학교 등록 받습니다
""",
                "date": today - timedelta(weeks=2),
            },
        ]

        for bulletin_data in bulletins:
            bulletin = Bulletin(
                church_id=church.id,
                title=bulletin_data["title"],
                content=bulletin_data["content"],
                date=bulletin_data["date"],
                created_by=admin_user.id,
            )
            db.add(bulletin)

        db.commit()

        print("\n✅ 샘플 데이터 생성 완료!")
        print(f"- 교회: {church.name}")
        print(f"- 사용자: {db.query(User).count()}명")
        print(f"- 교인: {db.query(Member).count()}명")
        print(f"- 출석기록: {db.query(Attendance).count()}개")
        print(f"- 주보: {db.query(Bulletin).count()}개")

        print("\n🔐 로그인 정보:")
        print("- 관리자: admin / sungkwang2025")
        print("- 교역자: pastor / sungkwang2025")
        print("- 교사: teacher1 / sungkwang2025")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("성광교회 샘플 데이터 생성을 시작합니다...")
    create_sample_data()
