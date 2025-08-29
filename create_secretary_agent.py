#!/usr/bin/env python3
"""
Create secretary agent for testing
"""

from app.db.session import SessionLocal
from app.models.ai_agent import AIAgent
from app.models.church import Church
from app.models.user import User

def create_secretary_agent():
    """Create a secretary agent for church 9999"""
    db = SessionLocal()
    
    try:
        print("🤖 Creating secretary agent...")
        
        # Check if church 9999 exists
        church = db.query(Church).filter(Church.id == 9999).first()
        if not church:
            print("❌ Church 9999 not found")
            return
            
        print(f"✅ Found church: {church.name}")
        
        # Check if secretary agent already exists
        existing_agent = db.query(AIAgent).filter(
            AIAgent.church_id == 9999,
            AIAgent.category == "secretary"
        ).first()
        
        if existing_agent:
            print(f"📝 Secretary agent already exists: {existing_agent.name}")
            # Update settings
            existing_agent.enable_church_data = True
            existing_agent.church_data_sources = {
                "announcements": True,
                "prayer_requests": True,
                "pastoral_care_requests": True,
                "offerings": True,
                "attendances": True,
                "members": True,
                "worship_services": True
            }
            existing_agent.is_active = True
            db.commit()
            print("✅ Updated existing secretary agent with church data sources")
            return
        
        # Create new secretary agent
        secretary_agent = AIAgent(
            church_id=9999,
            name="스마트요람 데모교회 비서",
            category="secretary", 
            system_prompt="""안녕하세요! 저는 스마트요람 데모교회의 AI 비서입니다.

교회 운영과 관련된 모든 질문에 성심성의껏 답변드리겠습니다:
- 헌금 현황 및 재정 정보
- 교인 출석 통계 및 현황  
- 기도 요청사항 및 심방 요청
- 교회 공지사항 및 일정
- 예배 시간 및 행사 안내
- 기타 교회 운영 관련 문의

궁금한 것이 있으시면 언제든지 말씀해 주세요!""",
            description="교회 운영 전반에 대한 정보를 제공하는 전문 비서",
            gpt_model="gpt-4o-mini",
            max_tokens=4000,
            temperature=0.7,
            enable_church_data=True,  # 핵심: 교회 데이터 활성화
            church_data_sources={
                "announcements": True,
                "prayer_requests": True, 
                "pastoral_care_requests": True,
                "offerings": True,
                "attendances": True,
                "members": True,
                "worship_services": True
            },
            is_active=True,
            is_default=False
        )
        
        db.add(secretary_agent)
        db.commit()
        db.refresh(secretary_agent)
        
        print(f"✅ Created secretary agent: {secretary_agent.name} (ID: {secretary_agent.id})")
        print(f"   Category: {secretary_agent.category}")
        print(f"   Enable Church Data: {secretary_agent.enable_church_data}")
        print(f"   Church Data Sources: {secretary_agent.church_data_sources}")
        
        # Also create a basic general agent if needed
        general_agent = db.query(AIAgent).filter(
            AIAgent.church_id == 9999,
            AIAgent.category == "일반"
        ).first()
        
        if not general_agent:
            general_agent = AIAgent(
                church_id=9999,
                name="기본 AI 도우미",
                category="일반",
                system_prompt="안녕하세요! 저는 일반적인 질문에 답변하는 AI 도우미입니다.",
                description="일반적인 대화 및 질문 답변",
                gpt_model="gpt-4o-mini", 
                max_tokens=4000,
                temperature=0.7,
                enable_church_data=False,
                is_active=True,
                is_default=True
            )
            
            db.add(general_agent)
            db.commit()
            print(f"✅ Also created general agent: {general_agent.name}")
        
        # Verify creation
        agents = db.query(AIAgent).filter(AIAgent.church_id == 9999).all()
        print(f"\\n📊 Total agents for church 9999: {len(agents)}")
        for agent in agents:
            print(f"   • {agent.name} ({agent.category}) - Church Data: {agent.enable_church_data}")
            
    except Exception as e:
        print(f"❌ Error creating secretary agent: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_secretary_agent()