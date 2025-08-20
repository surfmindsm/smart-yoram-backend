from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Offering(Base):
    __tablename__ = "offerings"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(
        Integer, ForeignKey("members.id"), nullable=False
    )  # 교인 직접 참조
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    offered_on = Column(Date, nullable=False)  # 헌금일자
    fund_type = Column(String, nullable=False)  # 헌금유형 (십일조, 감사, 건축 등)
    amount = Column(DECIMAL(15, 2), nullable=False)  # 금액
    note = Column(Text)  # 적요 (비고)
    input_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 입력자

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="offerings")
    church = relationship("Church", backref="offerings")
    input_user = relationship("User", backref="input_offerings")


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    member_id = Column(
        Integer, ForeignKey("members.id"), nullable=False
    )  # 교인 직접 참조
    tax_year = Column(Integer, nullable=False)  # 귀속연도
    issue_no = Column(String, nullable=False)  # 일련번호 (교회별 연도 단위 고유번호)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # 발급자
    issued_at = Column(DateTime(timezone=True), nullable=False)  # 발급일
    canceled_at = Column(DateTime(timezone=True))  # 취소일 (있으면 무효 처리)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="receipts")
    member = relationship("Member", backref="receipts")
    issuer = relationship("User", backref="issued_receipts")


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    offering_id = Column(Integer, ForeignKey("offerings.id"), nullable=False)
    fund_code = Column(String, default="41")  # 코드 (41: 종교단체기부금 등)
    description = Column(String)  # 적요 (십일조, 감사헌금 등)
    amount = Column(DECIMAL(15, 2), nullable=False)  # 금액

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    receipt = relationship("Receipt", backref="items")
    offering = relationship("Offering", backref="receipt_items")


class ReceiptSnapshot(Base):
    __tablename__ = "receipt_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    member_name = Column(String, nullable=False)  # 발급 시점의 교인 성명
    member_rrn_masked = Column(String)  # 주민등록번호(마스킹 처리)
    member_address = Column(String)  # 주소 문자열
    church_name = Column(String, nullable=False)  # 교회명
    church_business_no = Column(String)  # 교회 사업자번호
    total_amount = Column(DECIMAL(15, 2), nullable=False)  # 총액

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    receipt = relationship("Receipt", backref="snapshot")


class FundType(Base):
    __tablename__ = "fund_types"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    code = Column(String, nullable=False)  # 고유 코드
    name = Column(String, nullable=False)  # 표시명 (십일조, 감사헌금, 건축헌금 등)
    description = Column(Text)  # 상세 설명
    is_active = Column(Boolean, default=True)  # 활성 상태
    sort_order = Column(Integer, default=0)  # 정렬 순서

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="fund_types")


class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    report_type = Column(String, nullable=False)  # monthly, yearly, custom
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    summary_data = Column(Text)  # JSON 형태의 집계 데이터

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    church = relationship("Church", backref="financial_reports")
    generator = relationship("User", backref="generated_financial_reports")
