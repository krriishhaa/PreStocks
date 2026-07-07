from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRiskProfile, RiskTierEnum
from app.schemas.user import SignupRequest, RiskAssessmentRequest
from app.core.security import hash_password, verify_password
from app.core.constants import RISK_TIERS


class UserService:
    @staticmethod
    def create_user(db: Session, signup_data: SignupRequest) -> User:
        """Create a new user"""
        try:
            user = User(
                email=signup_data.email,
                password_hash=hash_password(signup_data.password),
                full_name=signup_data.full_name,
                age=signup_data.age,
                risk_tier=RiskTierEnum.BEGINNER,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already registered")

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def assess_risk_profile(db: Session, user_id: int, assessment: RiskAssessmentRequest):
        """
        Calculate risk profile based on answers.
        Scoring: each question 0-3, total 0-15
        Map to 0-100 scale
        """
        # Sum answers (0-15 range)
        total_score = (
            assessment.question_1_answer +
            assessment.question_2_answer +
            assessment.question_3_answer +
            assessment.question_4_answer +
            assessment.question_5_answer
        )

        # Convert to 0-100 scale
        knowledge_level = int((total_score / 15) * 100)

        # Determine tier
        if knowledge_level < 40:
            tier = RiskTierEnum.BEGINNER
        elif knowledge_level < 70:
            tier = RiskTierEnum.INTERMEDIATE
        else:
            tier = RiskTierEnum.ADVANCED

        # Save risk profile
        risk_profile = UserRiskProfile(
            user_id=user_id,
            risk_tolerance_score=knowledge_level,
            knowledge_level=knowledge_level,
        )
        db.add(risk_profile)

        # Update user tier
        user = db.query(User).filter(User.id == user_id).first()
        user.risk_tier = tier

        db.commit()
        db.refresh(risk_profile)
        return risk_profile
