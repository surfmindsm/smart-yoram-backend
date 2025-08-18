from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    date = Column(Date, nullable=False)  # 심방 날짜
    place = Column(String)  # 장소
    term_year = Column(Integer)  # 해당년도
    term_unit = Column(String)  # 단기/회기 등 단위
    category_code = Column(String)  # 심방구분 (가정/병원/전화/방문 등)
    visit_type_code = Column(String)  # 방문심방/전화심방 등
    hymn_no = Column(String)  # 찬송가 번호
    scripture = Column(String)  # 성경말씀
    notes = Column(Text)  # 심방내역 (본문 메모)
    grade = Column(String)  # 등급 (보고용 분류)
    pastor_comment = Column(Text)  # 교역자 의견
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="visits")


class VisitPeople(Base):
    __tablename__ = "visit_people"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)
    role = Column(String, nullable=False)  # visitor1, visitor2, visitor3, accompanist, target
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)  # 교인 ID
    name = Column(String)  # 비회원/외부자 이름 (선택)
    district_code = Column(String)  # 대상자 구역/교구 코드
    position_code = Column(String)  # 직분 코드 (대상자 직분)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    visit = relationship("Visit", backref="people")
    member = relationship("Member", backref="visit_records")


class VisitIndex(Base):
    __tablename__ = "visits_index"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)  # 주요 대상 교인
    term_start = Column(Date)  # 회계/회기 시작일
    term_end = Column(Date)  # 회계/회기 종료일
    has_family = Column(Boolean, default=False)  # 가족포함 여부
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    visit = relationship("Visit")
    member = relationship("Member")


class DailyMinistryReport(Base):
    __tablename__ = "daily_ministry_reports"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    worker_member_id = Column(Integer, ForeignKey("members.id"), nullable=False)  # 보고자 (심방자)
    date = Column(Date, nullable=False)  # 보고일자
    plan = Column(Text)  # 일일사역계획
    report = Column(Text)  # 일일사역보고
    attendance_summary = Column(Text)  # 참석/심방 요약 (텍스트)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="daily_ministry_reports")
    worker = relationship("Member", backref="ministry_reports")


class DailyMinistryLink(Base):
    __tablename__ = "daily_ministry_links"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("daily_ministry_reports.id"), nullable=False)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("DailyMinistryReport", backref="visit_links")
    visit = relationship("Visit", backref="report_links")