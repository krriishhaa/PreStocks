"""
Learning model — modules and user progress tracking.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class LearningModule(BaseModel):
    __tablename__ = "learning_module"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    tier = Column(String(50), nullable=False)  # 'beginner', 'intermediate', 'advanced'
    duration_minutes = Column(Integer, default=5)
    order_index = Column(Integer, default=0)
    content_url = Column(String(500), nullable=True)
    quiz_questions = Column(JSONB, nullable=True)

    user_progress = relationship("UserModuleProgress", back_populates="module")


class UserModuleProgress(BaseModel):
    __tablename__ = "user_module_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    module_id = Column(Integer, ForeignKey("learning_module.id", ondelete="CASCADE"))
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed
    progress_pct = Column(Integer, default=0)
    quiz_score = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="module_progress")
    module = relationship("LearningModule", back_populates="user_progress")
