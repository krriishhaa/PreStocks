from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.session import get_db
from app.schemas.user import SignupRequest, LoginRequest, LoginResponse, RiskAssessmentRequest, UserResponse
from app.services.user_service import UserService
from app.core.security import create_access_token, get_current_user_id
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=dict)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Sign up a new user"""
    try:
        user = UserService.create_user(db, request)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        )

        return {
            "message": "User created successfully. Complete risk assessment next.",
            "user_id": user.id,
            "access_token": access_token,
            "next_step": "risk_assessment",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=dict)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = UserService.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "risk_tier": user.risk_tier,
        },
    }


@router.post("/risk-assessment", response_model=dict)
async def assess_risk(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Complete risk assessment after signup"""
    risk_profile = UserService.assess_risk_profile(db, current_user_id, request)

    # Get updated user
    user = UserService.get_user_by_id(db, current_user_id)

    return {
        "message": "Risk assessment completed",
        "risk_tier": user.risk_tier,
        "risk_tolerance_score": risk_profile.risk_tolerance_score,
        "knowledge_level": risk_profile.knowledge_level,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """Get current authenticated user"""
    user = UserService.get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
