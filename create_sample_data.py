#!/usr/bin/env python
"""Create sample data for testing."""

from datetime import datetime, date, timedelta
from app.db.session import SessionLocal
from app import models
from app.core.security import get_password_hash

def create_sample_data():
    db = SessionLocal()
    
    try:
        # Create a sample church
        church = models.Church(
            name="은혜로운 교회",
            address="서울시 강남구 역삼동 123-45",
            phone="02-1234-5678",
            email="info@gracechurch.kr",
            pastor_name="김은혜 목사",
            subscription_status="active",
            subscription_end_date=datetime.now() + timedelta(days=365),
            member_limit=500
        )
        db.add(church)
        db.commit()
        db.refresh(church)
        print(f"Created church: {church.name}")
        
        # Update admin user with church
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if admin:
            admin.church_id = church.id
            db.commit()
            print("Updated admin user with church")
        
        # Create sample members
        members_data = [
            {"name": "홍길동", "position": "elder", "department": "예배부", "phone": "010-1111-2222"},
            {"name": "김성도", "position": "deacon", "department": "찬양부", "phone": "010-2222-3333"},
            {"name": "이믿음", "position": "member", "department": "청년부", "phone": "010-3333-4444"},
            {"name": "박사랑", "position": "member", "department": "교육부", "phone": "010-4444-5555"},
            {"name": "최은혜", "position": "deacon", "department": "봉사부", "phone": "010-5555-6666"},
            {"name": "정평강", "position": "member", "department": "청년부", "phone": "010-6666-7777"},
            {"name": "강희망", "position": "member", "department": "교육부", "phone": "010-7777-8888"},
            {"name": "조기쁨", "position": "elder", "department": "예배부", "phone": "010-8888-9999"},
        ]
        
        members = []
        for data in members_data:
            member = models.Member(
                church_id=church.id,
                name=data["name"],
                position=data["position"],
                department=data["department"],
                phone=data["phone"],
                email=f"{data['name']}@example.com",
                gender="M" if data["name"][0] in ["홍", "김", "박", "정", "조"] else "F",
                status="active",
                registration_date=date.today() - timedelta(days=365)
            )
            db.add(member)
            members.append(member)
        
        db.commit()
        print(f"Created {len(members)} members")
        
        # Create sample attendance records for today
        today = date.today()
        for i, member in enumerate(members):
            if i % 3 != 2:  # 2/3 attendance rate
                attendance = models.Attendance(
                    church_id=church.id,
                    member_id=member.id,
                    service_date=today,
                    service_type="sunday_morning",
                    present=True,
                    check_in_time=datetime.now(),
                    check_in_method="manual"
                )
                db.add(attendance)
        
        db.commit()
        print("Created attendance records")
        
        # Create sample bulletins
        bulletins_data = [
            {
                "title": "2025년 1월 둘째주 주보",
                "date": today,
                "content": "이번 주 말씀: 사랑으로 하나되는 교회\n예배 순서: 찬양 - 기도 - 말씀 - 봉헌"
            },
            {
                "title": "2025년 1월 첫째주 주보", 
                "date": today - timedelta(days=7),
                "content": "새해 감사예배\n특별 찬양: 성가대"
            }
        ]
        
        for data in bulletins_data:
            bulletin = models.Bulletin(
                church_id=church.id,
                title=data["title"],
                date=data["date"],
                content=data["content"],
                created_by=admin.id if admin else None
            )
            db.add(bulletin)
        
        db.commit()
        print("Created bulletins")
        
        print("\n✅ Sample data created successfully!")
        print("\nYou can now login to the admin dashboard and see:")
        print("- Church information")
        print("- 8 sample members")
        print("- Attendance records")
        print("- 2 sample bulletins")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()