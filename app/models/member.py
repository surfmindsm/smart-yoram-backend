from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Basic Information
    code = Column(String, unique=True)  # 교번 (내부 일련번호)
    name = Column(String, nullable=False)
    name_eng = Column(String)  # 영문 이름
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    latitude = Column(Float)  # 위도
    longitude = Column(Float)  # 경도
    photo_url = Column(String)
    photo_file_id = Column(
        Integer, ForeignKey("files.id"), nullable=True
    )  # 프로필 사진

    # Personal Details
    birthdate = Column(Date)
    age = Column(Integer)  # 나이 (뷰/캐시용)
    gender = Column(String)  # M, F
    marital_status = Column(String)  # single, married, divorced, widowed

    # Church Information
    position = Column(String)  # 직분: pastor, elder, deacon, member, youth, child
    department = Column(String)  # 부서
    district = Column(String)  # 구역
    baptism_date = Column(Date)
    baptism_church = Column(String)
    registration_date = Column(Date)
    registration_background = Column(Text)  # 등록 배경/경위

    # Family Information
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    family_role = Column(String)  # head, spouse, child, other
    head_relationship = Column(String)  # 세대주와의 관계
    is_new_family_head = Column(Boolean, default=False)  # 신앙세대주 여부

    # Inviter Information
    inviter1_member_id = Column(
        Integer, ForeignKey("members.id"), nullable=True
    )  # 인도자1
    inviter2_member_id = Column(
        Integer, ForeignKey("members.id"), nullable=True
    )  # 인도자2

    # Enhanced Church Information (레퍼런스 요구사항) - TEMPORARILY DISABLED
    # These fields will be added back after database migration
    # member_type = Column(String)  # 교인구분: FULL_MEMBER, CONFIRMED_MEMBER, etc
    # confirmation_date = Column(Date)  # 입교일
    # sub_district = Column(String)  # 부구역
    # age_group = Column(String)  # 나이그룹: ADULT, YOUTH, CHILD, SENIOR
    
    # Regional Information - TEMPORARILY DISABLED
    # region_1 = Column(String)  # 안도구 1
    # region_2 = Column(String)  # 안도구 2  
    # region_3 = Column(String)  # 안도구 3
    
    # Third Inviter - TEMPORARILY DISABLED
    # inviter3_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    
    # Contact Details - TEMPORARILY DISABLED
    # postal_code = Column(String)  # 우편번호
    # last_contact_date = Column(Date)  # 통화일
    
    # Spiritual Information - TEMPORARILY DISABLED
    # spiritual_grade = Column(String)  # 신급: GRADE_A, GRADE_B, etc
    
    # Enhanced Job Information - TEMPORARILY DISABLED
    # job_category = Column(String)  # 직업분류: OFFICE_WORKER, TEACHER, etc
    # job_detail = Column(String)  # 구체적 업무
    # job_position = Column(String)  # 직책/직위
    
    # Ministry Information - TEMPORARILY DISABLED
    # ministry_start_date = Column(Date)  # 장업일
    # neighboring_church = Column(String)  # 이웃교회
    # position_decision = Column(String)  # 직관결정
    # daily_activity = Column(Text)  # 매일 활동
    
    # Custom Fields (자유1~자유12) - TEMPORARILY DISABLED
    # custom_field_1 = Column(String)
    # custom_field_2 = Column(String)
    # custom_field_3 = Column(String)
    # custom_field_4 = Column(String)
    # custom_field_5 = Column(String)
    # custom_field_6 = Column(String)
    # custom_field_7 = Column(String)
    # custom_field_8 = Column(String)
    # custom_field_9 = Column(String)
    # custom_field_10 = Column(String)
    # custom_field_11 = Column(String)
    # custom_field_12 = Column(String)
    
    # Special Notes - TEMPORARILY DISABLED
    # special_notes = Column(Text)  # 개인 특별 사항

    # Status and Notes
    status = Column(String, default="active")  # active, inactive, transferred
    notes = Column(Text)
    memo = Column(Text)  # 메모

    # Enhanced fields for app features
    profile_photo_url = Column(String)
    member_status = Column(
        String, default="active"
    )  # active, inactive, transferred, absent, visiting
    transfer_church = Column(String)
    transfer_date = Column(Date)
    invitation_sent = Column(Boolean, default=False)
    invitation_sent_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="members")
    user = relationship("User", backref="member_profile")
    family = relationship("Family", foreign_keys=[family_id], backref="members")

    # Self-referential relationships for inviters
    inviter1 = relationship(
        "Member", foreign_keys=[inviter1_member_id], remote_side=[id]
    )
    inviter2 = relationship(
        "Member", foreign_keys=[inviter2_member_id], remote_side=[id]
    )
    inviter3 = relationship(
        "Member", foreign_keys=[inviter3_member_id], remote_side=[id]
    )


class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    family_name = Column(String, nullable=False)
    head_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    address = Column(String)
    latitude = Column(Float)  # 위도
    longitude = Column(Float)  # 경도
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    church = relationship("Church", backref="families")
