from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class FamilyRelationship(Base):
    __tablename__ = "family_relationships"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    related_member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    relationship_type = Column(String, nullable=False)  # 부모, 자녀, 배우자, 형제, 자매 등
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    church = relationship("Church")
    member = relationship("Member", foreign_keys=[member_id])
    related_member = relationship("Member", foreign_keys=[related_member_id])