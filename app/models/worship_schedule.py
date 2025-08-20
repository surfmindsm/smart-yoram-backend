from sqlalchemy import Column, Integer, String, Time, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class WorshipService(Base):
    """예배 서비스 정보"""

    __tablename__ = "worship_services"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    name = Column(String(100), nullable=False)  # 예배 이름 (예: 주일예배 1부)
    location = Column(String(100))  # 장소 (예: 예루살렘성전)
    day_of_week = Column(Integer)  # 요일 (0: 월요일, 6: 일요일)
    start_time = Column(Time, nullable=False)  # 시작 시간
    end_time = Column(Time)  # 종료 시간
    service_type = Column(String(50))  # 예배 유형 (주일예배, 수요예배, 새벽기도회 등)
    target_group = Column(String(50))  # 대상 그룹 (전체, 어린이부, 청소년부 등)
    is_online = Column(Boolean, default=False)  # 온라인 여부
    is_active = Column(Boolean, default=True)  # 활성화 여부
    order_index = Column(Integer, default=0)  # 표시 순서

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="worship_services")


class WorshipServiceCategory(Base):
    """예배 카테고리 (주일예배, 수요예배, 새벽기도회 등)"""

    __tablename__ = "worship_service_categories"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    order_index = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church", back_populates="worship_categories")
