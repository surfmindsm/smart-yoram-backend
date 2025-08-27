"""
Test OpenAI service that returns mock responses
"""

import random
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class TestOpenAIService:
    """Mock OpenAI service for testing without real API calls"""

    def __init__(self, api_key: str = None, organization: str = None):
        self.api_key = api_key or "test-key"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
    ) -> Dict:
        """Generate a mock AI response for testing"""

        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # Generate a simple response based on the input
        responses = [
            "안녕하세요! 반갑습니다. 오늘 어떻게 도와드릴까요?",
            "네, 알겠습니다. 무엇을 도와드릴까요?",
            "좋은 질문입니다. 제가 도와드리겠습니다.",
            "교회 사역을 위해 최선을 다해 도와드리겠습니다.",
            "하나님의 은혜가 함께하시길 기도합니다.",
        ]

        # Check for specific keywords and provide context-aware responses
        if "안녕" in user_message:
            content = "안녕하세요! 저는 교회 사역을 돕는 AI 도우미입니다. 오늘 하루도 주님의 평안이 함께하시길 바랍니다. 😊"
        elif "날씨" in user_message:
            content = "오늘은 정말 좋은 날씨네요! 하나님이 주신 아름다운 하루입니다."
        elif "기도" in user_message:
            content = "함께 기도하겠습니다. 주님께서 우리의 기도를 들으시고 응답해 주실 것입니다."
        elif "헌금" in user_message and ("목표" in user_message or "계획" in user_message or "세울" in user_message or "설정" in user_message):
            content = """현재 교회 헌금 현황을 바탕으로 올해 목표를 제안드리겠습니다.

📊 **현재 현황 분석:**
- 올해 헌금 총액: 14,213,230원 (8월까지)
- 작년 동기 대비: -99% (작년 15억 → 올해 1,421만원)
- 월평균 헌금: 약 1,421만원
- 교인 1인당 월평균: 83,118원

💡 **목표 설정 제안:**
1. **보수적 목표**: 월 1,500만원 × 12개월 = 1억 8천만원
2. **성장 목표**: 월 2,000만원 × 12개월 = 2억 4천만원  
3. **도전 목표**: 월 2,500만원 × 12개월 = 3억원

**추천사항:**
- 171명 교인 기준으로 1인당 월 10-15만원 목표가 현실적
- 구역별 헌금 격려 프로그램 도입
- 분기별 목표 달성률 점검 및 조정

어떤 수준의 목표를 고려하고 계신가요?"""
        elif "지난달" in user_message and "헌금" in user_message:
            content = """지난달 헌금 현황을 알려드리겠습니다.

📈 **7월 헌금 현황:**
- 총 헌금액: 14,213,230원
- 전월 대비: 변동 없음 (0%)
- 십일조: 14,213,230원 (100%)
- 헌금 건수: 2건

**주요 헌금자:**
- 이유림: 12,222,222원 (십일조)
- 최믿음: 1,991,008원 (십일조)

교인 171명 기준 참여율이 매우 낮은 상황입니다. 헌금 참여 독려 방안을 검토해보시기 바랍니다."""
        elif "헌금" in user_message:
            content = """교회 헌금 관련 문의해주셔서 감사합니다.

📊 **올해 헌금 현황:**
- 총 헌금액: 14,213,230원 (8월까지)
- 교인 171명 기준 월평균 개인 헌금: 83,118원
- 주요 헌금 형태: 십일조 (100%)

💡 더 구체적인 정보가 필요하시면 다음과 같이 문의해 주세요:
- "올해 헌금 목표를 어떻게 세울까?"
- "지난달 헌금은 얼마나 됐나?"
- "헌금 참여율 현황이 어떻게 되나?"

어떤 부분이 궁금하신가요?"""
        else:
            content = random.choice(responses)

        # Ensure content is not empty
        if not content or content.strip() == "":
            content = "죄송합니다. 요청을 처리하는 중에 문제가 발생했습니다. 다시 시도해 주세요."
        
        # Calculate mock token usage
        tokens_used = len(user_message.split()) + len(content.split()) * 3

        # Log the generated response for debugging
        logger.info(f"Test OpenAI Service - User: '{user_message[:50]}...' -> Response: '{content[:100]}...'")

        return {
            "content": content,
            "tokens_used": tokens_used,
            "model": model,
            "finish_reason": "stop",
        }

    def generate_response_sync(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
    ) -> Dict:
        """Synchronous version of generate_response"""
        import asyncio

        return asyncio.run(
            self.generate_response(
                messages, model, max_tokens, temperature, system_prompt
            )
        )

    def calculate_cost(self, tokens: int, model: str = "gpt-4o-mini") -> float:
        """Calculate mock cost"""
        return tokens * 0.000001  # Very cheap for testing

    async def test_connection(self, api_key: str = None) -> bool:
        """Always return True for testing"""
        return True

    def analyze_message_intent(self, message: str) -> List[str]:
        """Analyze message intent"""
        required_data = []

        if "출석" in message or "결석" in message:
            required_data.append("attendance")
        if "성도" in message or "교인" in message:
            required_data.append("members")
        if "헌금" in message:
            required_data.append("donations")
        if "행사" in message or "예배" in message:
            required_data.append("events")

        return required_data


# Create a singleton instance
test_openai_service = TestOpenAIService()
