from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel
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
    age = Column(Integer)
    risk_tier = Column(String(50), default=RiskTierEnum.BEGINNER)

    # Relationships
    risk_profile = relationship("UserRiskProfile", back_populates="user", uselist=False)
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    module_progress = relationship("UserModuleProgress", back_populates="user")
    social_posts = relationship("SocialPost", back_populates="user")


class UserRiskProfile(BaseModel):
    __tablename__ = "user_risk_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    risk_tolerance_score = Column(Integer)  # 0-100
    knowledge_level = Column(Integer)  # 0-100

    # Relationships
    user = relationship("User", back_populates="risk_profile")
