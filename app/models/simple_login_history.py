from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class LoginHistory(Base):
    """
    매우 단순한 로그인 기록 테이블
    - 복잡한 JSON, Enum 타입 제거
    - 필수 필드만 포함
    - 실패해도 기존 로그인에 영향 없도록 설계
    """
    __tablename__ = "login_history"

    # 기본 필드 (필수)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 로그인 정보 (단순)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)  # 브라우저 정보
    
    # 상태 (단순)
    status = Column(String(20), default="success", nullable=False)  # success, failed
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    location = Column(String(200), nullable=True)  # 위치 정보 (IP 기반)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 관계 (단순)
    user = relationship("User", back_populates="login_records")
    
    # 인덱스 (성능)
    # SQLAlchemy가 자동으로 생성할 인덱스들
    # - Primary key: id
    # - Foreign key: user_id
    # 추가 인덱스는 migration에서 생성