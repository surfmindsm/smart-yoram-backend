#!/usr/bin/env python3
"""
Create sample offering data for testing
"""

from datetime import datetime, timedelta
import random
from app.db.session import SessionLocal
from app.models.financial import Offering
from app.models.member import Member
from app.models.user import User
from sqlalchemy import func

def create_sample_offerings(church_id=9999):
    """Create sample offering data for specified church ID"""
    db = SessionLocal()
    
    try:
        print(f"🏛️  Creating sample offering data for church ID {church_id}...")
        
        # Get admin user for input_user_id
        admin_user = db.query(User).filter(User.church_id == church_id).first()
        if not admin_user:
            print(f"⚠️  No user found for church {church_id}. Cannot create offerings without input_user_id")
            return
        
        print(f"👤 Using admin user: {admin_user.username} (ID: {admin_user.id})")
        
        # Check if church has members
        members = db.query(Member).filter(Member.church_id == church_id, Member.status == "active").all()
        
        if not members:
            print(f"⚠️  No active members found for church {church_id}. Creating sample members first...")
            # Create some sample members
            sample_members = [
                {"name": "김철수", "age": 45, "gender": "M", "position": "elder"},
                {"name": "이영희", "age": 38, "gender": "F", "position": "deacon"},
                {"name": "박민수", "age": 32, "gender": "M", "position": "member"},
                {"name": "정수진", "age": 29, "gender": "F", "position": "member"},
                {"name": "최대환", "age": 55, "gender": "M", "position": "deacon"},
                {"name": "한미경", "age": 41, "gender": "F", "position": "member"},
                {"name": "류정호", "age": 36, "gender": "M", "position": "member"},
                {"name": "송지영", "age": 44, "gender": "F", "position": "deacon"},
            ]
            
            for member_data in sample_members:
                member = Member(
                    church_id=church_id,
                    name=member_data["name"],
                    age=member_data["age"],
                    gender=member_data["gender"],
                    position=member_data["position"],
                    status="active",
                    registration_date=datetime.now().date() - timedelta(days=random.randint(30, 365*2))
                )
                db.add(member)
            
            db.commit()
            print(f"✅ Created {len(sample_members)} sample members")
            
            # Refresh members list
            members = db.query(Member).filter(Member.church_id == church_id, Member.status == "active").all()
        
        print(f"👥 Found {len(members)} active members for church {church_id}")
        
        # Create offerings for the past 12 months
        offering_types = ["십일조", "주일헌금", "감사헌금", "선교헌금", "건축헌금", "특별헌금"]
        
        offerings_created = 0
        start_date = datetime.now().date() - timedelta(days=365)
        
        # Create weekly offerings
        current_date = start_date
        while current_date <= datetime.now().date():
            # Sunday offerings (more members participate)
            sunday_participants = random.sample(members, k=random.randint(len(members)//2, len(members)))
            
            for member in sunday_participants:
                # Each member might give multiple types of offerings
                num_offerings = random.choices([1, 2, 3], weights=[70, 25, 5], k=1)[0]
                selected_types = random.sample(offering_types, k=min(num_offerings, len(offering_types)))
                
                for offering_type in selected_types:
                    # Amount varies by offering type and member position
                    base_amounts = {
                        "십일조": (50000, 300000),
                        "주일헌금": (10000, 50000), 
                        "감사헌금": (30000, 200000),
                        "선교헌금": (20000, 100000),
                        "건축헌금": (50000, 500000),
                        "특별헌금": (20000, 150000)
                    }
                    
                    min_amt, max_amt = base_amounts[offering_type]
                    
                    # Leaders tend to give more
                    if member.position in ["pastor", "elder"]:
                        min_amt = int(min_amt * 1.5)
                        max_amt = int(max_amt * 2)
                    elif member.position == "deacon":
                        min_amt = int(min_amt * 1.2)
                        max_amt = int(max_amt * 1.5)
                    
                    amount = random.randint(min_amt, max_amt)
                    # Round to nearest 1000
                    amount = round(amount / 1000) * 1000
                    
                    offering = Offering(
                        church_id=church_id,
                        member_id=member.id,
                        amount=amount,
                        fund_type=offering_type,
                        offered_on=current_date,
                        note=f"{member.name}님 {offering_type}",
                        input_user_id=admin_user.id,
                        created_at=datetime.combine(current_date, datetime.min.time())
                    )
                    db.add(offering)
                    offerings_created += 1
            
            # Move to next Sunday
            days_until_sunday = (6 - current_date.weekday()) % 7
            if days_until_sunday == 0:
                days_until_sunday = 7
            current_date += timedelta(days=days_until_sunday)
        
        # Add some mid-week special offerings
        for _ in range(20):
            member = random.choice(members)
            special_date = start_date + timedelta(days=random.randint(0, 365))
            offering_type = random.choice(["감사헌금", "특별헌금", "선교헌금"])
            amount = random.randint(30000, 200000)
            amount = round(amount / 1000) * 1000
            
            offering = Offering(
                church_id=church_id,
                member_id=member.id,
                amount=amount,
                fund_type=offering_type,
                offered_on=special_date,
                note=f"{member.name}님 특별 {offering_type}",
                input_user_id=admin_user.id,
                created_at=datetime.combine(special_date, datetime.min.time())
            )
            db.add(offering)
            offerings_created += 1
        
        db.commit()
        
        # Verify created data
        total_offerings = db.query(Offering).filter(Offering.church_id == church_id).count()
        total_amount = db.query(func.sum(Offering.amount)).filter(Offering.church_id == church_id).scalar() or 0
        
        print(f"✅ Successfully created {offerings_created} offering records")
        print(f"📊 Total offerings in database: {total_offerings}")
        print(f"💰 Total amount: {total_amount:,} 원")
        
        # Show breakdown by fund type
        fund_breakdown = db.query(
            Offering.fund_type,
            func.sum(Offering.amount).label("total"),
            func.count(Offering.id).label("count")
        ).filter(Offering.church_id == church_id).group_by(Offering.fund_type).all()
        
        print("\n📋 Fund type breakdown:")
        for fund_type, total, count in fund_breakdown:
            print(f"   • {fund_type}: {total:,}원 ({count}건)")
            
        # Test the offering function
        print("\n🧪 Testing get_all_offerings function...")
        from app.services.church_data_context import get_all_offerings
        result = get_all_offerings(db, church_id)
        
        print(f"✅ Function returned data:")
        print(f"   • This year total: {result['totals']['this_year']:,.0f}원")
        print(f"   • This month total: {result['totals']['this_month']:,.0f}원")
        print(f"   • Fund types: {len(result['fund_breakdown'])}")
        print(f"   • Recent offerings: {len(result['recent_offerings'])}")
        
    except Exception as e:
        print(f"❌ Error creating sample offerings: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_offerings()