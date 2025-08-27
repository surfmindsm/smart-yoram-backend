#!/usr/bin/env python3
"""
Update existing secretary agents with new data sources
"""

import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.ai_agent import AIAgent

logger = logging.getLogger(__name__)

def update_secretary_agents():
    """Update existing secretary agents with new data sources"""
    db = SessionLocal()
    
    try:
        print("🚀 Updating secretary agents with new data sources...")
        
        # Find all secretary agents
        secretary_agents = db.query(AIAgent).filter(
            AIAgent.category == "secretary"
        ).all()
        
        print(f"📊 Found {len(secretary_agents)} secretary agents")
        
        updated_count = 0
        
        for agent in secretary_agents:
            try:
                # Get current data sources or create new dict
                current_sources = agent.church_data_sources or {}
                
                # Add new data sources
                new_sources = {
                    "pastoral_care_requests": True,
                    "prayer_requests": True, 
                    "announcements": True,
                    "offerings": True,
                    "attendances": True,
                    "members": True,
                    "worship_services": True,
                    "visits": True,
                    "users": True
                }
                
                # Update the agent's data sources
                agent.church_data_sources = new_sources
                
                print(f"✅ Updated agent {agent.id} ({agent.name}) with new data sources")
                updated_count += 1
                
            except Exception as e:
                print(f"❌ Failed to update agent {agent.id}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Update completed!")
        print(f"📈 Statistics:")
        print(f"   - Total secretary agents: {len(secretary_agents)}")
        print(f"   - Successfully updated: {updated_count}")
        
        if updated_count > 0:
            print(f"\n💡 {updated_count} secretary agents now have access to:")
            print("   - 헌금 현황 (offerings)")
            print("   - 출석 통계 (attendances)")
            print("   - 교인 정보 (members)")
            print("   - 예배 일정 (worship_services)")
            
    except Exception as e:
        print(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_secretary_agents()