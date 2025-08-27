"""
스마트 AI 어시스턴트 관련 Pydantic 스키마
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class SmartAssistantQuery(BaseModel):
    """스마트 어시스턴트 질의 요청 스키마"""
    
    message: str = Field(..., description="사용자 질문", min_length=1, max_length=1000)
    model: Optional[str] = Field(None, description="사용할 GPT 모델 (기본값: 교회 설정)")
    max_tokens: Optional[int] = Field(None, description="최대 토큰 수", ge=100, le=4000)
    temperature: Optional[float] = Field(None, description="응답 창의성 (0.0-1.0)", ge=0.0, le=1.0)
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('질문을 입력해주세요.')
        return v.strip()


class SmartAssistantResponse(BaseModel):
    """스마트 어시스턴트 응답 스키마"""
    
    response: str = Field(..., description="AI 생성 응답")
    query_type: str = Field(..., description="질문 유형 (분류된 의도)")
    data_sources: List[str] = Field(default=[], description="응답에 사용된 데이터 소스 목록")
    tokens_used: int = Field(default=0, description="사용된 토큰 수")
    model: str = Field(..., description="사용된 GPT 모델")
    success: bool = Field(default=True, description="처리 성공 여부")
    error_message: Optional[str] = Field(None, description="오류 메시지 (실패시)")


class QueryAnalysisResponse(BaseModel):
    """질문 분석 결과 스키마"""
    
    primary_intent: str = Field(..., description="주요 의도")
    secondary_intents: List[str] = Field(default=[], description="부차적 의도들")
    time_context: str = Field(..., description="시간적 맥락 (today, tomorrow, this_week 등)")
    confidence: int = Field(..., description="분석 신뢰도 점수")
    detected_keywords: List[str] = Field(default=[], description="감지된 키워드들")
    suggested_data_sources: List[str] = Field(default=[], description="권장 데이터 소스들")


class AssistantCapability(BaseModel):
    """어시스턴트 기능 정의 스키마"""
    
    description: str = Field(..., description="기능 설명")
    examples: List[str] = Field(..., description="사용 예시들")


class AssistantCapabilitiesResponse(BaseModel):
    """어시스턴트 지원 기능 목록 응답 스키마"""
    
    supported_queries: Dict[str, AssistantCapability] = Field(..., description="지원 질의 유형들")
    time_contexts: List[str] = Field(..., description="지원하는 시간 맥락들")
    data_sources: List[str] = Field(..., description="사용 가능한 데이터 소스들")
    privacy_note: str = Field(..., description="개인정보 보호 안내")


class UsageStatistics(BaseModel):
    """사용 통계 응답 스키마"""
    
    church_id: int = Field(..., description="교회 ID")
    church_name: str = Field(..., description="교회명")
    current_month_tokens: int = Field(..., description="이번달 사용 토큰 수")
    current_month_cost: float = Field(..., description="이번달 사용 비용 (USD)")
    monthly_token_limit: int = Field(..., description="월 토큰 한도")
    token_usage_percentage: float = Field(..., description="토큰 사용률 (%)")
    gpt_model: str = Field(..., description="사용중인 GPT 모델")
    api_key_configured: bool = Field(..., description="API 키 설정 여부")
    subscription_plan: str = Field(..., description="구독 플랜")


class ContextData(BaseModel):
    """컨텍스트 데이터 스키마 (내부 사용)"""
    
    pastoral_visits: Optional[List[Dict[str, Any]]] = Field(None, description="심방 일정")
    prayer_requests: Optional[List[Dict[str, Any]]] = Field(None, description="기도 요청")
    announcements: Optional[List[Dict[str, Any]]] = Field(None, description="공지사항")
    visit_reports: Optional[List[Dict[str, Any]]] = Field(None, description="심방 보고서")
    member_info: Optional[Dict[str, Any]] = Field(None, description="성도 정보")
    error: Optional[str] = Field(None, description="데이터 수집 오류")


class QueryIntentAnalysis(BaseModel):
    """질문 의도 분석 결과 (내부 사용)"""
    
    primary_intent: str = Field(..., description="주요 의도")
    secondary_intents: List[str] = Field(default=[], description="부차적 의도들")
    time_context: str = Field(..., description="시간적 맥락")
    confidence: int = Field(..., description="신뢰도 점수")
    original_message: str = Field(..., description="원본 메시지")