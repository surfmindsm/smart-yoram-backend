"""
Global Default Agent Service

Provides a fallback AI agent for churches that don't have custom agents configured.
This ensures that AI chat functionality is always available regardless of church setup.
"""

from typing import Optional, Dict, Any
from app.models.ai_agent import AIAgent


class DefaultAgentService:
    """Service for managing the global default AI agent"""

    # Global default agent configuration
    DEFAULT_AGENT_CONFIG = {
        "id": 0,
        "church_id": None,
        "template_id": None,
        "name": "기본 AI 도우미",
        "category": "일반",
        "description": "모든 교회에서 사용 가능한 공통 AI 도우미입니다.",
        "detailed_description": "새로운 교회를 위한 기본 AI 에이전트입니다. 일반적인 질문에 답변하고, 교회 업무에 대한 기본적인 안내를 제공합니다. 더 전문적인 기능이 필요하시면 관리자에게 커스텀 에이전트 생성을 요청하세요.",
        "icon": "🤖",
        "system_prompt": """당신은 모든 교회에서 사용할 수 있는 기본 AI 도우미입니다.

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
- 특정 교회의 내부 데이터나 개인정보에는 접근할 수 없음
- 의료, 법률, 재정 등 전문적인 상담은 해당 전문가에게 의뢰하도록 안내
- 교리나 신학적으로 민감한 주제는 신중하게 접근""",
        "church_data_sources": {},
        "is_active": True,
        "usage_count": 0,
        "total_tokens_used": 0,
        "total_cost": 0.0,
        "created_at": None,
        "updated_at": None,
    }

    @classmethod
    def get_default_agent(cls) -> Dict[str, Any]:
        """Get the global default agent configuration"""
        return cls.DEFAULT_AGENT_CONFIG.copy()

    @classmethod
    def create_virtual_agent(cls) -> AIAgent:
        """Create a virtual AIAgent object for the default agent"""
        config = cls.get_default_agent()

        # Create a virtual AIAgent object (not persisted to database)
        virtual_agent = AIAgent()
        for key, value in config.items():
            setattr(virtual_agent, key, value)

        return virtual_agent

    @classmethod
    def get_agent_for_church(
        cls, agent_id: int, church_id: int, db
    ) -> Optional[AIAgent]:
        """
        Get agent for a specific church, with fallback to default agent

        Args:
            agent_id: The requested agent ID (0 for default)
            church_id: The church ID
            db: Database session

        Returns:
            AIAgent object or None
        """
        # If requesting default agent (ID 0), return virtual default agent
        if agent_id == 0:
            return cls.create_virtual_agent()

        # Try to find the specific agent for this church
        agent = (
            db.query(AIAgent)
            .filter(
                AIAgent.id == agent_id,
                AIAgent.church_id == church_id,
                AIAgent.is_active == True,
            )
            .first()
        )

        if agent:
            return agent

        # If specific agent not found, return default agent as fallback
        return cls.create_virtual_agent()

    @classmethod
    def get_available_agents_for_church(cls, church_id: int, db) -> list:
        """
        Get all available agents for a church including the default agent

        Args:
            church_id: The church ID
            db: Database session

        Returns:
            List of agent data dictionaries
        """
        # Get church-specific agents
        church_agents = db.query(AIAgent).filter(AIAgent.church_id == church_id).all()

        # Convert to list of dictionaries
        agents_data = []

        # Always include the default agent first
        default_config = cls.get_default_agent()
        agents_data.append(default_config)

        # Add church-specific agents
        for agent in church_agents:
            agent_dict = {
                "id": agent.id,
                "church_id": agent.church_id,
                "template_id": agent.template_id,
                "name": agent.name,
                "category": agent.category,
                "description": agent.description,
                "detailed_description": agent.detailed_description,
                "icon": agent.icon,
                "system_prompt": agent.system_prompt,
                "church_data_sources": agent.church_data_sources or {},
                "is_active": agent.is_active,
                "usage_count": agent.usage_count or 0,
                "total_tokens_used": agent.total_tokens_used or 0,
                "total_cost": agent.total_cost or 0.0,
                "created_at": agent.created_at,
                "updated_at": agent.updated_at,
            }
            agents_data.append(agent_dict)

        return agents_data

    @classmethod
    def is_default_agent(cls, agent_id: int) -> bool:
        """Check if the given agent_id is the default agent"""
        return agent_id == 0

    @classmethod
    def can_use_agent(cls, agent_id: int, church_id: int, db) -> bool:
        """Check if a church can use a specific agent"""
        if cls.is_default_agent(agent_id):
            return True  # Default agent is always available

        # Check if church-specific agent exists and is active
        agent = (
            db.query(AIAgent)
            .filter(
                AIAgent.id == agent_id,
                AIAgent.church_id == church_id,
                AIAgent.is_active == True,
            )
            .first()
        )

        return agent is not None
