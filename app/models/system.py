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


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    name = Column(String, nullable=False)  # 집회명 (주일1부/2부/수요 등)
    date = Column(Date, nullable=False)  # 일자
    start_time = Column(DateTime(timezone=True))  # 시작 시간
    end_time = Column(DateTime(timezone=True))  # 종료 시간
    place = Column(String)  # 장소
    group_scope = Column(String)  # 대상 범위 (전체/구역/가족 정렬 기준 등)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="services")


class SearchPreset(Base):
    __tablename__ = "search_presets"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    name = Column(String, nullable=False)  # 프리셋 명
    query_json = Column(Text)  # 조건 JSON (교구/구역/정렬/사진포함 등)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="search_presets")


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    requester_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # 요청자
    template_code = Column(
        String, nullable=False
    )  # 양식 코드 (개인교적부/사진리스트/구역사진리스트 등)
    scope = Column(String)  # 대상 범위 (현재교인/검색된교인/선택교인/구역그룹 등)
    options_json = Column(
        Text
    )  # 옵션 JSON (최근심방 출력건수, 가족비고 자동늘리기, 사진포함 등)
    status = Column(String, default="pending")  # 상태 (대기/완료/실패)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="print_jobs")
    requester = relationship("User", backref="requested_print_jobs")


class StatsSnapshot(Base):
    __tablename__ = "stats_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    date = Column(Date, nullable=False)  # 기준일
    payload_json = Column(Text)  # 출결/심방/등록 등 집계 결과 JSON

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    church = relationship("Church", backref="stats_snapshots")
