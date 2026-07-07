"""
User Schemas — request/response models for auth and user endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class SignupRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = None
    username: Optional[str] = None
    age: Optional[int] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: str


class RiskAssessmentRequest(BaseModel):
    answers: list = Field(..., min_length=1, max_length=10)


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    username: Optional[str]
    avatar_url: Optional[str]
    risk_tier: Optional[str]
    is_active: bool
    is_verified: bool
    preferences: Optional[dict]
    notification_settings: Optional[dict]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None
    notification_settings: Optional[dict] = None
