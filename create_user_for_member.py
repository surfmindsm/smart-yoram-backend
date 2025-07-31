#!/usr/bin/env python3
"""
Create user account for existing member
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import models
from app.utils.password import generate_temporary_password
from app.utils.encryption import encrypt_password
from app.core.security import get_password_hash

def create_user_for_member(member_id: int):
    db = SessionLocal()
    try:
        # Get member
        member = db.query(models.Member).filter(models.Member.id == member_id).first()
        if not member:
            print(f"Member {member_id} not found")
            return
        
        print(f"Found member: {member.name} ({member.email})")
        
        if member.user_id:
            print(f"Member already has user account: {member.user_id}")
            return
        
        if not member.email:
            print(f"Member has no email address")
            return
        
        # Check if user already exists
        existing_user = db.query(models.User).filter(models.User.email == member.email).first()
        if existing_user:
            print(f"User with email {member.email} already exists")
            # Link member to existing user
            member.user_id = existing_user.id
            db.commit()
            print(f"Linked member to existing user {existing_user.id}")
            return
        
        # Generate temporary password
        temp_password = generate_temporary_password()
        print(f"Generated temporary password: {temp_password}")
        
        # Create user
        user = models.User(
            email=member.email,
            username=member.email,
            hashed_password=get_password_hash(temp_password),
            encrypted_password=encrypt_password(temp_password),
            full_name=member.name,
            phone=member.phone,
            church_id=member.church_id,
            role="member",
            is_active=True
        )
        
        db.add(user)
        db.flush()
        
        # Link member to user
        member.user_id = user.id
        
        db.commit()
        print(f"Created user {user.id} for member {member.id}")
        print(f"Email: {user.email}")
        print(f"Temporary password: {temp_password}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        member_id = int(sys.argv[1])
        create_user_for_member(member_id)
    else:
        print("Usage: python create_user_for_member.py <member_id>")