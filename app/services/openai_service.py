from openai import OpenAI
import os
from typing import List, Dict, Optional
import logging
from app.core.config import settings
from app.core.security import decrypt_data, encrypt_data
import json

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, api_key: str = None, organization: str = None):
        """Initialize OpenAI service with optional custom API key"""
        if api_key:
            self.client = OpenAI(api_key=api_key, organization=organization)
        else:
            # Try to get from environment
            env_key = os.getenv("OPENAI_API_KEY")
            env_org = os.getenv("OPENAI_ORGANIZATION")
            if env_key:
                self.client = OpenAI(api_key=env_key, organization=env_org)
            else:
                self.client = None

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
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
        if not self.client:
            raise Exception("OpenAI client not initialized. Please provide an API key.")

        # Log request details for debugging
        logger.info(
            f"OpenAI Request - Model: {model}, Max Tokens: {max_tokens}, Temperature: {temperature}"
        )
        logger.info(f"Messages count: {len(messages)}")

        try:
            # Validate and normalize model name
            normalized_model = self._normalize_model_name(model)
            if normalized_model != model:
                logger.warning(f"Model '{model}' normalized to '{normalized_model}'")

            # Prepare messages
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            logger.debug(f"Calling OpenAI API with model: {normalized_model}")

            # Call OpenAI API using the new client
            # GPT-5 models have specific parameter requirements
            if normalized_model.startswith("gpt-5"):
                # GPT-5 models require specific parameters
                adjusted_temperature = 1.0  # GPT-5 only supports temperature=1.0
                if temperature != 1.0:
                    logger.warning(
                        f"🔧 GPT-5 Temperature 조정: {temperature} → 1.0 (모델 제약)"
                    )

                logger.info(
                    f"Using GPT-5 parameters - max_completion_tokens: {max_tokens}, temperature: 1.0"
                )
                response = self.client.chat.completions.create(
                    model=normalized_model,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=adjusted_temperature,
                )
            else:
                response = self.client.chat.completions.create(
                    model=normalized_model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            logger.info(f"OpenAI Response successful - Tokens used: {tokens_used}")
            logger.info(f"OpenAI Response content length: {len(content or '')}")
            logger.info(f"OpenAI Response content preview: '{(content or '')[:100]}...'")
            
            # Handle empty content
            if not content:
                logger.warning("OpenAI returned empty content, using fallback")
                content = "죄송합니다. 응답을 생성하는 중에 문제가 발생했습니다. 다시 시도해 주세요."

            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": normalized_model,
                "finish_reason": response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"OpenAI API Error Details:")
            logger.error(f"  Model: {model}")
            logger.error(f"  Error Type: {type(e).__name__}")
            logger.error(f"  Error Message: {str(e)}")

            error_str = str(e).lower()
            if (
                "authentication" in error_str
                or "api key" in error_str
                or "unauthorized" in error_str
            ):
                logger.error(f"OpenAI authentication error: {e}")
                raise Exception("GPT API 키가 유효하지 않습니다.")
            elif "rate limit" in error_str:
                logger.error(f"OpenAI rate limit error: {e}")
                raise Exception(
                    "API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
                )
            elif "invalid request" in error_str or "model" in error_str:
                logger.error(f"OpenAI invalid request/model error: {e}")
                # Try fallback to gpt-4o-mini if different model was requested
                # But don't fallback for GPT-5 models - user specifically wants GPT-5
                if (
                    model != "gpt-4o-mini"
                    and "model" in error_str
                    and not model.lower().startswith("gpt-5")
                ):
                    logger.warning(
                        f"Model '{model}' failed, trying fallback to gpt-4o-mini"
                    )
                    try:
                        response = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature,
                        )
                        content = response.choices[0].message.content
                        tokens_used = response.usage.total_tokens
                        logger.info(
                            f"Fallback successful with gpt-4o-mini - Tokens: {tokens_used}"
                        )
                        return {
                            "content": content,
                            "tokens_used": tokens_used,
                            "model": "gpt-4o-mini",
                            "finish_reason": response.choices[0].finish_reason,
                        }
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {fallback_error}")
                        raise Exception(
                            f"모델 '{model}'를 사용할 수 없습니다. 기본 모델로도 실패했습니다: {str(fallback_error)}"
                        )
                else:
                    # GPT-5 models or gpt-4o-mini failed without fallback
                    if model.lower().startswith("gpt-5"):
                        raise Exception(
                            f"GPT-5 모델 '{model}'은 아직 지원되지 않습니다. GPT-4o 또는 GPT-4o-mini를 사용해주세요."
                        )
                raise Exception(
                    f"잘못된 요청입니다. 모델 '{model}'를 확인해주세요: {str(e)}"
                )
            else:
                logger.error(f"OpenAI API error: {e}")
                raise Exception(f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}")

    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name to handle variations"""
        model_lower = model.lower().strip()

        # Handle common variations and typos (but preserve original GPT-5 models)
        if model_lower in ["gpt-5-mini", "gpt5-mini", "gpt-5mini"]:
            # Keep GPT-5 models as is - let OpenAI API handle availability
            logger.info(f"Using GPT-5 model as configured: {model}")
            return "gpt-5-mini"  # Use as configured
        elif model_lower in ["gpt-4o-mini", "gpt4o-mini", "gpt-4omini"]:
            return "gpt-4o-mini"
        elif model_lower in ["gpt-4o", "gpt4o", "gpt-4-omni"]:
            return "gpt-4o"
        elif model_lower in ["gpt-4", "gpt4"]:
            return "gpt-4"
        elif model_lower in ["gpt-3.5-turbo", "gpt3.5-turbo", "gpt-35-turbo"]:
            return "gpt-3.5-turbo"
        else:
            return model  # Return as-is if no normalization needed

    def generate_response_sync(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
    ) -> Dict:
        """Synchronous version of generate_response"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please provide an API key.")

        try:
            # Prepare messages
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            # Call OpenAI API
            # GPT-5 models have specific parameter requirements
            if model.startswith("gpt-5"):
                # GPT-5 models require specific parameters
                adjusted_temperature = 1.0  # GPT-5 only supports temperature=1.0
                if temperature != 1.0:
                    logger.warning(
                        f"🔧 GPT-5 Temperature 조정: {temperature} → 1.0 (모델 제약)"
                    )

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=adjusted_temperature,
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            return {
                "content": content,
                "tokens_used": tokens_used,
                "model": model,
                "finish_reason": response.choices[0].finish_reason,
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
            test_client = OpenAI(api_key=api_key) if api_key else self.client

            if not test_client:
                return False

            # Simple test request
            response = test_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
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
