"""
Authentication Router — signup, login, refresh, password reset, sessions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.database.session import get_db
from app.schemas.user import (
    SignupRequest, LoginRequest, LoginResponse,
    RiskAssessmentRequest, UserResponse, TokenRefreshRequest, PasswordResetRequest
)
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, get_current_user_id, verify_refresh_token
from app.core.config import settings

router = APIRouter()


@router.post("/signup", response_model=dict, status_code=201)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(db, request)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
        )
        return {
            "message": "User created successfully",
            "user_id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "next_step": "risk_assessment",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=dict)
def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    user = UserService.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "tier": user.risk_tier},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    )

    UserService.record_login(db, user.id, ip=req.client.host if req.client else None)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_HOURS * 3600,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username,
            "risk_tier": user.risk_tier,
            "avatar_url": user.avatar_url,
        },
    }


@router.post("/refresh", response_model=dict)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    user_id = verify_refresh_token(payload.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = UserService.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "tier": user.risk_tier},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    )
    return {"access_token": access_token, "token_type": "bearer", "expires_in": settings.JWT_EXPIRATION_HOURS * 3600}


@router.post("/password-reset/request", response_model=dict)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    UserService.initiate_password_reset(db, payload.email)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/password-reset/confirm", response_model=dict)
def confirm_password_reset(token: str, new_password: str, db: Session = Depends(get_db)):
    success = UserService.reset_password(db, token, new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return {"message": "Password updated successfully"}


@router.post("/risk-assessment", response_model=dict)
def assess_risk(
    request: RiskAssessmentRequest,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    risk_profile = UserService.assess_risk_profile(db, current_user_id, request)
    user = UserService.get_user_by_id(db, current_user_id)
    return {
        "message": "Risk assessment completed",
        "risk_tier": user.risk_tier,
        "risk_tolerance_score": risk_profile.risk_tolerance_score,
        "knowledge_level": risk_profile.knowledge_level,
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    user = UserService.get_user_by_id(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/logout", response_model=dict)
def logout(current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    UserService.invalidate_sessions(db, current_user_id)
    return {"message": "Logged out successfully"}
