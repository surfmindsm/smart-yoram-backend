"""
Church-specific Default Agent Service

Manages default agent creation and management for each church.
Each church gets its own default agent instead of using a global one.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.ai_agent import AIAgent
from app.schemas.ai_agent import AIAgentCreate


class ChurchDefaultAgentService:
    """Service for managing church-specific default agents"""

    @staticmethod
    def get_default_agent_config(church_id: int) -> dict:
        """Get default agent configuration for a church"""
        return {
            "name": "기본 AI 도우미",
            "category": "일반",
            "description": "일반적인 질문과 교회 업무를 도와드립니다.",
            "detailed_description": "교회의 기본 AI 도우미입니다. 일반적인 질문에 답변하고, 교회 업무와 관련된 기본적인 안내를 제공합니다. 더 전문적인 기능이 필요하시면 관리자에게 커스텀 에이전트 생성을 요청하세요.",
            "icon": "🤖",
            "system_prompt": """당신은 교회 관리 AI 도우미입니다.

역할:
- 일반적인 질문에 친절하게 답변
- 교회 업무와 관련된 기본적인 안내 제공  
- 성경에 대한 기본적인 질문 답변
- 교회 행정업무에 대한 일반적인 조언

응답 원칙:
- 항상 친절하고 정중한 톤으로 응답
- 구체적인 교회 데이터가 필요한 경우 관리자에게 문의하도록 안내
- 복잡하거나 전문적인 상담이 필요한 경우 적절한 전문가에게 연결하도록 안내
- 성경적 가치와 일치하는 건전한 답변 제공

제한사항:
- 의료, 법률, 재정 등 전문적인 상담은 해당 전문가에게 의뢰하도록 안내
- 교리나 신학적으로 민감한 주제는 신중하게 접근""",
            "church_data_sources": {},
            "is_active": True,
            "church_id": church_id,
            "template_id": None,
        }

    @staticmethod
    def create_default_agent_for_church(church_id: int, db: Session) -> AIAgent:
        """Create a default agent for a church"""

        # Check if church already has agents
        existing_agents = (
            db.query(AIAgent).filter(AIAgent.church_id == church_id).first()
        )
        if existing_agents:
            # Church already has agents, return the first one as default
            return existing_agents

        # Create new default agent
        config = ChurchDefaultAgentService.get_default_agent_config(church_id)

        agent = AIAgent(
            name=config["name"],
            category=config["category"],
            description=config["description"],
            detailed_description=config["detailed_description"],
            icon=config["icon"],
            system_prompt=config["system_prompt"],
            church_data_sources=config["church_data_sources"],
            is_active=config["is_active"],
            church_id=config["church_id"],
            template_id=config["template_id"],
            usage_count=0,
            total_tokens_used=0,
            total_cost=0.0,
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)

        return agent

    @staticmethod
    def get_or_create_default_agent(church_id: int, db: Session) -> AIAgent:
        """Get existing default agent or create one if none exists"""

        # Try to get the first active agent for the church
        agent = (
            db.query(AIAgent)
            .filter(AIAgent.church_id == church_id, AIAgent.is_active == True)
            .first()
        )

        if agent:
            return agent

        # No active agents found, create default agent
        return ChurchDefaultAgentService.create_default_agent_for_church(church_id, db)

    @staticmethod
    def ensure_church_has_default_agent(church_id: int, db: Session) -> AIAgent:
        """Ensure a church has at least one active agent"""
        return ChurchDefaultAgentService.get_or_create_default_agent(church_id, db)

    @staticmethod
    def add_default_agents_to_existing_churches(db: Session) -> dict:
        """Add default agents to churches that don't have any (migration helper)"""
        from app.models.church import Church

        results = {"created": 0, "skipped": 0, "errors": []}

        # Get all churches
        churches = db.query(Church).all()

        for church in churches:
            try:
                # Check if church has any agents
                existing_agents = (
                    db.query(AIAgent).filter(AIAgent.church_id == church.id).first()
                )

                if not existing_agents:
                    # Create default agent
                    agent = ChurchDefaultAgentService.create_default_agent_for_church(
                        church.id, db
                    )
                    results["created"] += 1
                    print(
                        f"✅ Created default agent for church: {church.name} (ID: {church.id})"
                    )
                else:
                    results["skipped"] += 1
                    print(f"⏭️ Church {church.name} already has agents")

            except Exception as e:
                error_msg = f"Failed to create agent for church {church.id}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")

        return results
