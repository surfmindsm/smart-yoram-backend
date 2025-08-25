#!/usr/bin/env python3
"""
Update admin user to be a superuser (system admin)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app import models
import sys


def update_system_admin():
    # Create database connection
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()

    try:
        # Find admin user
        admin_user = (
            db.query(models.User).filter(models.User.username == "admin").first()
        )

        if not admin_user:
            print("Admin user not found")
            return False

        # Update to superuser
        admin_user.is_superuser = True
        admin_user.role = "system_admin"

        db.commit()

        print(f"Updated user '{admin_user.username}' to system admin (superuser)")
        print(f"User ID: {admin_user.id}")
        print(f"Email: {admin_user.email}")
        print(f"Is Superuser: {admin_user.is_superuser}")
        print(f"Role: {admin_user.role}")

        return True

    except Exception as e:
        print(f"Error updating admin user: {e}")
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    if update_system_admin():
        print("System admin updated successfully")
        sys.exit(0)
    else:
        print("Failed to update system admin")
        sys.exit(1)
