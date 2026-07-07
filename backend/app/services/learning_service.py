from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.learning import LearningModule, UserModuleProgress
from app.core.constants import QUIZ_PASS_THRESHOLD


class LearningService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_modules_with_progress(self, user_id: int, tier: Optional[str] = None) -> list[dict]:
        query = select(LearningModule)
        if tier:
            query = query.where(LearningModule.required_tier == tier)

        result = await self.db.execute(query)
        modules = result.scalars().all()

        progress_result = await self.db.execute(
            select(UserModuleProgress).where(UserModuleProgress.user_id == user_id)
        )
        progress_map = {p.module_id: p for p in progress_result.scalars().all()}

        output = []
        for m in modules:
            p = progress_map.get(m.id)
            progress_pct = 0
            mod_status = "not_started"
            if p:
                if p.completed_at:
                    mod_status = "completed"
                    progress_pct = 100
                elif p.started_at:
                    mod_status = "in_progress"
                    progress_pct = 50

            output.append({
                "id": m.id, "slug": str(m.id), "title": m.title,
                "description": m.description, "tier": m.required_tier,
                "duration_minutes": m.estimated_duration_minutes or 0,
                "order_index": 0,
                "status": mod_status,
                "progress_pct": progress_pct,
                "locked": False,
            })
        return output

    async def get_module_detail(self, user_id: int, module_id: str) -> dict:
        result = await self.db.execute(select(LearningModule).where(LearningModule.id == int(module_id)))
        module = result.scalar_one_or_none()
        if not module:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

        progress_result = await self.db.execute(
            select(UserModuleProgress).where(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id == module.id
            )
        )
        progress = progress_result.scalar_one_or_none()

        progress_pct = 0
        mod_status = "not_started"
        if progress:
            if progress.completed_at:
                mod_status = "completed"
                progress_pct = 100
            elif progress.started_at:
                mod_status = "in_progress"
                progress_pct = 50

        return {
            "id": module.id, "slug": str(module.id), "title": module.title,
            "description": module.description, "tier": module.required_tier,
            "duration_minutes": module.estimated_duration_minutes or 0,
            "order_index": 0,
            "status": mod_status,
            "progress_pct": progress_pct,
            "content_url": module.content_url,
            "quiz_questions": module.quiz_questions,
        }

    async def score_quiz(self, user_id: int, module_id: str, answers: dict[int, int]) -> dict:
        result = await self.db.execute(select(LearningModule).where(LearningModule.id == int(module_id)))
        module = result.scalar_one_or_none()
        if not module:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

        quiz = module.quiz_questions or []
        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quiz questions found")

        correct = 0
        total = len(quiz)
        for i, q in enumerate(quiz):
            correct_idx = q.get("correct_index", -1)
            if answers.get(i) == correct_idx:
                correct += 1

        score = (correct / total * 100) if total > 0 else 0
        passed = score >= (QUIZ_PASS_THRESHOLD * 100)

        # Update progress
        progress = await self._get_or_create_progress(user_id, module.id)
        progress.quiz_score = int(score)
        if passed:
            progress.completed_at = datetime.now(timezone.utc)
        await self.db.flush()

        return {"score": score, "passed": passed, "correct_count": correct, "total_count": total}

    async def mark_complete(self, user_id: int, module_id: str) -> dict:
        result = await self.db.execute(select(LearningModule).where(LearningModule.id == int(module_id)))
        module = result.scalar_one_or_none()
        if not module:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

        progress = await self._get_or_create_progress(user_id, module.id)
        progress.completed_at = datetime.now(timezone.utc)
        progress.quiz_score = progress.quiz_score or 100
        await self.db.flush()

        return {"module_id": module.id, "status": "completed", "progress_pct": 100}

    async def _get_or_create_progress(self, user_id: int, module_id: int) -> UserModuleProgress:
        result = await self.db.execute(
            select(UserModuleProgress).where(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id == module_id
            )
        )
        progress = result.scalar_one_or_none()
        if not progress:
            progress = UserModuleProgress(
                user_id=user_id, module_id=module_id,
                started_at=datetime.now(timezone.utc),
            )
            self.db.add(progress)
            await self.db.flush()
        return progress
