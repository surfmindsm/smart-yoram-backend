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


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    photo_url = Column(String)

    birthdate = Column(Date)
    gender = Column(String)  # M, F
    marital_status = Column(String)  # single, married, divorced, widowed

    position = Column(String)  # 직분: pastor, elder, deacon, member, youth, child
    department = Column(String)  # 부서
    district = Column(String)  # 구역

    baptism_date = Column(Date)
    baptism_church = Column(String)
    registration_date = Column(Date)

    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    family_role = Column(String)  # head, spouse, child, other

    status = Column(String, default="active")  # active, inactive, transferred
    notes = Column(Text)
    
    # New fields for enhanced features
    profile_photo_url = Column(String)
    member_status = Column(String, default="active")  # active, inactive, transferred, absent, visiting
    transfer_church = Column(String)
    transfer_date = Column(Date)
    memo = Column(Text)
    invitation_sent = Column(Boolean, default=False)
    invitation_sent_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="members")
    user = relationship("User", backref="member_profile")
    family = relationship("Family", foreign_keys=[family_id], backref="members")


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    family_name = Column(String, nullable=False)
    head_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    address = Column(String)
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="families")
