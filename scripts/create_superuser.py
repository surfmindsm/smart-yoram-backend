#!/usr/bin/env python3
"""
Create superuser account for system administration
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

def create_superuser():
    db = SessionLocal()
    
    try:
        # Check if superuser exists
        email = "admin@smartyoram.com"
        password = "changeme123!"  # Change this in production!
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Get first church for association
            church = db.query(Church).first()
            if not church:
                logger.error("No church found. Please create a church first.")
                return None
            
            # Create superuser
            user = User(
                email=email,
                username="superadmin",  # Add username
                hashed_password=get_password_hash(password),
                full_name="System Administrator",
                church_id=church.id,
                is_active=True,
                is_superuser=True,  # This is the key flag for system admin
                role="admin"  # Set role to admin
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created superuser: {user.email}")
        else:
            # Update to superuser if not already
            if not user.is_superuser:
                user.is_superuser = True
                db.commit()
                logger.info(f"Updated user to superuser: {user.email}")
            else:
                logger.info(f"Superuser already exists: {user.email}")
        
        print("\n" + "="*60)
        print("SYSTEM ADMINISTRATOR ACCOUNT")
        print("="*60)
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"User ID: {user.id}")
        print(f"Is Superuser: {user.is_superuser}")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("="*60)
        
        print("\n📌 Access Points:")
        print("1. Swagger UI (API Documentation):")
        print("   https://api.surfmind-team.com/docs")
        print("   - Login with the credentials above")
        print("   - Test and manage all API endpoints")
        print("")
        print("2. Frontend Admin Dashboard:")
        print("   https://smart-yoram-admin.vercel.app")
        print("   - Login with the credentials above")
        print("   - Manage churches, users, and system settings")
        print("")
        print("3. Direct API Access:")
        print("   Use the credentials to get JWT token and access all endpoints")
        print("="*60)
        
        return user
        
    except Exception as e:
        logger.error(f"Error creating superuser: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()