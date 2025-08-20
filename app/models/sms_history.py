from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class SMSHistory(Base):
    __tablename__ = "sms_history"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    recipient_phone = Column(String, nullable=False)
    recipient_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)

    message = Column(Text, nullable=False)
    sms_type = Column(String)  # invitation, notice, birthday, general
    status = Column(String, default="pending")  # pending, sent, failed

    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    church = relationship("Church", backref="sms_history")
    sender = relationship("User", backref="sent_sms")
    recipient = relationship("Member", backref="received_sms")
