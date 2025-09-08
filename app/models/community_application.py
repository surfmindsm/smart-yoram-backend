from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base


class CommunityApplication(Base):
    """
    커뮤니티 회원 신청서 모델
    SQLite 호환성을 위해 ENUM 대신 String 타입 사용
    """
    __tablename__ = "community_applications"
    
    # 기본 키 (SQLite 호환)
    id = Column(Integer, primary_key=True, index=True)
    
    # 신청자 정보 (String 타입으로 안전하게)
    applicant_type = Column(String(20), nullable=False)  # 'company', 'individual', 'musician', etc.
    organization_name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=False)  
    email = Column(String(255), nullable=False, index=True)  # 검색용 인덱스
    phone = Column(String(20), nullable=False)
    
    # 선택 정보
    business_number = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    service_area = Column(String(200), nullable=True)
    website = Column(String(500), nullable=True)
    
    # 첨부파일 정보 (JSON 문자열로 저장 - SQLite 호환)
    attachments = Column(Text, nullable=True)  # JSON string
    
    # 상태 관리 (String 타입)
    status = Column(String(20), default='pending', nullable=False)  # 'pending', 'approved', 'rejected'
    
    # 시간 정보
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 검토 관련
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # 생성/수정 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)