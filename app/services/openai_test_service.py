"""
Test OpenAI service that returns mock responses
"""
import random
from typing import List, Dict


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
        system_prompt: str = None
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
            "하나님의 은혜가 함께하시길 기도합니다."
        ]
        
        # Check for specific keywords
        if "안녕" in user_message:
            content = "안녕하세요! 저는 교회 사역을 돕는 AI 도우미입니다. 오늘 하루도 주님의 평안이 함께하시길 바랍니다. 😊"
        elif "날씨" in user_message:
            content = "오늘은 정말 좋은 날씨네요! 하나님이 주신 아름다운 하루입니다."
        elif "기도" in user_message:
            content = "함께 기도하겠습니다. 주님께서 우리의 기도를 들으시고 응답해 주실 것입니다."
        else:
            content = random.choice(responses)
        
        # Calculate mock token usage
        tokens_used = len(user_message.split()) + len(content.split()) * 3
        
        return {
            "content": content,
            "tokens_used": tokens_used,
            "model": model,
            "finish_reason": "stop"
        }
    
    def generate_response_sync(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> Dict:
        """Synchronous version of generate_response"""
        import asyncio
        return asyncio.run(self.generate_response(
            messages, model, max_tokens, temperature, system_prompt
        ))
    
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