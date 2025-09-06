from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index, BigInteger, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class ActionType(enum.Enum):
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    LOGIN = "login"
    LOGOUT = "logout"


class ResourceType(enum.Enum):
    MEMBER = "member"
    ATTENDANCE = "attendance"
    FINANCIAL = "financial"
    BULLETIN = "bulletin"
    ANNOUNCEMENT = "announcement"
    SYSTEM = "system"
    USER = "user"
    CHURCH = "church"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    # Basic keys
    id = Column(BigInteger, primary_key=True, index=True)
    
    # User information
    user_id = Column(String(50), nullable=False)
    session_id = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Activity classification
    action = Column(Enum(ActionType), nullable=False)
    resource = Column(Enum(ResourceType), nullable=False)
    
    # Target information
    target_id = Column(String(50))
    target_name = Column(String(100))
    
    # Page/Location information
    page_path = Column(String(200), nullable=False)
    page_name = Column(String(100), nullable=False)
    
    # Detailed information (JSON)
    details = Column(JSON)
    sensitive_data = Column(JSON)  # List of sensitive data fields accessed/modified
    
    # Network information
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Performance optimization indexes
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_action_resource', 'action', 'resource'),
        Index('idx_target', 'target_id', 'resource'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_ip_address', 'ip_address'),
        Index('idx_user_action_date', 'user_id', 'action', func.date('timestamp')),
        Index('idx_resource_target', 'resource', 'target_id'),
    )