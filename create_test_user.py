#!/usr/bin/env python3
"""Create a test user for Supabase Storage testing."""
from app.db.session import SessionLocal
from app import models
from app.core.security import get_password_hash

db = SessionLocal()

# Create test user
test_user = models.User(
    email="test@smartyoram.com",
    username="test@smartyoram.com",  # Username is same as email
    hashed_password=get_password_hash("test123"),
    full_name="Test User",
    role="admin",
    church_id=6,
    is_active=True,
    is_superuser=True,  # Make superuser for testing
)

# Check if user exists
existing_user = (
    db.query(models.User).filter(models.User.email == test_user.email).first()
)
if not existing_user:
    db.add(test_user)
    db.commit()
    print(f"Created test user: {test_user.email}")
else:
    print(f"User already exists: {test_user.email}")

db.close()
