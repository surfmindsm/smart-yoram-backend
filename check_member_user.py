#!/usr/bin/env python3
"""
Check member and user relationship
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import models

def check_member_user():
    db = SessionLocal()
    try:
        # Get members with their user_id
        members = db.query(models.Member).all()
        
        print(f"Total members: {len(members)}")
        print("\nMembers and their user accounts:")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'User ID':<10} {'Has Account':<12}")
        print("-" * 80)
        
        for member in members:
            has_account = "Yes" if member.user_id else "No"
            print(f"{member.id:<5} {member.name:<20} {member.email or 'N/A':<30} {member.user_id or 'None':<10} {has_account:<12}")
        
        # Check users
        users = db.query(models.User).all()
        print(f"\n\nTotal users: {len(users)}")
        print("\nUsers:")
        print("-" * 80)
        print(f"{'ID':<5} {'Email':<30} {'Username':<20} {'Church ID':<10}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.id:<5} {user.email:<30} {user.username:<20} {user.church_id:<10}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_member_user()