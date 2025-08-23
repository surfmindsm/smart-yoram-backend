#!/usr/bin/env python
"""
데모 테넌트 (Church ID: 9999) 생성 스크립트
- 데모 교회 생성
- 관리자 계정 1개
- 사용자 계정 2개
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.church import Church
from app.models.user import User
from app.models.member import Member
from app.core.security import get_password_hash
from app.utils.encryption import encrypt_password
from datetime import datetime, date
import json


def create_demo_church(db: Session):
    """데모 교회 생성"""
    # 기존 데모 교회 확인
    existing = db.query(Church).filter(Church.id == 9999).first()
    if existing:
        print(f"✅ Demo church already exists: {existing.name}")
        return existing
    
    demo_church = Church(
        id=9999,
        name="스마트요람 데모교회",
        address="서울특별시 강남구 테헤란로 152",
        phone="02-1234-5678",
        email="demo@smartyoram.com",
        pastor_name="김목사",
        district_scheme="구역",
        subscription_status="active",
        subscription_plan="premium",
        member_limit=1000,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(demo_church)
    db.commit()
    db.refresh(demo_church)
    print(f"✅ Created demo church: {demo_church.name} (ID: {demo_church.id})")
    return demo_church


def create_admin_account(db: Session, church_id: int):
    """관리자 계정 생성"""
    # 기존 관리자 확인
    existing = db.query(User).filter(
        User.email == "admin@demo.smartyoram.com"
    ).first()
    if existing:
        print(f"✅ Admin account already exists: {existing.email}")
        return existing
    
    password = "Demo@Admin2025"
    admin_user = User(
        email="admin@demo.smartyoram.com",
        username="demo_admin",
        hashed_password=get_password_hash(password),
        encrypted_password=encrypt_password(password),
        full_name="데모 관리자",
        phone="010-1111-2222",
        church_id=church_id,
        role="admin",
        is_active=True,
        is_superuser=False,
        is_first=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # 관리자 Member 생성
    admin_member = Member(
        church_id=church_id,
        user_id=admin_user.id,
        name="데모 관리자",
        phone="010-1111-2222",
        email="admin@demo.smartyoram.com",
        address="서울특별시 강남구 테헤란로 152",
        position="pastor",  # 목사
        department="관리부",
        status="active",
        member_status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(admin_member)
    db.commit()
    
    print(f"✅ Created admin account:")
    print(f"   Email: {admin_user.email}")
    print(f"   Password: {password}")
    print(f"   Role: {admin_user.role}")
    
    return admin_user


def create_user_accounts(db: Session, church_id: int):
    """사용자 계정 2개 생성"""
    users = []
    
    user_data = [
        {
            "email": "user1@demo.smartyoram.com",
            "username": "demo_user1",
            "full_name": "김성도",
            "phone": "010-3333-4444",
            "password": "Demo@User1",
            "position": "deacon",  # 집사
            "department": "청년부"
        },
        {
            "email": "user2@demo.smartyoram.com",
            "username": "demo_user2",
            "full_name": "이신실",
            "phone": "010-5555-6666",
            "password": "Demo@User2",
            "position": "member",  # 성도
            "department": "여전도회"
        }
    ]
    
    for data in user_data:
        # 기존 사용자 확인
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            print(f"✅ User account already exists: {existing.email}")
            users.append(existing)
            continue
        
        # User 생성
        user = User(
            email=data["email"],
            username=data["username"],
            hashed_password=get_password_hash(data["password"]),
            encrypted_password=encrypt_password(data["password"]),
            full_name=data["full_name"],
            phone=data["phone"],
            church_id=church_id,
            role="member",
            is_active=True,
            is_superuser=False,
            is_first=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Member 생성
        member = Member(
            church_id=church_id,
            user_id=user.id,
            name=data["full_name"],
            phone=data["phone"],
            email=data["email"],
            address="서울특별시 강남구 테헤란로 152",
            position=data["position"],
            department=data["department"],
            status="active",
            member_status="active",
            birthdate=date(1990, 1, 1),
            gender="M" if "김" in data["full_name"] else "F",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(member)
        db.commit()
        
        print(f"✅ Created user account:")
        print(f"   Email: {user.email}")
        print(f"   Password: {data['password']}")
        print(f"   Name: {user.full_name}")
        print(f"   Position: {data['position']}")
        
        users.append(user)
    
    return users


def save_credentials(admin, users):
    """계정 정보를 파일로 저장"""
    credentials = {
        "demo_church": {
            "church_id": 9999,
            "name": "스마트요람 데모교회",
            "description": "데모 및 테스트용 교회"
        },
        "admin_account": {
            "email": "admin@demo.smartyoram.com",
            "password": "Demo@Admin2025",
            "role": "admin",
            "description": "교회 관리자 계정"
        },
        "user_accounts": [
            {
                "email": "user1@demo.smartyoram.com",
                "password": "Demo@User1",
                "name": "김성도",
                "position": "집사",
                "description": "일반 사용자 계정 1"
            },
            {
                "email": "user2@demo.smartyoram.com",
                "password": "Demo@User2",
                "name": "이신실",
                "position": "성도",
                "description": "일반 사용자 계정 2"
            }
        ],
        "api_endpoints": {
            "base_url": "http://13.211.169.169:8000",
            "login": "/api/v1/auth/login",
            "members": "/api/v1/members",
            "announcements": "/api/v1/announcements"
        },
        "notes": [
            "이 계정들은 데모 및 테스트 목적으로만 사용됩니다.",
            "프론트엔드 개발 시 이 계정들로 로그인하여 테스트할 수 있습니다.",
            "브라이언님이 목업 데이터 100명을 추가로 입력할 예정입니다."
        ]
    }
    
    # JSON 파일로 저장
    with open("DEMO_CREDENTIALS.json", "w", encoding="utf-8") as f:
        json.dump(credentials, f, ensure_ascii=False, indent=2)
    
    # Markdown 파일로도 저장
    with open("DEMO_CREDENTIALS.md", "w", encoding="utf-8") as f:
        f.write("# 스마트요람 데모 계정 정보\n\n")
        f.write("## 📌 데모 교회 정보\n")
        f.write("- **Church ID**: 9999\n")
        f.write("- **교회명**: 스마트요람 데모교회\n")
        f.write("- **설명**: 데모 및 테스트용 가상 교회\n\n")
        
        f.write("## 👤 관리자 계정\n")
        f.write("| 항목 | 내용 |\n")
        f.write("|------|------|\n")
        f.write("| Email | admin@demo.smartyoram.com |\n")
        f.write("| Password | Demo@Admin2025 |\n")
        f.write("| Role | admin (교회 관리자) |\n\n")
        
        f.write("## 👥 사용자 계정\n")
        f.write("| Email | Password | 이름 | 직분 |\n")
        f.write("|-------|----------|------|------|\n")
        f.write("| user1@demo.smartyoram.com | Demo@User1 | 김성도 | 집사 |\n")
        f.write("| user2@demo.smartyoram.com | Demo@User2 | 이신실 | 성도 |\n\n")
        
        f.write("## 🔗 API 엔드포인트\n")
        f.write("- **Base URL**: http://13.211.169.169:8000\n")
        f.write("- **로그인**: POST /api/v1/auth/login\n")
        f.write("- **회원 목록**: GET /api/v1/members\n")
        f.write("- **공지사항**: GET /api/v1/announcements\n\n")
        
        f.write("## 📝 참고사항\n")
        f.write("- 이 계정들은 데모 및 테스트 목적으로만 사용됩니다.\n")
        f.write("- 프론트엔드 개발 시 이 계정들로 로그인하여 테스트할 수 있습니다.\n")
        f.write("- 브라이언님이 목업 데이터 100명을 추가로 입력할 예정입니다.\n")
    
    print("\n✅ Credentials saved to:")
    print("   - DEMO_CREDENTIALS.json")
    print("   - DEMO_CREDENTIALS.md")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 Creating Demo Tenant (Church ID: 9999)")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. 데모 교회 생성
        church = create_demo_church(db)
        
        # 2. 관리자 계정 생성
        admin = create_admin_account(db, church.id)
        
        # 3. 사용자 계정 생성
        users = create_user_accounts(db, church.id)
        
        # 4. 계정 정보 저장
        save_credentials(admin, users)
        
        print("\n" + "=" * 50)
        print("✅ Demo tenant creation completed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()