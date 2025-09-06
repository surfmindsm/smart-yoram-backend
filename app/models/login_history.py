from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class LoginHistory(Base):
    __tablename__ = "user_login_history"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Login details
    login_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text)
    device = Column(String(255))
    location = Column(String(255))
    status = Column(String(20), default="success", nullable=False)  # success, failed
    
    # Session tracking
    session_start = Column(DateTime(timezone=True))
    session_end = Column(DateTime(timezone=True))
    session_duration = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="login_histories")

    # Indexes
    __table_args__ = (
        Index('idx_user_id_login_time', 'user_id', 'login_time'),
    )