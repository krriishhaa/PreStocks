"""
Learning Router — modules and progress tracking.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel as PydanticModel
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database.session import get_db
from app.core.security import get_current_user_id
from app.models.learning import LearningModule, UserModuleProgress

router = APIRouter()


class ProgressUpdate(PydanticModel):
    progress_pct: int = 0


class QuizSubmit(PydanticModel):
    answers: dict


@router.get("/modules")
def get_modules(
    tier: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    query = db.query(LearningModule)
    if tier:
        query = query.filter(LearningModule.tier == tier)
    modules = query.order_by(LearningModule.order_index).all()

    progress_map = {}
    progress_rows = db.query(UserModuleProgress).filter(UserModuleProgress.user_id == user_id).all()
    for p in progress_rows:
        progress_map[p.module_id] = p

    result = []
    for m in modules:
        p = progress_map.get(m.id)
        result.append({
            "id": m.id,
            "slug": m.slug,
            "title": m.title,
            "description": m.description,
            "tier": m.tier,
            "duration_minutes": m.duration_minutes,
            "order_index": m.order_index,
            "status": p.status if p else "not_started",
            "progress_pct": p.progress_pct if p else 0,
            "quiz_score": p.quiz_score if p else None,
            "started_at": p.started_at.isoformat() if p and p.started_at else None,
            "completed_at": p.completed_at.isoformat() if p and p.completed_at else None,
        })

    return result


@router.get("/modules/{module_id}")
def get_module(
    module_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.module_id == module_id,
    ).first()

    return {
        "id": module.id,
        "slug": module.slug,
        "title": module.title,
        "description": module.description,
        "tier": module.tier,
        "duration_minutes": module.duration_minutes,
        "content_url": module.content_url,
        "quiz_questions": module.quiz_questions,
        "status": progress.status if progress else "not_started",
        "progress_pct": progress.progress_pct if progress else 0,
        "quiz_score": progress.quiz_score if progress else None,
    }


@router.post("/modules/{module_id}/start")
def start_module(
    module_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.module_id == module_id,
    ).first()

    if not progress:
        progress = UserModuleProgress(
            user_id=user_id,
            module_id=module_id,
            status="in_progress",
            progress_pct=0,
            started_at=datetime.utcnow(),
        )
        db.add(progress)
    else:
        progress.status = "in_progress"
        if not progress.started_at:
            progress.started_at = datetime.utcnow()

    db.commit()
    return {"module_id": module_id, "status": "in_progress"}


@router.post("/modules/{module_id}/progress")
def update_progress(
    module_id: int,
    body: ProgressUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.module_id == module_id,
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="Start the module first")

    progress.progress_pct = min(body.progress_pct, 100)
    if progress.progress_pct == 100:
        progress.status = "completed"
        progress.completed_at = datetime.utcnow()

    db.commit()
    return {"module_id": module_id, "progress_pct": progress.progress_pct, "status": progress.status}


@router.post("/modules/{module_id}/complete")
def complete_module(
    module_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.module_id == module_id,
    ).first()

    if not progress:
        progress = UserModuleProgress(
            user_id=user_id,
            module_id=module_id,
            status="completed",
            progress_pct=100,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(progress)
    else:
        progress.status = "completed"
        progress.progress_pct = 100
        progress.completed_at = datetime.utcnow()

    db.commit()
    return {"module_id": module_id, "status": "completed", "progress_pct": 100}


@router.post("/modules/{module_id}/quiz")
def submit_quiz(
    module_id: int,
    body: QuizSubmit,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    questions = module.quiz_questions or []
    if not questions:
        raise HTTPException(status_code=400, detail="This module has no quiz")

    correct = 0
    total = len(questions)
    for q in questions:
        q_id = str(q.get("id", ""))
        correct_answer = q.get("correct_answer")
        user_answer = body.answers.get(q_id)
        if user_answer == correct_answer:
            correct += 1

    score = int((correct / total) * 100) if total > 0 else 0
    passed = score >= 70

    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.module_id == module_id,
    ).first()

    if progress:
        progress.quiz_score = score
        if passed and progress.status != "completed":
            progress.status = "completed"
            progress.progress_pct = 100
            progress.completed_at = datetime.utcnow()
    else:
        progress = UserModuleProgress(
            user_id=user_id,
            module_id=module_id,
            status="completed" if passed else "in_progress",
            progress_pct=100 if passed else 80,
            quiz_score=score,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if passed else None,
        )
        db.add(progress)

    db.commit()
    return {"score": score, "passed": passed, "correct": correct, "total": total}


@router.get("/progress")
def get_user_progress(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    total_modules = db.query(LearningModule).count()
    completed = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.status == "completed",
    ).count()
    in_progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.status == "in_progress",
    ).count()

    return {
        "total_modules": total_modules,
        "completed": completed,
        "in_progress": in_progress,
        "not_started": total_modules - completed - in_progress,
        "completion_pct": round((completed / total_modules * 100) if total_modules else 0, 1),
    }
