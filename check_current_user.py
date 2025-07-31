#!/usr/bin/env python3
"""
Check current users and their church_id
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import models

def check_users():
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        print("Current users:")
        print("-" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Church ID':<10} {'Church Name':<20}")
        print("-" * 80)
        
        for user in users:
            church_name = "N/A"
            if user.church_id:
                church = db.query(models.Church).filter(models.Church.id == user.church_id).first()
                if church:
                    church_name = church.name
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.church_id or 'None':<10} {church_name:<20}")
        
        print("\n\nCurrent churches:")
        print("-" * 60)
        churches = db.query(models.Church).all()
        for church in churches:
            print(f"ID: {church.id}, Name: {church.name}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()