from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    age: int = Field(..., ge=18, le=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RiskAssessmentRequest(BaseModel):
    question_1_answer: int
    question_2_answer: int
    question_3_answer: int
    question_4_answer: int
    question_5_answer: int


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    age: Optional[int]
    risk_tier: str

    class Config:
        from_attributes = True
