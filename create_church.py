#!/usr/bin/env python3
"""
Create initial church data for testing
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import models
from datetime import datetime, timedelta

def create_test_church():
    db = SessionLocal()
    try:
        # Check if church already exists
        existing_church = db.query(models.Church).filter(models.Church.id == 1).first()
        if existing_church:
            print(f"Church already exists: {existing_church.name}")
            return
        
        # Create new church
        church = models.Church(
            id=1,
            name="테스트 교회",
            address="서울시 강남구 테스트로 123",
            phone="02-1234-5678",
            email="admin@testchurch.com",
            pastor_name="홍길동 목사",
            subscription_status="active",
            subscription_end_date=datetime.utcnow() + timedelta(days=365),
            member_limit=1000,
            is_active=True
        )
        
        db.add(church)
        db.commit()
        db.refresh(church)
        
        print(f"Church created successfully: {church.name}")
        
    except Exception as e:
        print(f"Error creating church: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_church()