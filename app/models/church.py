from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Church(Base):
    __tablename__ = "churches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    pastor_name = Column(String)

    subscription_status = Column(String, default="trial")  # trial, active, expired
    subscription_end_date = Column(DateTime)
    member_limit = Column(Integer, default=100)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    worship_services = relationship("WorshipService", back_populates="church")
    worship_categories = relationship("WorshipServiceCategory", back_populates="church")
