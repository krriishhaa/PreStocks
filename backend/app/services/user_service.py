"""
User service — handles registration, authentication, risk assessment.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.user import User, UserRiskProfile, UserSession, RiskTierEnum
from app.models.portfolio import Portfolio
from app.schemas.user import SignupRequest, RiskAssessmentRequest
from app.core.security import hash_password, verify_password


class UserService:
    @staticmethod
    def create_user(db: Session, signup_data: SignupRequest) -> User:
        existing = db.query(User).filter(User.email == signup_data.email).first()
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=signup_data.email,
            password_hash=hash_password(signup_data.password),
            full_name=signup_data.full_name,
            risk_tier=RiskTierEnum.BEGINNER,
        )
        db.add(user)
        db.flush()

        # Auto-create a default portfolio with $10,000 paper cash
        portfolio = Portfolio(
            user_id=user.id,
            name="Main Portfolio",
            cash=10000.00,
            initial_capital=10000.00,
        )
        db.add(portfolio)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def record_login(db: Session, user_id: int, ip: str = None, user_agent: str = None):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login_at = datetime.utcnow()
            session = UserSession(user_id=user_id, ip_address=ip, user_agent=user_agent)
            db.add(session)
            db.commit()

    @staticmethod
    def invalidate_sessions(db: Session, user_id: int):
        db.query(UserSession).filter(UserSession.user_id == user_id).delete()
        db.commit()

    @staticmethod
    def initiate_password_reset(db: Session, email: str):
        # In production this would send an email; for now just a no-op that doesn't leak info
        pass

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        # Stub — would verify a reset token
        return False

    @staticmethod
    def assess_risk_profile(db: Session, user_id: int, assessment: RiskAssessmentRequest):
        total_score = sum(a.get("answer", 0) for a in assessment.answers)
        knowledge_level = int((total_score / (len(assessment.answers) * 3)) * 100)

        if knowledge_level < 40:
            tier = RiskTierEnum.BEGINNER
        elif knowledge_level < 70:
            tier = RiskTierEnum.INTERMEDIATE
        else:
            tier = RiskTierEnum.ADVANCED

        existing = db.query(UserRiskProfile).filter(UserRiskProfile.user_id == user_id).first()
        if existing:
            existing.risk_tolerance_score = knowledge_level
            existing.knowledge_level = knowledge_level
            existing.assessment_answers = assessment.answers
        else:
            profile = UserRiskProfile(
                user_id=user_id,
                risk_tolerance_score=knowledge_level,
                knowledge_level=knowledge_level,
                assessment_answers=assessment.answers,
            )
            db.add(profile)

        user = db.query(User).filter(User.id == user_id).first()
        user.risk_tier = tier.value

        db.commit()
        return db.query(UserRiskProfile).filter(UserRiskProfile.user_id == user_id).first()
