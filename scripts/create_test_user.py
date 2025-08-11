#!/usr/bin/env python3
"""
Create a test user for church
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import User, Church
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user():
    db = SessionLocal()
    
    try:
        # Get first church
        church = db.query(Church).first()
        if not church:
            logger.error("No church found in database")
            return None
        
        logger.info(f"Using church: {church.name} (ID: {church.id})")
        
        # Check if user exists
        email = "test@smartyoram.com"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create test user
            user = User(
                email=email,
                hashed_password=get_password_hash("test123"),
                full_name="Test User",
                church_id=church.id,
                is_active=True,
                is_superuser=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created test user: {user.email} (ID: {user.id})")
        else:
            logger.info(f"User already exists: {user.email} (ID: {user.id})")
        
        print("\n" + "="*50)
        print("TEST USER CREATED")
        print("="*50)
        print(f"Email: {email}")
        print(f"Password: test123")
        print(f"User ID: {user.id}")
        print(f"Church ID: {church.id}")
        print("="*50)
        
        return user
        
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()