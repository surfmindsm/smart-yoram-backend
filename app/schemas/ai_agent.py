from typing import Optional, List, Union, Dict
from datetime import datetime
from pydantic import BaseModel


class ChurchDataSources(BaseModel):
    announcements: Optional[bool] = False
    attendances: Optional[bool] = False
    members: Optional[bool] = False
    worship_services: Optional[bool] = False


class OfficialAgentTemplateBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    icon: Optional[str] = "🤖"
    system_prompt: str
    church_data_sources: Optional[ChurchDataSources] = ChurchDataSources()
    is_public: Optional[bool] = True
    version: Optional[str] = "1.0.0"


class OfficialAgentTemplateCreate(OfficialAgentTemplateBase):
    pass


class OfficialAgentTemplateUpdate(OfficialAgentTemplateBase):
    name: Optional[str] = None
    category: Optional[str] = None
    system_prompt: Optional[str] = None


class OfficialAgentTemplate(OfficialAgentTemplateBase):
    id: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIAgentBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    detailed_description: Optional[str] = None
    icon: Optional[str] = "🤖"
    system_prompt: Optional[str] = None
    church_data_sources: Optional[ChurchDataSources] = ChurchDataSources()
    is_active: Optional[bool] = True


class AIAgentCreate(AIAgentBase):
    template_id: Optional[Union[int, str]] = None


class AIAgentUpdate(AIAgentBase):
    name: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class AIAgent(AIAgentBase):
    id: int
    church_id: int
    template_id: Optional[int] = None
    usage_count: int
    total_tokens_used: int
    total_cost: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIAgentWithStats(AIAgent):
    total_requests: Optional[int] = 0
    avg_tokens_per_request: Optional[float] = 0
    last_used: Optional[datetime] = None


class ChatHistoryBase(BaseModel):
    title: str
    is_bookmarked: Optional[bool] = False


class ChatHistoryCreate(ChatHistoryBase):
    agent_id: Union[int, str]


class ChatHistoryUpdate(ChatHistoryBase):
    title: Optional[str] = None
    is_bookmarked: Optional[bool] = None


class ChatHistory(ChatHistoryBase):
    id: int
    church_id: int
    user_id: int
    agent_id: int
    message_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    agent_name: Optional[str] = None

    class Config:
        from_attributes = True


class ChatHistoryWithMessages(ChatHistory):
    messages: Optional[List["ChatMessage"]] = []


class ChatMessageBase(BaseModel):
    content: str
    role: str  # 'user' or 'assistant'


class ChatMessageCreate(ChatMessageBase):
    chat_history_id: int
    agent_id: int


class ChatMessage(ChatMessageBase):
    id: int
    chat_history_id: int
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    chat_history_id: Optional[Union[int, str]] = None
    agent_id: Union[int, str]
    content: str
    role: Optional[str] = "user"
    messages: Optional[List[Dict]] = []
    create_history_if_needed: Optional[bool] = True  # Auto-create history if null

    # 🆕 비서 에이전트 균형 파라미터들
    church_data_context: Optional[str] = None  # 조회된 교회 데이터 (JSON 문자열)
    secretary_mode: Optional[bool] = False  # 비서 모드 활성화
    prioritize_church_data: Optional[bool] = False  # 교회 데이터 우선 처리
    fallback_to_general: Optional[bool] = True  # 교회 데이터 부족 시 일반 GPT 응답 허용


class ChatResponse(BaseModel):
    user_message: ChatMessage
    ai_response: ChatMessage
    data_sources: Optional[List[str]] = []
    church_data_context: Optional[Dict] = None

    # 🆕 비서 모드 응답 메타데이터
    is_secretary_agent: Optional[bool] = False
    query_type: Optional[str] = (
        "general_query"  # church_data_query, general_query, hybrid_response
    )
    church_data_used: Optional[bool] = False
    fallback_used: Optional[bool] = False


class ChurchDatabaseConfigBase(BaseModel):
    db_type: str  # 'mysql', 'postgresql', 'mssql'
    host: str
    port: int
    database_name: str
    username: str
    password: str


class ChurchDatabaseConfigCreate(ChurchDatabaseConfigBase):
    pass


class ChurchDatabaseConfigUpdate(ChurchDatabaseConfigBase):
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class ChurchDatabaseConfig(ChurchDatabaseConfigBase):
    id: int
    church_id: int
    is_active: bool
    last_sync: Optional[datetime] = None
    tables_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DatabaseTestResult(BaseModel):
    connected: bool
    tables_found: Optional[List[str]] = []
    error: Optional[str] = None
    last_sync: Optional[datetime] = None


class GPTConfigBase(BaseModel):
    api_key: str
    model: Optional[str] = "gpt-4"
    max_tokens: Optional[int] = 4000
    temperature: Optional[float] = 0.7


class GPTConfigUpdate(GPTConfigBase):
    api_key: Optional[str] = None


class ChurchProfile(BaseModel):
    id: int
    name: str
    subscription_plan: str
    max_agents: int
    current_agents_count: Optional[int] = 0
    gpt_api_configured: bool
    database_connected: Optional[bool] = False
    last_sync: Optional[datetime] = None
    monthly_usage: Optional[dict] = None

    class Config:
        from_attributes = True


class SystemStatus(BaseModel):
    gpt_api: dict
    database: dict
    agents: dict


class UsageStats(BaseModel):
    current_month: dict
    daily_usage: List[dict]
    agent_usage: List[dict]
