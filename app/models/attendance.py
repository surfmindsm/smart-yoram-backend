from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    church_id = Column(Integer, ForeignKey("churches.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)

    service_date = Column(Date, nullable=False)
    service_type = Column(
        String, nullable=False
    )  # sunday_morning, sunday_evening, wednesday, etc

    present = Column(Boolean, default=True)
    check_in_time = Column(DateTime(timezone=True))
    check_in_method = Column(String)  # qr, manual, online

    notes = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    church = relationship("Church", backref="attendances")
    member = relationship("Member", backref="attendances")
