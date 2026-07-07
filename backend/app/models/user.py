from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID, INET
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
import enum
import uuid


class RiskTierEnum(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    username = Column(String(50), unique=True)
    avatar_url = Column(Text)
    age = Column(Integer)
    risk_tier = Column(String(50), default=RiskTierEnum.BEGINNER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime)
    preferences = Column(JSONB, default={})
    notification_settings = Column(JSONB, default={"email": True, "push": True, "weekly_digest": True})

    risk_profile = relationship("UserRiskProfile", back_populates="user", uselist=False)
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    module_progress = relationship("UserModuleProgress", back_populates="user")
    social_posts = relationship("SocialPost", back_populates="user")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserRiskProfile(BaseModel):
    __tablename__ = "user_risk_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    risk_tolerance_score = Column(Integer)
    knowledge_level = Column(Integer)
    investment_horizon = Column(String(20))
    income_stability = Column(String(20))
    loss_tolerance = Column(Integer)
    assessment_answers = Column(JSONB)

    user = relationship("User", back_populates="risk_profile")


class UserSession(BaseModel):
    __tablename__ = "user_session"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    refresh_token_hash = Column(String(255), nullable=False)
    device_info = Column(JSONB)
    ip_address = Column(String(45))
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")
