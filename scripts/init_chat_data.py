#!/usr/bin/env python3
"""
Initialize chat data for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.ai_agent import AIAgent, ChatHistory
from app.models import User, Church
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_chat_data():
    db = SessionLocal()
    
    try:
        # Get first church
        church = db.query(Church).first()
        if not church:
            logger.error("No church found in database")
            return
        
        logger.info(f"Using church: {church.name} (ID: {church.id})")
        
        # Check if AI agents exist
        agents = db.query(AIAgent).filter(AIAgent.church_id == church.id).all()
        
        if not agents:
            logger.info("No agents found. Creating default agents...")
            
            # Create default agents
            default_agents = [
                {
                    "name": "일반 상담 도우미",
                    "category": "general",
                    "system_prompt": "당신은 한국 교회를 돕는 친절한 AI 상담사입니다. 교인들의 신앙 생활과 교회 생활에 대한 질문에 성경적 관점에서 답변해주세요.",
                    "description": "교회 생활과 신앙에 대한 일반적인 질문을 도와드립니다.",
                    "is_active": True
                },
                {
                    "name": "성경 공부 도우미",
                    "category": "bible",
                    "system_prompt": "당신은 성경 교사입니다. 성경 구절의 의미와 적용에 대해 쉽고 명확하게 설명해주세요.",
                    "description": "성경 구절 해석과 적용을 도와드립니다.",
                    "is_active": True
                },
                {
                    "name": "교회 행정 도우미",
                    "category": "admin",
                    "system_prompt": "당신은 교회 행정을 돕는 AI 비서입니다. 교회 운영, 행사 기획, 교인 관리 등에 대한 실용적인 조언을 제공하세요.",
                    "description": "교회 행정과 운영에 대한 도움을 제공합니다.",
                    "is_active": True
                }
            ]
            
            for agent_data in default_agents:
                agent = AIAgent(
                    church_id=church.id,
                    **agent_data
                )
                db.add(agent)
            
            db.commit()
            logger.info(f"Created {len(default_agents)} default agents")
            
            # Refresh agents list
            agents = db.query(AIAgent).filter(AIAgent.church_id == church.id).all()
        
        logger.info(f"Found {len(agents)} agents:")
        for agent in agents:
            logger.info(f"  - Agent ID: {agent.id}, Name: {agent.name}, Category: {agent.category}")
        
        # Get first user (any user for testing)
        user = db.query(User).first()
        if not user:
            logger.error("No user found for this church")
            return
        
        logger.info(f"Using user: {user.email} (ID: {user.id})")
        
        # Check if chat histories exist
        histories = db.query(ChatHistory).filter(
            ChatHistory.church_id == church.id,
            ChatHistory.user_id == user.id
        ).all()
        
        if not histories and agents:
            logger.info("No chat histories found. Creating initial chat history...")
            
            # Create initial chat history with first agent
            first_agent = agents[0]
            history = ChatHistory(
                church_id=church.id,
                user_id=user.id,
                agent_id=first_agent.id,
                title=f"{first_agent.name}와의 대화",
                is_bookmarked=False,
                message_count=0
            )
            db.add(history)
            db.commit()
            
            logger.info(f"Created chat history ID: {history.id} with agent ID: {first_agent.id}")
        else:
            logger.info(f"Found {len(histories)} existing chat histories:")
            for history in histories:
                logger.info(f"  - History ID: {history.id}, Agent ID: {history.agent_id}, Title: {history.title}")
        
        # Print summary for testing
        print("\n" + "="*50)
        print("CHAT DATA INITIALIZATION COMPLETE")
        print("="*50)
        print(f"Church ID: {church.id}")
        print(f"User ID: {user.id}")
        if agents:
            print(f"Agent IDs: {[a.id for a in agents]}")
            print(f"\nYou can test with:")
            print(f"  agent_id: {agents[0].id}")
            if histories:
                print(f"  chat_history_id: {histories[0].id}")
            else:
                history = db.query(ChatHistory).filter(
                    ChatHistory.church_id == church.id,
                    ChatHistory.user_id == user.id
                ).first()
                if history:
                    print(f"  chat_history_id: {history.id}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Error initializing chat data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_chat_data()