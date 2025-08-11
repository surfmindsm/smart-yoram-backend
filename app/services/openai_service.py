import openai
import os
from typing import List, Dict, Optional
import logging
from app.core.config import settings
from app.core.security import decrypt_data, encrypt_data
import json
import asyncio

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: str = None, organization: str = None):
        """Initialize OpenAI service with optional custom API key"""
        if api_key:
            self.api_key = api_key
            openai.api_key = api_key
        else:
            # Try to get from environment
            env_key = os.getenv("OPENAI_API_KEY")
            if env_key:
                self.api_key = env_key
                openai.api_key = env_key
            else:
                self.api_key = None
            
        if organization:
            openai.organization = organization
        else:
            # Try to get from environment
            env_org = os.getenv("OPENAI_ORGANIZATION")
            if env_org:
                openai.organization = env_org
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> Dict:
        """
        Generate AI response using OpenAI API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-1)
            system_prompt: System prompt to prepend
            
        Returns:
            Dictionary with response content and metadata
        """
        if not self.api_key:
            raise Exception("OpenAI API key not configured. Please provide an API key.")
            
        try:
            # Set the API key for this request
            openai.api_key = self.api_key
            
            # Prepare messages
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            # Call OpenAI API - using sync version in async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": model,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except openai.error.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise Exception("GPT API 키가 유효하지 않습니다.")
            
        except openai.error.RateLimitError as e:
            logger.error(f"OpenAI rate limit error: {e}")
            raise Exception("API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
            
        except openai.error.InvalidRequestError as e:
            logger.error(f"OpenAI invalid request: {e}")
            raise Exception(f"잘못된 요청입니다: {str(e)}")
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}")
    
    def generate_response_sync(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> Dict:
        """Synchronous version of generate_response"""
        if not self.api_key:
            raise Exception("OpenAI API key not configured. Please provide an API key.")
            
        try:
            # Set the API key for this request
            openai.api_key = self.api_key
            
            # Prepare messages
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": model,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def calculate_cost(self, tokens: int, model: str = "gpt-4o-mini") -> float:
        """
        Calculate cost based on token usage
        
        Pricing (as of 2024):
        - GPT-4o-mini: $0.00015 per 1K input tokens, $0.0006 per 1K output tokens
        - GPT-4o: $0.005 per 1K input tokens, $0.015 per 1K output tokens
        - GPT-4: $0.03 per 1K input tokens, $0.06 per 1K output tokens
        - GPT-3.5-turbo: $0.0005 per 1K input tokens, $0.0015 per 1K output tokens
        """
        if model == "gpt-4o-mini":
            # Average of input and output pricing for GPT-4o-mini
            cost_per_1k = 0.000375  # ($0.00015 + $0.0006) / 2
        elif model == "gpt-4o":
            # Average of input and output pricing for GPT-4o
            cost_per_1k = 0.01  # ($0.005 + $0.015) / 2
        elif model.startswith("gpt-4"):
            # Approximate average of input and output pricing
            cost_per_1k = 0.045
        elif model.startswith("gpt-3.5"):
            cost_per_1k = 0.001  # ($0.0005 + $0.0015) / 2
        else:
            cost_per_1k = 0.02  # Default fallback
        
        return (tokens / 1000) * cost_per_1k
    
    async def test_connection(self, api_key: str = None) -> bool:
        """Test if the API key is valid"""
        try:
            test_key = api_key or self.api_key
            if not test_key:
                return False
                
            openai.api_key = test_key
            
            # Simple test request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
            )
            return True
            
        except Exception as e:
            logger.error(f"API key test failed: {e}")
            return False
    
    def analyze_message_intent(self, message: str) -> List[str]:
        """
        Analyze user message to determine what church data might be needed
        
        Returns:
            List of data types needed (e.g., ['attendance', 'members'])
        """
        required_data = []
        
        # Keywords for different data types
        attendance_keywords = ["출석", "결석", "참석", "예배참여", "출석률"]
        member_keywords = ["성도", "교인", "회원", "연락처", "전화번호", "주소"]
        donation_keywords = ["헌금", "십일조", "감사헌금", "건축헌금", "재정"]
        event_keywords = ["행사", "예배", "모임", "일정", "스케줄"]
        
        message_lower = message.lower()
        
        if any(keyword in message for keyword in attendance_keywords):
            required_data.append("attendance")
        
        if any(keyword in message for keyword in member_keywords):
            required_data.append("members")
        
        if any(keyword in message for keyword in donation_keywords):
            required_data.append("donations")
        
        if any(keyword in message for keyword in event_keywords):
            required_data.append("events")
        
        return required_data


# Create a singleton instance with environment key if available
openai_service = OpenAIService()