from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class SermonMaterial(Base):
    """설교 자료 모델"""

    __tablename__ = "sermon_materials"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), index=True)  # 설교자 이름
    content = Column(Text)  # 설교 내용/요약
    file_url = Column(String(500))  # 업로드된 파일 경로
    file_type = Column(String(50))  # pdf, docx, txt, mp3, mp4 등
    file_size = Column(Integer)  # 파일 크기 (bytes)
    category = Column(String(100), index=True)  # 주제별 분류
    scripture_reference = Column(String(200))  # 성경 구절 참조
    date_preached = Column(Date, index=True)  # 설교 날짜
    tags = Column(JSON, default=[])  # 검색용 태그 (JSON array of strings)
    is_public = Column(Boolean, default=False, index=True)  # 공개/비공개
    view_count = Column(Integer, default=0)  # 조회수
    download_count = Column(Integer, default=0)  # 다운로드수
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    church = relationship("Church", back_populates="sermon_materials")
    user = relationship("User", back_populates="sermon_materials")


class SermonCategory(Base):
    """설교 카테고리 모델"""

    __tablename__ = "sermon_categories"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500))
    color = Column(String(7), default="#3B82F6")  # 색상 코드
    order_index = Column(Integer, default=0)  # 정렬 순서
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    church = relationship("Church")
