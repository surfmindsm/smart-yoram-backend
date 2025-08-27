"""
비서 에이전트 서비스 - AI Agent 시스템과 Smart Assistant 통합
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.models.ai_agent import AIAgent, OfficialAgentTemplate
from app.services.smart_assistant_service import SmartAssistantService
from app.models.church import Church

logger = logging.getLogger(__name__)


class SecretaryAgentService:
    """교회 비서 에이전트 관리 서비스"""
    
    def __init__(self):
        self.smart_assistant = SmartAssistantService()
    
    def ensure_secretary_agent_template(self, db: Session) -> OfficialAgentTemplate:
        """비서 에이전트 템플릿이 없으면 생성"""
        
        template = db.query(OfficialAgentTemplate).filter(
            OfficialAgentTemplate.category == "secretary"
        ).first()
        
        if not template:
            template = OfficialAgentTemplate(
                name="교회 비서 AI",
                category="secretary",
                description="교회 업무를 도와주는 스마트 비서 에이전트",
                detailed_description="""
교회 데이터를 실시간으로 조회하여 업무를 지원하는 AI 비서입니다.

주요 기능:
• 심방 일정 조회 및 관리
• 중보기도 요청 확인
• 공지사항 정리 및 안내  
• 심방 보고서 분석
• 교회 업무 전반적인 지원

자연어로 질문하시면 관련 데이터를 찾아서 구체적이고 실용적인 답변을 드립니다.
                """.strip(),
                icon="👩‍💼",
                system_prompt=self._get_secretary_system_prompt(),
                church_data_sources={
                    "pastoral_care_requests": True,
                    "prayer_requests": True, 
                    "announcements": True,
                    "offerings": True,
                    "attendances": True,
                    "members": True,
                    "worship_services": True,
                    "visits": True,
                    "users": True
                },
                is_public=True,
                version="1.0.0",
                created_by="Smart Yoram Team"
            )
            db.add(template)
            db.commit()
            db.refresh(template)
            logger.info("Secretary agent template created")
        
        return template
    
    def ensure_church_secretary_agent(self, church_id: int, db: Session) -> AIAgent:
        """교회에 비서 에이전트가 없으면 생성"""
        
        # 기존 비서 에이전트 확인
        secretary = db.query(AIAgent).filter(
            AIAgent.church_id == church_id,
            AIAgent.category == "secretary"
        ).first()
        
        if not secretary:
            # 템플릿 확인/생성
            template = self.ensure_secretary_agent_template(db)
            
            # 교회 정보 조회
            church = db.query(Church).filter(Church.id == church_id).first()
            church_name = church.name if church else f"교회 {church_id}"
            
            # 비서 에이전트 생성
            secretary = AIAgent(
                church_id=church_id,
                template_id=template.id,
                name=f"{church_name} 비서",
                category="secretary", 
                description=f"{church_name}의 업무를 도와주는 스마트 비서",
                detailed_description=template.detailed_description,
                icon="👩‍💼",
                system_prompt=template.system_prompt,
                church_data_sources=template.church_data_sources,
                is_active=True,
                is_default=False,  # 기본 에이전트는 아님
                enable_church_data=True,  # 데이터 조회 기능 활성화
                max_tokens=2000,
                temperature=0.3,  # 사실적 응답을 위한 낮은 온도
                created_by_system=True
            )
            db.add(secretary)
            db.commit() 
            db.refresh(secretary)
            logger.info(f"Secretary agent created for church {church_id}")
        
        return secretary
    
    async def process_secretary_message(
        self,
        agent: AIAgent,
        user_message: str,
        user_id: int,
        db: Session,
        chat_history_id: Optional[int] = None
    ) -> Dict:
        """비서 에이전트 메시지 처리 (데이터 조회 기능 포함)"""
        
        try:
            # Smart Assistant 로직 사용하여 데이터 기반 응답 생성
            result = await self.smart_assistant.process_query(
                user_message=user_message,
                church_id=agent.church_id,
                user_id=user_id,
                db=db,
                gpt_config={
                    "model": agent.gpt_model or "gpt-4o-mini",
                    "max_tokens": agent.max_tokens or 2000,
                    "temperature": agent.temperature or 0.3
                }
            )
            
            return {
                "response": result["response"],
                "query_type": result.get("query_type", "general"),
                "data_sources": result.get("data_sources", []),
                "tokens_used": result.get("tokens_used", 0),
                "model": result.get("model", "gpt-4o-mini"),
                "success": True,
                "is_data_enhanced": True  # 데이터가 강화된 응답임을 표시
            }
            
        except Exception as e:
            logger.error(f"Secretary agent processing error: {e}")
            return {
                "response": "죄송합니다. 업무 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "query_type": "error",
                "data_sources": [],
                "tokens_used": 0,
                "success": False,
                "error": str(e),
                "is_data_enhanced": False
            }
    
    def _get_secretary_system_prompt(self) -> str:
        """비서 에이전트 시스템 프롬프트"""
        return """
당신은 교회 업무를 전문적으로 도와주는 AI 비서입니다.

# 역할과 책임
- 교회 담임목사, 교역자, 관리자의 업무 지원
- 교회 데이터를 활용한 정확한 정보 제공  
- 실무적이고 구체적인 답변 제공
- 친근하면서도 전문적인 서비스

# 전문 분야
1. **심방 관리**: 일정 조회, 우선순위 안내, 방문 정보 제공
2. **기도 요청 관리**: 중보기도 현황, 긴급 요청 파악
3. **공지사항 관리**: 최신 소식 정리, 중요도별 분류
4. **심방 보고서**: 현황 분석, 후속 조치 안내
5. **일반 업무**: 교회 운영 전반에 대한 지원

# 응답 스타일
- 시간, 장소, 연락처 등 구체적 정보 포함
- 우선순위나 긴급도 명시
- 실행 가능한 조치사항 제안
- 개인정보는 업무상 필요한 범위에서만 언급

# 인사말
안녕하세요! 교회 업무를 도와드리는 AI 비서입니다. 
심방 일정, 기도 요청, 공지사항 등 어떤 업무든 문의해 주세요.

예시 질문:
"오늘 심방 일정 알려줘"
"긴급한 기도 요청 있나?"
"이번주 중요한 공지사항 정리해줘"
        """.strip()


# 서비스 인스턴스
secretary_agent_service = SecretaryAgentService()