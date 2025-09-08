from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base


class CommunityApplication(Base):
    __tablename__ = "community_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 신청자 정보 - ENUM 대신 String 사용 (SQLite 호환)
    applicant_type = Column(String(50), nullable=False, comment='신청자 유형: company, individual, musician, minister, organization, other')
    organization_name = Column(String(200), nullable=False, comment='단체/회사명')
    contact_person = Column(String(100), nullable=False, comment='담당자명')
    email = Column(String(255), nullable=False, comment='이메일')
    phone = Column(String(50), nullable=False, comment='연락처')
    business_number = Column(String(50), nullable=True, comment='사업자등록번호')
    address = Column(Text, nullable=True, comment='주소')
    description = Column(Text, nullable=False, comment='상세 소개 및 신청 사유')
    service_area = Column(String(200), nullable=True, comment='서비스 지역')
    website = Column(String(500), nullable=True, comment='웹사이트/SNS')
    
    # 첨부파일 - JSON 대신 Text로 JSON 문자열 저장 (SQLite 호환)
    attachments = Column(Text, nullable=True, comment='첨부파일 정보 JSON 문자열')
    
    # 상태 관리 - ENUM 대신 String 사용
    status = Column(String(20), default='pending', nullable=False, comment='신청 상태: pending, approved, rejected')
    
    # 시간 정보
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment='신청일시')
    reviewed_at = Column(DateTime(timezone=True), nullable=True, comment='검토일시')
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment='검토자 ID')
    rejection_reason = Column(Text, nullable=True, comment='반려 사유')
    notes = Column(Text, nullable=True, comment='검토 메모')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())