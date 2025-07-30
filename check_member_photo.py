#!/usr/bin/env python3
"""Check if member photo URL is saved in database."""
from app.db.session import SessionLocal
from app import models

db = SessionLocal()

# Check member with ID 63
member = db.query(models.Member).filter(models.Member.id == 63).first()

if member:
    print(f"Member: {member.name}")
    print(f"Profile Photo URL: {member.profile_photo_url}")
    print(f"Photo URL (old field): {member.photo_url}")
else:
    print("Member not found")

db.close()