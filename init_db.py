#!/usr/bin/env python
"""Initialize the database with tables and default data."""

from sqlalchemy import create_engine
from app.db.base import Base
from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.core.config import settings


def create_tables():
    """Create all tables in the database."""
    print("Creating database tables...")
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


def create_initial_data():
    """Create initial data including superuser."""
    print("Creating initial data...")
    db = SessionLocal()
    try:
        init_db(db)
        print("Initial data created successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Initializing database at: {settings.DATABASE_URL}")
    create_tables()
    create_initial_data()
    print("\nDatabase initialization completed!")
    print(f"Superuser created: {settings.FIRST_SUPERUSER}")
    print(f"Password: {settings.FIRST_SUPERUSER_PASSWORD}")
    print("\nYou can now login with these credentials.")
