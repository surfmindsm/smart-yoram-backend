from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class DailyVerse(Base):
    __tablename__ = "daily_verses"

    id = Column(Integer, primary_key=True, index=True)
    verse = Column(Text, nullable=False, comment="성경 구절 내용")
    reference = Column(String(100), nullable=False, comment="성경 구절 출처 (예: 시편 23:1)")
    is_active = Column(Boolean, default=True, comment="활성 상태")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
