from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Church(Base):
    __tablename__ = "churches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 단체명
    business_no = Column(String)  # 사업자등록번호
    rrn_encrypted = Column(String)  # 주민등록번호 (단체용, 암호화)
    address = Column(String)  # 소재지
    phone = Column(String)
    email = Column(String)
    pastor_name = Column(String)
    district_scheme = Column(String)  # 구역/교구 체계 명칭

    subscription_status = Column(String, default="trial")  # trial, active, expired
    subscription_end_date = Column(DateTime)
    subscription_plan = Column(
        String(50), default="basic"
    )  # basic, premium, enterprise
    member_limit = Column(Integer, default=100)

    # GPT API Configuration
    gpt_api_key = Column(Text)  # Encrypted
    gpt_model = Column(String(50), default="gpt-4o-mini")
    max_tokens = Column(Integer, default=4000)
    temperature = Column(Float, default=0.7)
    gpt_last_test = Column(DateTime)

    # AI Agent Configuration
    max_agents = Column(Integer, default=10)
    monthly_token_limit = Column(Integer, default=100000)
    current_month_tokens = Column(Integer, default=0)
    current_month_cost = Column(Float, default=0.0)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    worship_services = relationship("WorshipService", back_populates="church")
    worship_categories = relationship("WorshipServiceCategory", back_populates="church")
    notification_templates = relationship(
        "NotificationTemplate", back_populates="church"
    )
    push_notifications = relationship("PushNotification", back_populates="church")
    ai_agents = relationship("AIAgent", back_populates="church")
    chat_histories = relationship("ChatHistory", back_populates="church")
    database_config = relationship(
        "ChurchDatabaseConfig", back_populates="church", uselist=False
    )
    pastoral_care_requests = relationship(
        "PastoralCareRequest", back_populates="church"
    )
    prayer_requests = relationship("PrayerRequest", back_populates="church")
    prayer_participations = relationship("PrayerParticipation", back_populates="church")
