#!/usr/bin/env python3
"""
Check user and church relationships
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import User, Church
from app.models.ai_agent import AIAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_user_church():
    db = SessionLocal()

    try:
        # Check user ID 14
        user = db.query(User).filter(User.id == 14).first()
        if user:
            print(f"User ID 14: {user.email}")
            print(f"  Church ID: {user.church_id}")

            # Get church info
            if user.church_id:
                church = db.query(Church).filter(Church.id == user.church_id).first()
                if church:
                    print(f"  Church Name: {church.name}")

                    # Get agents for this church
                    agents = (
                        db.query(AIAgent).filter(AIAgent.church_id == church.id).all()
                    )
                    print(f"  Agents for church {church.id}: {len(agents)}")
                    for agent in agents:
                        print(f"    - Agent ID: {agent.id}, Name: {agent.name}")
                else:
                    print(f"  Church not found!")
            else:
                print(f"  No church assigned!")

        # Update user's church_id if needed
        if user and user.church_id != 1:
            print(f"\nUpdating user's church_id from {user.church_id} to 1...")
            user.church_id = 1
            db.commit()
            print("Updated successfully!")

    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    check_user_church()
