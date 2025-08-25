#!/usr/bin/env python3
"""
Add default agents to existing churches that don't have any agents

This is a one-time migration script to ensure all existing churches
have at least one default agent for the new church-specific agent system.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.church_default_agent_service import ChurchDefaultAgentService


def main():
    """Run the migration to add default agents to existing churches"""
    print("🚀 Adding default agents to existing churches...")
    print("=" * 60)

    db: Session = SessionLocal()

    try:
        # Run the migration
        results = ChurchDefaultAgentService.add_default_agents_to_existing_churches(db)

        print("\n" + "=" * 60)
        print("📊 Migration Results:")
        print(f"✅ Created: {results['created']} default agents")
        print(f"⏭️ Skipped: {results['skipped']} churches (already had agents)")

        if results["errors"]:
            print(f"❌ Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"   - {error}")

        print("\n🎉 Migration completed successfully!")

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        db.close()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
