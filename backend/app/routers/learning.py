from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.services.learning_service import LearningService
from app.core.security import get_current_user_id

router = APIRouter()


class ModuleResponse(BaseModel):
    id: int
    slug: str
    title: Optional[str] = None
    description: Optional[str] = None
    tier: Optional[str] = None
    duration_minutes: int = 0
    order_index: int = 0
    status: str = "not_started"
    progress_pct: int = 0
    locked: bool = False


class QuizSubmit(BaseModel):
    answers: dict[int, int]


class QuizResult(BaseModel):
    score: float
    passed: bool
    correct_count: int
    total_count: int


class ModuleCompleteResponse(BaseModel):
    module_id: int
    status: str
    progress_pct: int


@router.get("/modules", response_model=list[ModuleResponse])
async def get_modules(
    tier: Optional[str] = Query(default=None, pattern="^(beginner|intermediate|advanced)$"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = LearningService(db)
    return await service.get_modules_with_progress(user_id, tier)


@router.get("/modules/{module_id}")
async def get_module(
    module_id: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = LearningService(db)
    return await service.get_module_detail(user_id, module_id)


@router.post("/modules/{module_id}/quiz", response_model=QuizResult)
async def submit_quiz(
    module_id: str,
    data: QuizSubmit,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = LearningService(db)
    return await service.score_quiz(user_id, module_id, data.answers)


@router.post("/modules/{module_id}/complete", response_model=ModuleCompleteResponse)
async def complete_module(
    module_id: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = LearningService(db)
    return await service.mark_complete(user_id, module_id)
