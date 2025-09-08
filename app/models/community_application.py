"""
커뮤니티 회원 신청 모델
외부 업체/개인의 회원가입 신청을 관리
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class CommunityApplication(Base):
    """
    커뮤니티 회원 신청 테이블
    - 외부 업체, 연주자, 사역자 등의 회원가입 신청
    - 슈퍼어드민이 승인/반려 처리
    - 승인 시 자동으로 사용자 계정 생성
    """
    __tablename__ = "community_applications"

    # 기본 필드
    id = Column(Integer, primary_key=True, index=True)
    
    # 신청자 정보
    applicant_type = Column(String(20), nullable=False)  # company, individual, musician, minister, organization, other
    organization_name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    business_number = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=False)  # 상세 소개 및 신청 사유
    service_area = Column(String(200), nullable=True)
    website = Column(String(500), nullable=True)
    
    # 첨부파일 정보 (JSON)
    # [{"filename": "파일명", "path": "저장경로", "size": 크기, "mimetype": "타입"}]
    attachments = Column(JSON, nullable=True)
    
    # 신청 상태 관리
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending, approved, rejected
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # 검토 메모
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    reviewer = relationship("User", back_populates="reviewed_applications")
    
    # 편의 메서드
    @property
    def is_pending(self):
        return self.status == "pending"
    
    @property
    def is_approved(self):
        return self.status == "approved"
    
    @property
    def is_rejected(self):
        return self.status == "rejected"
    
    @property
    def applicant_type_display(self):
        """신청자 유형 한글 표시"""
        type_map = {
            "company": "업체/회사",
            "individual": "개인",
            "musician": "연주자/찬양사역자",
            "minister": "목회자/사역자",
            "organization": "단체/기관",
            "other": "기타"
        }
        return type_map.get(self.applicant_type, self.applicant_type)
    
    @property
    def status_display(self):
        """상태 한글 표시"""
        status_map = {
            "pending": "검토 대기",
            "approved": "승인",
            "rejected": "반려"
        }
        return status_map.get(self.status, self.status)
    
    def __repr__(self):
        return f"<CommunityApplication(id={self.id}, organization={self.organization_name}, status={self.status})>"