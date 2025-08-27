from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class OfficialAgentTemplate(Base):
    __tablename__ = "official_agent_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    detailed_description = Column(Text)
    icon = Column(String(10), default="🤖")
    system_prompt = Column(Text, nullable=False)
    church_data_sources = Column(JSON, default={})
    is_public = Column(Boolean, default=True)
    version = Column(String(20), default="1.0.0")
    created_by = Column(String(255), default="Smart Yoram Team")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    agents = relationship("AIAgent", back_populates="template")


class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    template_id = Column(
        Integer, ForeignKey("official_agent_templates.id"), nullable=True
    )
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    detailed_description = Column(Text)
    icon = Column(String(10), default="🤖")
    system_prompt = Column(Text)
    church_data_sources = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # 기본 에이전트 여부
    enable_church_data = Column(Boolean, default=False)  # 교회 데이터 조회 기능 활성화
    created_by_system = Column(Boolean, default=False)  # 시스템에서 자동 생성된 에이전트
    
    # GPT 설정 (에이전트별 개별 설정)
    gpt_model = Column(String(50), nullable=True)  # None이면 교회 설정 사용
    max_tokens = Column(Integer, nullable=True)
    temperature = Column(Float, nullable=True)
    
    usage_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="ai_agents")
    template = relationship("OfficialAgentTemplate", back_populates="agents")
    chat_histories = relationship("ChatHistory", back_populates="agent")


class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("ai_agents.id"), nullable=False)
    title = Column(String(255), nullable=False)
    is_bookmarked = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="chat_histories")
    user = relationship("User", back_populates="chat_histories")
    agent = relationship("AIAgent", back_populates="chat_histories")
    messages = relationship(
        "ChatMessage", back_populates="chat_history", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_history_id = Column(Integer, ForeignKey("chat_histories.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chat_history = relationship("ChatHistory", back_populates="messages")


class ChurchDatabaseConfig(Base):
    __tablename__ = "church_database_configs"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), unique=True, nullable=False)
    db_type = Column(String(50))  # 'mysql', 'postgresql', 'mssql'
    host = Column(String(255))
    port = Column(Integer)
    database_name = Column(String(255))
    username = Column(String(255))
    password = Column(Text)  # Encrypted
    connection_string = Column(Text)  # Encrypted
    is_active = Column(Boolean, default=False)
    last_sync = Column(DateTime(timezone=True))
    tables_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="database_config")
