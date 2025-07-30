from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    
    code = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    qr_type = Column(String, default="attendance")  # attendance, member_card
    
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    church = relationship("Church", backref="qr_codes")
    member = relationship("Member", backref="qr_codes")