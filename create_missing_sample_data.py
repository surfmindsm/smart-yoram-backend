#!/usr/bin/env python3
"""
Create sample data for missing data sources: attendance and worship services
"""

from datetime import datetime, timedelta, time
import random
from app.db.session import SessionLocal
from app.models.attendance import Attendance
from app.models.worship_schedule import WorshipService
from app.models.member import Member
from app.models.user import User

def create_missing_sample_data(church_id=9999):
    """Create sample data for attendance and worship services"""
    db = SessionLocal()
    
    try:
        print(f"🏛️  Creating missing sample data for church ID {church_id}...")
        
        # Get admin user and members
        admin_user = db.query(User).filter(User.church_id == church_id).first()
        members = db.query(Member).filter(Member.church_id == church_id, Member.status == "active").all()
        
        if not admin_user:
            print(f"⚠️  No admin user found for church {church_id}")
            return
            
        if not members:
            print(f"⚠️  No members found for church {church_id}")
            return
        
        print(f"👤 Using admin user: {admin_user.username}")
        print(f"👥 Found {len(members)} members")
        
        # 1. Create Worship Services
        print(f"\n📅 Creating worship services...")
        worship_services = [
            {
                "name": "주일예배 1부",
                "service_type": "주일예배", 
                "day_of_week": 6,  # Sunday
                "start_time": time(9, 0),
                "end_time": time(10, 30),
                "location": "본당",
                "target_group": "전체",
                "is_online": False
            },
            {
                "name": "주일예배 2부", 
                "service_type": "주일예배",
                "day_of_week": 6,  # Sunday
                "start_time": time(11, 0), 
                "end_time": time(12, 30),
                "location": "본당",
                "target_group": "전체",
                "is_online": True
            },
            {
                "name": "수요예배",
                "service_type": "수요예배",
                "day_of_week": 2,  # Wednesday
                "start_time": time(19, 30),
                "end_time": time(21, 0),
                "location": "소예배실",
                "target_group": "전체",
                "is_online": False
            },
            {
                "name": "새벽기도회",
                "service_type": "새벽기도회", 
                "day_of_week": None,  # Daily
                "start_time": time(5, 30),
                "end_time": time(6, 30),
                "location": "기도실",
                "target_group": "전체",
                "is_online": False
            },
            {
                "name": "청년부 모임",
                "service_type": "부서예배",
                "day_of_week": 6,  # Sunday
                "start_time": time(14, 0),
                "end_time": time(16, 0), 
                "location": "청년부실",
                "target_group": "청년",
                "is_online": False
            }
        ]
        
        created_services = []
        for service_data in worship_services:
            service = WorshipService(
                church_id=church_id,
                **service_data,
                is_active=True,
                order_index=len(created_services)
            )
            db.add(service)
            created_services.append(service)
        
        db.commit()
        print(f"✅ Created {len(created_services)} worship services")
        
        # 2. Create Attendance Records
        print(f"\n📊 Creating attendance records...")
        
        # Create attendance for the past 8 weeks
        service_types = ["sunday_morning", "sunday_evening", "wednesday", "dawn_prayer"]
        created_attendance = 0
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=8)
        
        current_date = start_date
        while current_date <= end_date:
            # Sunday services (more attendance)
            if current_date.weekday() == 6:  # Sunday
                # Morning service - 80% attendance
                morning_attendees = random.sample(members, k=int(len(members) * 0.8))
                for member in morning_attendees:
                    attendance = Attendance(
                        church_id=church_id,
                        member_id=member.id,
                        service_date=current_date,
                        service_type="sunday_morning",
                        present=True,
                        check_in_time=datetime.combine(current_date, time(8, 50 + random.randint(0, 9))),
                        check_in_method="manual"
                    )
                    db.add(attendance)
                    created_attendance += 1
                
                # Evening service - 40% attendance
                evening_attendees = random.sample(members, k=int(len(members) * 0.4))
                for member in evening_attendees:
                    attendance = Attendance(
                        church_id=church_id,
                        member_id=member.id,
                        service_date=current_date,
                        service_type="sunday_evening", 
                        present=True,
                        check_in_time=datetime.combine(current_date, time(10, 50 + random.randint(0, 9))),
                        check_in_method="qr_code"
                    )
                    db.add(attendance)
                    created_attendance += 1
            
            # Wednesday service (30% attendance)
            elif current_date.weekday() == 2:  # Wednesday
                wed_attendees = random.sample(members, k=int(len(members) * 0.3))
                for member in wed_attendees:
                    attendance = Attendance(
                        church_id=church_id,
                        member_id=member.id,
                        service_date=current_date,
                        service_type="wednesday",
                        present=True,
                        check_in_time=datetime.combine(current_date, time(19, 20 + random.randint(0, 9))),
                        check_in_method="manual"
                    )
                    db.add(attendance)
                    created_attendance += 1
            
            # Dawn prayer (15% attendance, daily)
            if random.random() < 0.7:  # Not every day
                dawn_attendees = random.sample(members, k=max(1, int(len(members) * 0.15)))
                for member in dawn_attendees:
                    attendance = Attendance(
                        church_id=church_id,
                        member_id=member.id,
                        service_date=current_date,
                        service_type="dawn_prayer",
                        present=True,
                        check_in_time=datetime.combine(current_date, time(5, 25 + random.randint(0, 10))),
                        check_in_method="manual"
                    )
                    db.add(attendance)
                    created_attendance += 1
            
            current_date += timedelta(days=1)
        
        db.commit()
        print(f"✅ Created {created_attendance} attendance records")
        
        # Verify created data
        total_services = db.query(WorshipService).filter(WorshipService.church_id == church_id).count()
        total_attendance = db.query(Attendance).filter(Attendance.church_id == church_id).count()
        
        print(f"\n📊 Verification:")
        print(f"   • Worship services: {total_services}")
        print(f"   • Attendance records: {total_attendance}")
        
        # Test the functions
        print(f"\n🧪 Testing functions...")
        from app.services.church_data_context import get_worship_schedule, get_attendance_stats
        
        # Test worship schedule
        worship_result = get_worship_schedule(db, church_id)
        print(f"   • get_worship_schedule: {len(worship_result)} services")
        if worship_result:
            for service in worship_result[:2]:  # Show first 2
                print(f"     - {service['day_name']} {service['start_time'][:5]} {service['name']}")
        
        # Test attendance stats
        attendance_result = get_attendance_stats(db, church_id)
        print(f"   • get_attendance_stats:")
        print(f"     - Total members: {attendance_result['total_members']}")
        print(f"     - Last week attendance: {attendance_result['last_week_attendance']}")
        print(f"     - Attendance rate: {attendance_result['attendance_rate']}%")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_missing_sample_data()