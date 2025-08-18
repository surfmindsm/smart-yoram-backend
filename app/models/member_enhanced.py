from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    BigInteger,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Code(Base):
    __tablename__ = "codes"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    type = Column(String, nullable=False)  # position, department, district, visit_type, marital_status
    code = Column(String, nullable=False)
    label = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="codes")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    postal_code = Column(String)
    address1 = Column(String)  # 기본주소
    address2 = Column(String)  # 상세주소
    sido = Column(String)  # 시/도
    sigungu = Column(String)  # 시/군/구
    eupmyeondong = Column(String)  # 읍/면/동
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    owner_type = Column(String, nullable=False)  # member, visit, report
    owner_id = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    mime_type = Column(String)
    bytes = Column(BigInteger)
    taken_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="files")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)  # create, update, delete, view, print
    diff = Column(Text)  # JSON format
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    church = relationship("Church", backref="audit_logs")
    actor = relationship("User", backref="audit_logs")


class MemberContact(Base):
    __tablename__ = "member_contacts"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    type = Column(String, nullable=False)  # phone, mobile, email
    value = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="contacts")


class MemberAddress(Base):
    __tablename__ = "member_addresses"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="member_addresses")
    address = relationship("Address", backref="member_addresses")


class MemberVehicle(Base):
    __tablename__ = "member_vehicles"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    car_type = Column(String)
    plate_no = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="vehicles")


class MemberFamily(Base):
    __tablename__ = "member_family"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    role = Column(String)  # 세대주, 배우자, 자녀
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church")
    family = relationship("Family", backref="member_relations")
    member = relationship("Member", backref="family_relations")


class MemberStatusHistory(Base):
    __tablename__ = "member_status_history"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(Date, nullable=False)
    ended_at = Column(Date)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="status_history")


class MemberMinistry(Base):
    __tablename__ = "member_ministry"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    department_code = Column(String)
    position_code = Column(String)
    appointed_on = Column(Date)
    ordination_church = Column(String)
    job_title = Column(String)
    workplace = Column(String)
    workplace_phone = Column(String)
    resign_on = Column(Date)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="ministries")


class MemberChurchSchool(Base):
    __tablename__ = "member_church_school"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    year = Column(Integer)
    grade = Column(String)
    ministry_code = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="church_school_records")


class Sacrament(Base):
    __tablename__ = "sacraments"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    type = Column(String, nullable=False)  # 세례, 입교, 유아세례, 성찬
    date = Column(Date)
    church_name = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="sacraments")


class Marriage(Base):
    __tablename__ = "marriages"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    status = Column(String)  # 미혼, 기혼, 사별, 이혼
    spouse_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    married_on = Column(Date)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", foreign_keys=[member_id], backref="marriage_records")
    spouse = relationship("Member", foreign_keys=[spouse_member_id])


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    type = Column(String, nullable=False)  # in, out
    church_name = Column(String)
    date = Column(Date)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="transfers")


class EducationNote(Base):
    __tablename__ = "education_notes"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    level_code = Column(String)
    memo = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    member = relationship("Member", backref="education_notes")