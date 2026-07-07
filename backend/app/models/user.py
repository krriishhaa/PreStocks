"""
User model — accounts, risk profiles, and sessions.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


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
    username = Column(String(50), unique=True, nullable=True)
    avatar_url = Column(Text, nullable=True)
    risk_tier = Column(String(50), default=RiskTierEnum.BEGINNER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    risk_profile = relationship("UserRiskProfile", back_populates="user", uselist=False)
    module_progress = relationship("UserModuleProgress", back_populates="user")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserRiskProfile(BaseModel):
    __tablename__ = "user_risk_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    risk_tolerance_score = Column(Integer, default=0)
    knowledge_level = Column(Integer, default=0)
    assessment_answers = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="risk_profile")


class UserSession(BaseModel):
    __tablename__ = "user_session"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    user = relationship("User", back_populates="sessions")
